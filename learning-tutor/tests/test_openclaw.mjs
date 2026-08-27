import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import plugin from '../scripts/openclaw/index.mjs';

test('OpenClaw bridge: explicit opt-in, worker capture, authorized stop', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'learning bridge '));
  const home = path.join(root, 'private');
  const transcript = path.join(root, 'session.jsonl');
  fs.writeFileSync(transcript, '');
  let command, service;
  const python = process.env.LEARNING_TEST_PYTHON || 'python3';
  plugin.register({
    pluginConfig: { python, home },
    registerCommand(c) { command = c; }, registerService(s) { service = s; },
    logger: { info() {}, warn() {}, error() {} }
  });
  const ctx = { isAuthorizedSender: true, args: JSON.stringify({ action: 'start', session: 'fixture-session', key: 'optics/vergence', title: '辐辏角', transcript }) };
  try {
    assert.match(command.handler({ ...ctx, isAuthorizedSender: false }).text, /authorized/);
    const started = JSON.parse(command.handler(ctx).text);
    assert.equal(started.active, 1);
    fs.appendFileSync(transcript, JSON.stringify({ type: 'message', message: { role: 'user', content: [{ type: 'text', text: 'synthetic answer' }] } }) + '\n');
    service.start();
    const script = fileURLToPath(new URL('../scripts/learn.py', import.meta.url));
    let status;
    for (let i = 0; i < 30; i++) {
      await new Promise(resolve => setTimeout(resolve, 100));
      const result = spawnSync(python, [script, '--home', home, 'status'], { encoding: 'utf8' });
      assert.equal(result.status, 0, result.stderr);
      status = JSON.parse(result.stdout);
      if (status.pending >= 3 && status.worker.heartbeat) break;
    }
    assert.equal(status.pending, 3);
    assert.ok(status.worker.heartbeat);
    const stopped = command.handler({ ...ctx, args: JSON.stringify({ action: 'stop', session: 'fixture-session' }) });
    assert.equal(JSON.parse(stopped.text).action, 'stop');
    fs.appendFileSync(transcript, JSON.stringify({ type: 'message', message: { role: 'user', content: 'private after stop' } }) + '\n');
    const result = spawnSync(python, [script, '--home', home, 'capture', '--host', 'openclaw', '--host-session', 'fixture-session'], { encoding: 'utf8' });
    assert.equal(JSON.parse(result.stdout).state, 'not recording');
  } finally {
    service.stop();
    await new Promise(resolve => setTimeout(resolve, 300));
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('OpenClaw bridge requires explicit local configuration', () => {
  assert.throws(() => plugin.register({ pluginConfig: {} }), /requires explicit/);
});
