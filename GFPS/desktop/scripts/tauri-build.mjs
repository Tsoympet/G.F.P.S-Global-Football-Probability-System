import { spawnSync } from 'child_process';

const args = process.argv.slice(2);

// Handle accidental extra "build" argument (e.g. `npm run tauri:build build`)
if (args[0] === 'build') {
  args.shift();
}

const npx = process.platform === 'win32' ? 'npx.cmd' : 'npx';
const result = spawnSync(npx, ['tauri', 'build', ...args], { stdio: 'inherit' });

if (result.error) {
  console.error(result.error);
  process.exit(1);
}

process.exit(result.status ?? 0);
