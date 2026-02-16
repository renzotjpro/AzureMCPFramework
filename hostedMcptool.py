"""
HostedMCPTool - Runnable Example with Microsoft Agent Framework
================================================================

This file contains REAL code that you can run with Azure AI Foundry.

SETUP:
1. Install packages:
   pip install agent-framework agent-framework-azure-ai azure-identity --pre

2. Login to Azure:
   az login

3. Set environment variables (or create .env file):
   AZURE_AI_PROJECT_ENDPOINT=https://<your-project>.services.ai.azure.com/api/projects/<id>
   AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini

4. Run:
   python hosted_mcp_real_example.py
"""
"""
Hosted MCP Tool Example - CORRECTED
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv(override=True)
# Configuration - get from environment with defaults
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")



async def example_1_basic_hosted_mcp():
    """
    Agent searches Microsoft Learn documentation.
    """
    # UPDATED IMPORTS - Use MCPStreamableHTTPTool instead
    from agent_framework import Agent, MCPStreamableHTTPTool
    from agent_framework.azure import AzureAIAgentClient
    from azure.identity.aio import AzureCliCredential

    print("="*60)
    
    async with(
        AzureCliCredential() as credential,
        # Use MCPStreamableHTTPTool as context manager
        MCPStreamableHTTPTool(
            name="microsoft_learn",
            description="Search Microsoft Learn documentation for Azure",
            url="https://learn.microsoft.com/api/mcp",
            # approval_mode parameter may vary by version
        ) as mcp_tool,
        Agent(
            client=AzureAIAgentClient(credential=credential, project_endpoint=PROJECT_ENDPOINT, model_deployment_name=MODEL_DEPLOYMENT_NAME),
            name="DocAssistant",
            instructions="""
            You are a Microsoft documentation assistant.
            Use the Microsoft Learn search tool to find accurate answers.
            Always provide the source URL when answering.
            If you can't find relevant information, say so clearly.
            """,
            tools=[mcp_tool]  # Pass the tool object here
        ) as agent,
    ):
        questions = [
            "How do I create an Azure Storage account using Azure CLI?",
            "What is the difference between Azure AD and Microsoft Entra ID?",
        ]

        for question in questions:
            print(f"\nUser: {question}")
            result = await agent.run(question)
            print(f"\nAgent: {result.text[:500]}")    

async def example_2_alternative_pattern():
    """
    Create MCP tool outside the agent.
    This pattern is useful when you need to :
    - Reuse the samae MCP connection for multiple agents
    - Have more control over the tool lifecycle
    """
    from agent_framework import Agent, MCPStreamableHTTPTool
    from agent_framework.azure import AzureAIAgentClient
    from azure.identity.aio import AzureCliCredential

    print("Example 2: Alternative Pattern")
    print("=" * 60)

    async with AzureCliCredential() as credential:
        client = AzureAIAgentClient(
            credential = credential,
            project_endpoint = PROJECT_ENDPOINT,
            model_deployment_name = MODEL_DEPLOYMENT_NAME
        )
        #Create MCP tool with explicit lifecycle management
        async with MCPStreamableHTTPTool(
            name = "microsoft_learn",
            url ="https://learn.microsoft.com/api/mcp",
        ) as mcp_tool:

        #create agent using the tool
            agent = Agent(
                client = client,
                name = "DocBot",
                instructions ="You help with Microsoft documentation questions",
                tools = [mcp_tool],
            )

        questions = [
            "How do I create an Azure Storage account using Azure CLI?",
            "What is the difference between Azure AD and Microsoft Entra ID?",
        ]

        for question in questions:
            print(f"\nUser: {question}")
            result = await agent.run(question)
            print(f"\nAgent: {result.text[:500]}")

async def example_3_hosted_mcp_tool():
    """
    Hosted MCP Tool Example: content from Microsoft Learn
    """
    from agent_framework import Agent, MCPStreamableHTTPTool
    from agent_framework.azure import AzureAIAgentClient
    from azure.identity.aio import AzureCliCredential

    async with (
        AzureCliCredential() as credential,
        MCPStreamableHTTPTool(
            name = "microsoft_learn",
            description = "Search Microsoft learn documentation",
            url = "https://learn.microsoft.com/api/mcp",
            approval_mode = "never_require"
        ) as mcp_tool,
        Agent(
            client = AzureAIAgentClient(
                credential = credential,
                project_endpoint = PROJECT_ENDPOINT,
                model_deployment_name = MODEL_DEPLOYMENT_NAME
            ),
            name = "ManageDocAssistant",
            instructions = """
            You are a documentation assistant with access to Microsoft Learn.
            Search for accurate information and cite your sources.
            """,
            tools = [mcp_tool]
        ) as agent,
    ):
        result = await agent.run("What is Azure Kubernetes Service?")
        response = result.text
        if len(response) > 500:
            response = response[:500] + "..."
        print(f"\nAgent: {response}")

async def main():
    if not os.getenv("AZURE_AI_PROJECT_ENDPOINT"):
        print("Azure AI Foundry not configured!")
        return

    try:
        #print (os.getenv("AZURE_AI_PROJECT_ENDPOINT"))
        #print (os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME"))
        #await example_1_basic_hosted_mcp()
        #await example_2_alternative_pattern()
        await example_3_hosted_mcp_tool()
    except Exception as e:
        print(f"Example failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())