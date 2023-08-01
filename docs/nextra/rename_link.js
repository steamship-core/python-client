const readline = require("node:readline");

async function main() {
  const rl = readline.createInterface({
    input: process.stdin,
  });

  for await (const line of rl) {
    // process a line at a time
    process.stdout.write(`${line.replace('/../../../steamship/apps/python-docs/pages', '')}\n`);
  }
}

main();