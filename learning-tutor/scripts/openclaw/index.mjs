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
    let worker;
    function call(args) {
      const result = spawnSync(cfg.python, [...base, ...args], { encoding: 'utf8', timeout: 15000, maxBuffer: 2 * 1024 * 1024, windowsHide: true });
      if (result.error || result.status !== 0) throw new Error('Learning capture command failed; inspect local worker diagnostics.');
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
    api.registerService({
      id: 'learning-tutor-sync',
      start() {
        worker = spawn(cfg.python, [...base, 'worker'], { stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true });
        worker.stdout.on('data', data => api.logger.info(`learning-tutor: ${data.toString().trim()}`));
        worker.stderr.on('data', data => api.logger.warn(`learning-tutor: ${data.toString().trim()}`));
        worker.on('error', () => api.logger.error('learning-tutor worker failed to start; recording is degraded'));
        worker.on('exit', () => api.logger.warn('learning-tutor worker stopped; check capture status'));
      },
      stop() { worker?.kill(); worker = undefined; }
    });
    // Worker tails only explicitly bound files. No raw agent_end snapshots or unrelated sessions.
  }
};
