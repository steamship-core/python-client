const readline = require("node:readline");

async function main() {
  const rl = readline.createInterface({
    input: process.stdin,
  });

  for await (const line of rl) {
    // replace all instances of "/../../../steamship/apps/python-docs/pages" with ""
    // process a line at a time
    process.stdout.write(`${line.replaceAll('/../../../steamship/apps/python-docs/pages', '')}\n`);
  }
}

main();