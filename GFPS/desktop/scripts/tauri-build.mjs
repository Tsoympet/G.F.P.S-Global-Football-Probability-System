import { spawnSync } from 'child_process';

const args = process.argv.slice(2);

// Handle accidental extra "build" argument (e.g. `npm run tauri:build build`)
if (args[0] === 'build') {
  args.shift();
}

const result = spawnSync('npx', ['tauri', 'build', ...args], { stdio: 'inherit' });
process.exit(result.status ?? 0);
