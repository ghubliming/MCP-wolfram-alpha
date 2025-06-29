import base64
import asyncio
from mcp.server.models import InitializationOptions
from mcp.server.lowlevel import NotificationOptions, Server
import mcp.types as types
import mcp.server.stdio
from .wolfram_client import client
import httpx

# Create MCP server instance
server = Server("MCP-wolfram-alpha")


@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompts.
    """
    return [
        types.Prompt(
            name="wa",
            description="""
🧮 **ASK WOLFRAM ALPHA**

Generate a smart query for Wolfram Alpha's computational intelligence.

This prompt helps you:
• Frame questions for mathematical computations
• Get step-by-step solutions and explanations  
• Access scientific data and analysis
• Perform unit conversions and calculations
• Research factual information with citations

Perfect for: Students, researchers, analysts, anyone needing reliable computational answers

**Examples:**
- "What is the integral of sin(x) dx?"
- "Compare GDP of USA vs China in 2023"
- "How many calories in 100g of apple?"
- "Convert 25°C to Fahrenheit"
            """.strip(),
            arguments=[
                types.PromptArgument(
                    name="query",
                    description="Your question or calculation for Wolfram Alpha (e.g., 'solve x^2 - 4 = 0', 'population of Tokyo', 'derivative of ln(x)')",
                    required=True,
                )
            ],
        )
    ]


@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """
    Generate a prompt by combining arguments with server state.
    """
    if name != "wa":
        raise ValueError(f"Unknown prompt: {name}")

    if not arguments or "query" not in arguments:
        raise ValueError("Missing required 'query' argument for Wolfram Alpha prompt")

    query = arguments["query"].strip()
    if not query:
        raise ValueError("Query cannot be empty")

    return types.GetPromptResult(
        description="Ask Wolfram Alpha a computational question",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"""🧮 Please use Wolfram Alpha to answer the following question:

**Query:** {query}

Use the query-wolfram-alpha tool to get computational intelligence, mathematical solutions, scientific data, or factual information. Wolfram Alpha provides step-by-step solutions, graphs, and reliable data from authoritative sources.

After getting the results, please:
1. Summarize the key findings clearly
2. Explain any mathematical steps if applicable  
3. Provide context or interpretation when helpful
4. Mention if additional clarification might be needed""",
                ),
            )
        ],
    )


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="query-wolfram-alpha",
            description="""
🧮 WOLFRAM ALPHA COMPUTATIONAL INTELLIGENCE

Query Wolfram Alpha's computational knowledge engine for:
• Mathematical calculations and equations
• Scientific data and computations  
• Statistical analysis and data processing
• Unit conversions and measurements
• Factual queries and knowledge lookup
• Step-by-step solutions and explanations
• Graphical plots and visualizations

Perfect for: Math homework, research, data analysis, quick facts

Examples:
- "What is the derivative of x^2 + 3x?"
- "Population of Japan in 2023"
- "Convert 100 meters to feet" 
- "Plot sin(x) from 0 to 2π"
- "Solve 2x + 5 = 15"
            """.strip(),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Your question or calculation for Wolfram Alpha (e.g., 'What is 2+2?', 'derivative of x^2', 'population of France')",
                        "minLength": 1,
                        "maxLength": 500
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    if name != "query-wolfram-alpha":
        raise ValueError(f"Unknown tool: {name}")
        
    if not arguments:
        raise ValueError("Missing arguments for Wolfram Alpha query")

    query = arguments.get("query")
    if not query:
        raise ValueError("Missing 'query' parameter for Wolfram Alpha tool")
        
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be a non-empty string")
        
    query = query.strip()
    
    try:
        # Query Wolfram Alpha
        response = await asyncio.to_thread(client.query, query)
        
        if not response.pods:
            return [types.TextContent(
                type="text",
                text=f"🤔 No results found for '{query}'. Try rephrasing your question or being more specific."
            )]
        
        results: list[types.TextContent | types.ImageContent | types.EmbeddedResource] = []
        
        # Add a header with the query
        results.append(types.TextContent(
            type="text", 
            text=f"🧮 **Wolfram Alpha Results for:** {query}\n" + "="*50
        ))
        
        # Process response pods
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            for pod_idx, pod in enumerate(response.pods):
                pod_title = getattr(pod, 'title', f'Result {pod_idx + 1}')
                
                # Add pod title as a section header
                if pod_title and pod_title.strip():
                    results.append(types.TextContent(
                        type="text",
                        text=f"\n📊 **{pod_title}**"
                    ))
                
                for subpod_idx, subpod in enumerate(pod.subpods):
                    # Handle text content
                    if subpod.get("plaintext"):
                        text_content = subpod.plaintext.strip()
                        if text_content:
                            results.append(types.TextContent(
                                type="text",
                                text=f"• {text_content}"
                            ))
                    
                    # Handle image content  
                    if subpod.get("img"):
                        img_url = subpod.img.get("@src")
                        if img_url:
                            try:
                                img_response = await http_client.get(img_url)
                                if img_response.status_code == 200:
                                    img_base64 = base64.b64encode(img_response.content).decode('utf-8')
                                    
                                    # Determine image type from URL or content-type
                                    content_type = img_response.headers.get('content-type', 'image/png')
                                    if 'gif' in content_type:
                                        mime_type = "image/gif"
                                    elif 'jpeg' in content_type or 'jpg' in content_type:
                                        mime_type = "image/jpeg"
                                    else:
                                        mime_type = "image/png"
                                    
                                    results.append(types.ImageContent(
                                        type="image",
                                        data=img_base64,
                                        mimeType=mime_type
                                    ))
                                else:
                                    results.append(types.TextContent(
                                        type="text",
                                        text=f"📷 [Image unavailable - HTTP {img_response.status_code}]"
                                    ))
                            except Exception as img_error:
                                results.append(types.TextContent(
                                    type="text",
                                    text=f"📷 [Image could not be loaded: {str(img_error)}]"
                                ))
        
        # Add footer with helpful info
        results.append(types.TextContent(
            type="text",
            text=f"\n" + "="*50 + f"\n✅ **Analysis complete** - Found {len(response.pods)} result sections\n💡 **Tip:** Try more specific queries for better results"
        ))
        
        return results
        
    except Exception as e:
        # Provide more detailed error information
        error_msg = f"Failed to query Wolfram Alpha: {str(e)}"
        if "Content-Type" in str(e):
            error_msg += "\n💡 This may indicate an API key issue or service unavailability."
        elif "timeout" in str(e).lower():
            error_msg += "\n💡 The query timed out. Try a simpler question."
        elif "api" in str(e).lower():
            error_msg += "\n💡 There may be an issue with the Wolfram Alpha API service."
            
        return [types.TextContent(
            type="text", 
            text=f"❌ **Error:** {error_msg}\n\n🔧 **Troubleshooting:**\n• Check your internet connection\n• Try a simpler query\n• Verify API key is valid\n• Wait a moment and try again"
        )]


async def main():
    """Main entry point for the MCP server."""
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="MCP-wolfram-alpha",
                server_version="0.2.1",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
