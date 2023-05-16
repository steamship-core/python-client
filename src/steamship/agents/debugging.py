from steamship import Block
from steamship.agents.agent_context import AgentContext
from steamship.agents.agents import Tool


def tool_repl(tool: Tool, context: AgentContext):
    """Run a development repl in the CLI for testing the tool."""
    try:
        pass
    except ImportError:
        print("Error: Please run `pip install inquirer` to run this REPL.")
        exit(-1)

    try:
        from termcolor import colored
    except ImportError:
        print("Error: Please run `pip install termcolor` to run this REPL.")
        exit(-1)

    print(f"Starting Tool {tool.name}...")
    print(
        "If you make code changes, you will need to restart this client. Press CTRL+C to exit at any time.\n"
    )

    while True:
        input_text = input(colored("Input: ", "blue"))
        input_block = Block(text=input_text)
        output_blocks = tool.run([input_block], context=context)

        for block in output_blocks:
            if block.is_text():
                print(block.text)
            elif block.url:
                print(block.url)
            elif block.content_url:
                print(block.content_url)
            else:
                print(f"Binary object of {len(block.raw())} bytes")
