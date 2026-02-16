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
project_endpoint= os.getenv("AZURE_AI_PROJECT_ENDPOINT")
model_deployment_name= os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
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
            client=AzureAIAgentClient(credential=credential, project_endpoint=project_endpoint, model_deployment_name=model_deployment_name),
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

async def main():
    if not os.getenv("AZURE_AI_PROJECT_ENDPOINT"):
        print("Azure AI Foundry not configured!")
        return

    try:
        #print (os.getenv("AZURE_AI_PROJECT_ENDPOINT"))
        #print (os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME"))
        await example_1_basic_hosted_mcp()
    except Exception as e:
        print(f"Example failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())