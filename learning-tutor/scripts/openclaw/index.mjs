// Targets the inspected 2026.2.26 plugin interfaces. Real Gateway coverage remains to be verified.
import { spawn, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

export default {
  id: 'learning-tutor',
  name: 'Learning Tutor Capture',
  register(api) {
    const cfg = api.pluginConfig ?? {};
    if (!cfg.python || !cfg.home) throw new Error('learning-tutor requires explicit python and private home paths');
    const script = fileURLToPath(new URL('../learn.py', import.meta.url));
    const base = [script, '--home', cfg.home, '--profile', cfg.profile ?? 'personal'];
    function call(args) {
      const result = spawnSync(cfg.python, [...base, ...args], { encoding: 'utf8', timeout: 15000, maxBuffer: 2 * 1024 * 1024, windowsHide: true });
      if (result.error || result.status !== 0) throw new Error('Learning capture command failed; inspect local capture diagnostics.');
      return JSON.parse(result.stdout);
    }
    // JSON arguments make session identity explicit. No channel-to-session guesswork.
    api.registerCommand({
      name: 'learn', description: 'Start/stop/status for an explicitly identified learning session',
      acceptsArgs: true, requireAuth: true,
      handler(ctx) {
        if (!ctx.isAuthorizedSender) return { text: 'Learning command requires an authorized sender.' };
        try {
          const input = JSON.parse(ctx.args || '{"action":"status"}');
          let result;
          if (input.action === 'start') {
            for (const k of ['session', 'key', 'title', 'transcript']) {
              if (typeof input[k] !== 'string' || !input[k].trim()) throw new Error('Missing start fields');
            }
            if (!path.isAbsolute(input.transcript)) throw new Error('Transcript must be absolute');
            result = call(['start', input.key, input.title, '--host', 'openclaw', '--host-session', input.session, '--transcript', input.transcript]);
          } else if (input.action === 'stop' && typeof input.session === 'string') {
            result = call(['stop', '--host', 'openclaw', '--host-session', input.session]);
          } else if (input.action === 'status') {
            const status = call(['status']);
            result = { pending: status.pending, last_sync: status.last_sync, sync_error: status.sync_error, recording: status.recording };
          } else throw new Error('Unknown action');
          return { text: JSON.stringify(result) };
        } catch {
          return { text: 'Learning operation failed. Use /learn with JSON action, and for start include session, key, title, absolute transcript. Check local storage and session identity; no completion is claimed.' };
        }
      }
    });
    // Native event adapters tail only the explicitly bound source; event.messages isn't imported.
    function observe(event, ctx, captureOnly = false, completed = false) {
      const session = event.sessionId ?? ctx?.sessionId;
      if (typeof session !== 'string' || !session) {
        api.logger.warn('learning-tutor: no verified session id; hook skipped');
        return;
      }
      let lastText;
      if (completed && event.success === true && Array.isArray(event.messages)) {
        const last = [...event.messages].reverse().find(m => m?.role === 'assistant');
        if (typeof last?.content === 'string') lastText = last.content;
        else if (Array.isArray(last?.content)) {
          lastText = last.content.filter(b => b.type === 'text' && typeof b.text === 'string').map(b => b.text).join('\n');
        }
      }
      try {
        const captureArgs = ['tick', '--host', 'openclaw', '--host-session', session, '--capture-only'];
        if (completed && event.success === true && lastText) captureArgs.push('--complete', '--last-assistant-message', lastText);
        call(captureArgs);
      } catch {
        api.logger.warn('learning-tutor: local capture failed; inspect status before claiming completeness');
        return;
      }
      if (captureOnly) return;
      const args = [...base, 'tick', '--host', 'openclaw', '--host-session', session];
      return new Promise(resolve => {
        const task = spawn(cfg.python, args, { stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true });
        let output = '';
        task.stdout.on('data', data => { if (output.length < 2 * 1024 * 1024) output += data.toString(); });
        task.stderr.on('data', () => {});
        task.on('error', () => { api.logger.warn('learning-tutor: delivery task failed to launch'); resolve(); });
        task.on('close', () => {
          try {
            const result = JSON.parse(output);
            if (result.upload?.notice) api.logger.warn(result.upload.notice);
          } catch { api.logger.warn('learning-tutor: delivery task interrupted; pending data retained'); }
          resolve();
        });
      });
    }
    api.on('session_start', (event, ctx) => observe(event, ctx));
    api.on('before_agent_run', (event, ctx) => observe(event, ctx));
    api.on('agent_end', (event, ctx) => observe(event, ctx, false, true));
    api.on('session_end', (event, ctx) => observe(event, ctx, true));
  }
};
