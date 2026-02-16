"""
MCP Client - Connect to Local Banking MCP Server
=================================================

This demonstrates how to use Microsoft Agent Framework to connect
to a LOCAL MCP server using MCPStdioTool.

ARCHITECTURE:
┌─────────────────────────────────────────────────────────────────┐
│                        Your Application                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐      MCPStdioTool       ┌─────────────────┐  │
│   │   Agent     │ ◄──── stdin/stdout ───► │  local_mcp_     │  │
│   │  (GPT-4)    │                         │  server.py      │  │
│   └─────────────┘                         └─────────────────┘  │
│         │                                         │             │
│         │                                         │             │
│    Uses tools:                              Provides tools:     │
│    - get_balance                            - get_balance       │
│    - get_transactions                       - get_transactions  │
│    - etc.                                   - etc.              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

SETUP:
1. pip install agent-framework agent-framework-azure-ai azure-identity fastmcp --pre

2. Set environment variables:
   export AZURE_AI_PROJECT_ENDPOINT="..."
   export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o-mini"
   # OR
   export OPENAI_API_KEY="sk-..."

3. Run:
   python client_local_mcp.py
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)


async def example_1_with_azure():
    """
    Example 1: Connect to local MCP server using Azure AI Foundry.
    """
    from agent_framework import Agent, MCPStdioTool
    from agent_framework.azure import AzureAIAgentClient
    from azure.identity.aio import AzureCliCredential

    print("=" * 60)
    print("Example 1: Local MCP Server with Azure AI Foundry")
    print("=" * 60)

    # Path to the local MCP server
    server_path = Path(__file__).parent / "local_mcp_server.py"
    
    if not server_path.exists():
        print(f"❌ Server not found: {server_path}")
        return

    async with (
        AzureCliCredential() as credential,
        
        # MCPStdioTool launches the server as a subprocess
        MCPStdioTool(
            name="banking_tools",
            command=sys.executable,  # Python interpreter
            args=[str(server_path)],  # The server script
            # Optional: Pass environment variables to the server
            env={"PYTHONUNBUFFERED": "1"},
        ) as mcp_server,
        
        Agent(
            client=AzureAIAgentClient(
                credential=credential,
                project_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
                model_deployment_name=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")
            ),
            name="BankingAssistant",
            instructions="""
            You are a helpful banking assistant.
            Use the available tools to help users with their banking needs.
            Always be clear and provide specific numbers when discussing finances.
            """,
            tools=[mcp_server]  # Pass the MCP server as tools
        ) as agent,
    ):
        # Test questions that will use the MCP tools
        questions = [
            "What's my account balance?",
            "Show me my recent transactions",
            "How much did I spend on entertainment?",
            "If I take a $200,000 mortgage at 6.5% for 30 years, what's my monthly payment?",
        ]

        for question in questions:
            print(f"\n{'─' * 50}")
            print(f"👤 User: {question}")
            print(f"{'─' * 50}")
            
            result = await agent.run(question)
            print(f"\n🤖 Agent: {result.text}")

    print("\n✅ Example 1 completed!")


async def example_2_with_openai():
    """
    Example 2: Connect to local MCP server using OpenAI directly.
    
    This doesn't require Azure - just an OpenAI API key.
    """
    from agent_framework import ChatAgent, MCPStdioTool
    from agent_framework.openai import OpenAIChatClient

    print("\n" + "=" * 60)
    print("Example 2: Local MCP Server with OpenAI")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEY not set, skipping this example")
        return

    server_path = Path(__file__).parent / "local_mcp_server.py"

    async with MCPStdioTool(
        name="banking_tools",
        command=sys.executable,
        args=[str(server_path)],
    ) as mcp_server:
        
        # Create OpenAI chat client
        client = OpenAIChatClient(
            model_id="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        
        # Create agent with the MCP tools
        agent = ChatAgent(
            chat_client=client,
            name="BankingBot",
            instructions="You are a helpful banking assistant. Use the tools to answer questions.",
            tools=mcp_server,  # Can pass single tool or list
        )
        
        # Test
        result = await agent.run("What's my balance and show me my cards?")
        print(f"\n🤖 Agent: {result.text}")

    print("\n✅ Example 2 completed!")


async def example_3_multiple_mcp_servers():
    """
    Example 3: Connect to MULTIPLE local MCP servers.
    
    This shows how you can combine tools from different servers.
    """
    from agent_framework import ChatAgent, MCPStdioTool
    from agent_framework.openai import OpenAIChatClient

    print("\n" + "=" * 60)
    print("Example 3: Multiple MCP Servers")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEY not set, skipping this example")
        return

    server_path = Path(__file__).parent / "local_mcp_server.py"

    # You can connect to multiple MCP servers
    async with (
        MCPStdioTool(
            name="banking",
            command=sys.executable,
            args=[str(server_path)],
        ) as banking_mcp,
        
        # You could add more servers here:
        # MCPStdioTool(
        #     name="calculator",
        #     command="uvx",
        #     args=["mcp-server-calculator"],
        # ) as calc_mcp,
    ):
        client = OpenAIChatClient(
            model_id="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        
        # Combine tools from multiple servers
        # all_tools = [*banking_mcp.functions, *calc_mcp.functions]
        all_tools = banking_mcp  # Just banking for now
        
        agent = ChatAgent(
            chat_client=client,
            name="MultiToolAgent",
            instructions="You have access to banking tools. Help the user.",
            tools=all_tools,
        )
        
        result = await agent.run("Give me a spending summary")
        print(f"\n🤖 Agent: {result.text}")

    print("\n✅ Example 3 completed!")


async def example_4_list_tools():
    """
    Example 4: Just list the tools available from the MCP server.
    
    Useful for debugging and understanding what's available.
    """
    from agent_framework import MCPStdioTool

    print("\n" + "=" * 60)
    print("Example 4: List Available Tools")
    print("=" * 60)

    server_path = Path(__file__).parent / "local_mcp_server.py"

    async with MCPStdioTool(
        name="banking_tools",
        command=sys.executable,
        args=[str(server_path)],
    ) as mcp_server:
        
        print("\n📋 Tools available from the MCP server:\n")
        
        # The MCP server exposes tools as functions
        for func in mcp_server.functions:
            print(f"  🔧 {func.name}")
            if func.description:
                # Print first line of description
                desc = func.description.split('\n')[0].strip()
                print(f"     {desc}")
            print()

    print("✅ Example 4 completed!")


async def main():
    """Main entry point."""
    
    print("\n" + "🚀" * 20)
    print("   Local MCP Server Examples")
    print("🚀" * 20)
    
    # Check configuration
    has_azure = bool(os.getenv("AZURE_AI_PROJECT_ENDPOINT"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    
    print(f"\n📋 Configuration:")
    print(f"   Azure AI Foundry: {'✅ Configured' if has_azure else '❌ Not set'}")
    print(f"   OpenAI API Key:   {'✅ Configured' if has_openai else '❌ Not set'}")
    
    if not has_azure and not has_openai:
        print("""
❌ No API credentials found!

Set one of:
  export AZURE_AI_PROJECT_ENDPOINT="..."
  export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o-mini"

Or:
  export OPENAI_API_KEY="sk-..."
        """)
        
        # Still run example 4 (no API needed)
        print("Running Example 4 only (no API required)...")
        try:
            await example_4_list_tools()
        except Exception as e:
            print(f"❌ Example 4 failed: {e}")
        return
    
    # Run examples based on available credentials
    if has_azure:
        try:
            await example_1_with_azure()
        except Exception as e:
            print(f"\n❌ Example 1 failed: {e}")
            import traceback
            traceback.print_exc()
    
    if has_openai:
        try:
            await example_2_with_openai()
        except Exception as e:
            print(f"\n❌ Example 2 failed: {e}")
    
    # Always run tool listing (no API needed)
    try:
        await example_4_list_tools()
    except Exception as e:
        print(f"\n❌ Example 4 failed: {e}")
    
    print("\n👋 Done!")


if __name__ == "__main__":
    asyncio.run(main())