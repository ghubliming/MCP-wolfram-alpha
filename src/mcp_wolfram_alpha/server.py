import base64
import asyncio
import traceback
from mcp.server.models import InitializationOptions
from mcp.server.lowlevel import NotificationOptions, Server
import mcp.types as types
import mcp.server.stdio
from .wolfram_client import client
import httpx
from pydantic import AnyUrl
import logging

# Set up logging
logger = logging.getLogger(__name__)

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
    Handle MCP tool calls with comprehensive error handling and user guidance.
    
    This function implements robust error handling patterns to ensure the user
    always receives meaningful, actionable feedback following the best practices
    demonstrated in the sample MCP approach.
    
    Args:
        name (str): Name of the tool being called
        arguments (dict | None): Tool arguments provided by the client
        
    Returns:
        list[types.TextContent | types.ImageContent | types.EmbeddedResource]: 
            Formatted response content with results or detailed error messages
    """
    logger.info(f"🛠️ Tool called: {name} with arguments: {arguments}")
    
    # Validate tool name
    if name != "query-wolfram-alpha":
        error_msg = f"""
❌ UNKNOWN TOOL REQUEST

Tool '{name}' is not recognized. Available tools:
• query-wolfram-alpha - Query Wolfram Alpha for mathematical, scientific, and factual computations

Please check the tool name and try again.
        """.strip()
        logger.warning(f"Unknown tool requested: {name}")
        return [types.TextContent(type="text", text=error_msg)]
    
    # Validate arguments structure
    if not arguments:
        error_msg = """
❌ MISSING ARGUMENTS

No arguments provided for the Wolfram Alpha query. Please provide a 'query' parameter.

Example usage:
• query: "What is the square root of 144?"
• query: "Population of Tokyo"
• query: "Derivative of x^2 + 3x + 1"
        """.strip()
        logger.error("No arguments provided to query-wolfram-alpha tool")
        return [types.TextContent(type="text", text=error_msg)]
    
    # Extract and validate query parameter
    query = arguments.get("query", "").strip() if arguments.get("query") else ""
    if not query:
        error_msg = """
❌ INVALID QUERY

No query text provided. Please specify a 'query' parameter with your question.

Example queries:
• "What is 2+2?"
• "Population of Paris"
• "Solve x^2 - 5x + 6 = 0"
• "Convert 100 fahrenheit to celsius"
        """.strip()
        logger.error("Empty query parameter provided")
        return [types.TextContent(type="text", text=error_msg)]
    
    # Input validation for query length and content
    if len(query) < 2:
        return [types.TextContent(
            type="text",
            text="❌ ERROR: Query too short. Please provide a meaningful question (at least 2 characters)."
        )]
        
    if len(query) > 1000:
        return [types.TextContent(
            type="text", 
            text="❌ ERROR: Query too long. Please limit your question to 1000 characters or less."
        )]
    
    # Verify API key is available
    import os
    api_key = os.getenv('WOLFRAM_API_KEY')
    if not api_key:
        error_msg = """
❌ WOLFRAM ALPHA SERVICE UNAVAILABLE

The Wolfram Alpha service is not properly initialized. This usually means:
• WOLFRAM_API_KEY environment variable is missing or invalid
• Service startup failed during initialization

🔧 SOLUTION STEPS:
1. Set your Wolfram Alpha API key in environment variables
2. Get a free API key at: https://products.wolframalpha.com/api
3. Restart the MCP server after setting the key
4. Verify the key is correctly set in your environment

Example: WOLFRAM_API_KEY=YOUR_API_KEY_HERE
        """.strip()
        logger.error("Wolfram Alpha API key not set when tool called")
        return [types.TextContent(type="text", text=error_msg)]
    
    # Verify Wolfram Alpha client initialization
    if not client:
        error_msg = """
❌ WOLFRAM ALPHA CLIENT UNAVAILABLE

The Wolfram Alpha client is not properly initialized despite having an API key.

This indicates a system initialization error. 

🔧 SUGGESTED ACTIONS:
• Restart the MCP server
• Check the server logs for initialization errors
• Verify the wolframalpha library is properly installed
• Ensure no firewall is blocking the connection
        """.strip()
        logger.error("Wolfram Alpha client not initialized when tool called")
        return [types.TextContent(type="text", text=error_msg)]
    
    try:
        logger.info(f"🔍 Processing Wolfram Alpha query: '{query[:50]}...'")
        
        # Query Wolfram Alpha using thread-safe approach
        response = await asyncio.to_thread(client.query, query)
        
        # Validate response structure
        if not response:
            error_msg = f"""
❌ NO RESPONSE FROM WOLFRAM ALPHA

Wolfram Alpha returned no response for query: "{query}"

This could indicate:
• API rate limiting or quota exceeded
• Temporary service issues
• Query format not recognized by Wolfram Alpha
• Network connectivity problems

🔧 SUGGESTED ACTIONS:
• Try rephrasing your question more clearly
• Use simpler mathematical expressions
• Wait a moment and try again
• Try a basic test query like "2+2"
• Check your API quota at https://products.wolframalpha.com/api
            """.strip()
            logger.warning(f"No response from Wolfram Alpha for query: {query}")
            return [types.TextContent(type="text", text=error_msg)]
        
        # Check for response pods (the actual results)
        if not hasattr(response, 'pods') or not response.pods:
            error_msg = f"""
🤔 NO RESULTS FOUND

Wolfram Alpha couldn't find results for: "{query}"

This might happen because:
• The query is too ambiguous or unclear
• The topic is outside Wolfram Alpha's knowledge base
• The query syntax needs adjustment
• The query contains unsupported characters or formatting

💡 SUGGESTIONS:
• Try being more specific with your question
• Use standard mathematical notation
• Ask factual questions about science, math, or general knowledge
• Examples: "population of France", "derivative of sin(x)", "weather in London"
• Avoid overly complex or compound questions
            """.strip()
            logger.info(f"No pods found in Wolfram Alpha response for: {query}")
            return [types.TextContent(type="text", text=error_msg)]
        
        # Process successful response
        results: list[types.TextContent | types.ImageContent | types.EmbeddedResource] = []
        
        # Add header with query information
        results.append(types.TextContent(
            type="text", 
            text=f"🧮 **Wolfram Alpha Results for:** {query}\n" + "="*50
        ))
        
        # Process response pods with error handling for images
        processed_pods = 0
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            for pod_idx, pod in enumerate(response.pods):
                try:
                    pod_title = getattr(pod, 'title', f'Result {pod_idx + 1}')
                    
                    # Add pod title as section header
                    if pod_title and pod_title.strip():
                        results.append(types.TextContent(
                            type="text",
                            text=f"\n📊 **{pod_title}**"
                        ))
                    
                    # Process subpods within each pod
                    subpod_count = 0
                    for subpod_idx, subpod in enumerate(pod.subpods):
                        try:
                            # Handle text content
                            if subpod.get("plaintext"):
                                text_content = subpod.plaintext.strip()
                                if text_content:
                                    results.append(types.TextContent(
                                        type="text",
                                        text=f"• {text_content}"
                                    ))
                                    subpod_count += 1
                            
                            # Handle image content with robust error handling
                            if subpod.get("img"):
                                img_url = subpod.img.get("@src")
                                if img_url:
                                    try:
                                        img_response = await http_client.get(img_url, timeout=10.0)
                                        if img_response.status_code == 200:
                                            img_base64 = base64.b64encode(img_response.content).decode('utf-8')
                                            
                                            # Determine MIME type from response headers
                                            content_type = img_response.headers.get('content-type', 'image/png')
                                            if 'gif' in content_type.lower():
                                                mime_type = "image/gif"
                                            elif 'jpeg' in content_type.lower() or 'jpg' in content_type.lower():
                                                mime_type = "image/jpeg"
                                            else:
                                                mime_type = "image/png"
                                            
                                            results.append(types.ImageContent(
                                                type="image",
                                                data=img_base64,
                                                mimeType=mime_type
                                            ))
                                            subpod_count += 1
                                        else:
                                            results.append(types.TextContent(
                                                type="text",
                                                text=f"📷 [Image unavailable - HTTP {img_response.status_code}]"
                                            ))
                                    except httpx.TimeoutException:
                                        results.append(types.TextContent(
                                            type="text",
                                            text=f"📷 [Image loading timed out]"
                                        ))
                                    except Exception as img_error:
                                        results.append(types.TextContent(
                                            type="text",
                                            text=f"📷 [Image could not be loaded: {str(img_error)[:100]}]"
                                        ))
                        except Exception as subpod_error:
                            logger.warning(f"Error processing subpod {subpod_idx}: {subpod_error}")
                            # Continue processing other subpods
                            continue
                    
                    if subpod_count > 0:
                        processed_pods += 1
                        
                except Exception as pod_error:
                    logger.warning(f"Error processing pod {pod_idx}: {pod_error}")
                    # Continue processing other pods
                    continue
        
        # Ensure we have meaningful results
        if processed_pods == 0:
            error_msg = f"""
⚠️ INCOMPLETE RESULTS

Wolfram Alpha responded but no readable content could be extracted for: "{query}"

This might indicate:
• Response format issues
• Network problems during image loading
• Temporary parsing errors
• Complex response structure that couldn't be processed

🔧 SUGGESTED ACTIONS:
• Try rephrasing your query
• Use a simpler question format
• Try again in a moment
• Test with a basic query like "2+2"
• Check if images are being blocked by your network
            """.strip()
            logger.warning(f"No processable content found in Wolfram Alpha response for: {query}")
            return [types.TextContent(type="text", text=error_msg)]
        
        # Add success footer with statistics
        results.append(types.TextContent(
            type="text",
            text=f"\n" + "="*50 + f"\n✅ **Analysis complete** - Found {processed_pods} result sections\n💡 **Tip:** Try more specific queries for detailed results"
        ))
        
        logger.info(f"✅ Successfully processed Wolfram Alpha query: {processed_pods} pods extracted")
        return results
        
    except httpx.TimeoutException:
        error_msg = f"""
⏰ QUERY TIMEOUT

The Wolfram Alpha query timed out: "{query}"

This usually happens when:
• Network connection is slow
• Wolfram Alpha servers are overloaded
• The query is computationally intensive

🔧 SUGGESTED ACTIONS:
• Try a simpler query
• Check your internet connection
• Wait a moment and try again
• Break complex queries into smaller parts
        """.strip()
        logger.error(f"Timeout during Wolfram Alpha query: {query}")
        return [types.TextContent(type="text", text=error_msg)]
        
    except httpx.HTTPStatusError as e:
        error_msg = f"""
🚫 WOLFRAM ALPHA API ERROR

HTTP {e.response.status_code} error during query: "{query}"

This indicates:
• API key issues (401/403 errors)
• Rate limiting (429 error)
• Server problems (5xx errors)

🔧 TROUBLESHOOTING:
• Verify your API key is valid at https://products.wolframalpha.com/api
• Check if you've exceeded your API quota
• Wait before retrying if rate limited
• Contact Wolfram Alpha support for persistent issues
        """.strip()
        logger.error(f"HTTP error {e.response.status_code} during Wolfram Alpha query: {query}")
        return [types.TextContent(type="text", text=error_msg)]
        
    except Exception as e:
        # Comprehensive error analysis with specific guidance
        error_details = str(e)
        error_type = type(e).__name__
        tb_str = traceback.format_exc()
        
        # Categorize common error types
        if "Content-Type" in error_details or "xml" in error_details.lower():
            category = "API Response Format Issue"
            likely_cause = "Invalid API key or API service returning error page"
            solution = "Verify your WOLFRAM_API_KEY is correct and valid"
        elif "timeout" in error_details.lower():
            category = "Network Timeout"
            likely_cause = "Network connectivity or server response issues"
            solution = "Check internet connection and try a simpler query"
        elif "connection" in error_details.lower() or "network" in error_details.lower():
            category = "Network Connection Error"
            likely_cause = "Cannot reach Wolfram Alpha servers"
            solution = "Check internet connection and firewall settings"
        elif "assertion" in error_details.lower() or "attribute" in error_details.lower():
            category = "API Response Parsing Error"
            likely_cause = "Unexpected response format from Wolfram Alpha"
            solution = "Try a different query format or contact support"
        elif "authentication" in error_details.lower() or "unauthorized" in error_details.lower():
            category = "Authentication Error"
            likely_cause = "Invalid or missing API key"
            solution = "Check your WOLFRAM_API_KEY environment variable"
        else:
            category = "Unexpected Error"
            likely_cause = "Unknown system or API issue"
            solution = "Try again later or contact support"
        
        error_msg = f"""
❌ WOLFRAM ALPHA QUERY FAILED

Query: "{query}"
Error Type: {error_type}
Category: {category}

🔍 LIKELY CAUSE: {likely_cause}

🔧 RECOMMENDED SOLUTION: {solution}

📋 TECHNICAL DETAILS: {error_details[:200]}

Traceback:
{tb_str}

💡 ADDITIONAL TROUBLESHOOTING:
• Verify WOLFRAM_API_KEY environment variable is set correctly
• Test your API key at https://products.wolframalpha.com/api
• Try a simple test query like "2+2"
• Check internet connectivity
• Wait a moment and try again
• Ensure your API quota hasn't been exceeded
        """.strip()
        
        logger.error(f"Unexpected error during Wolfram Alpha query '{query}': {error_type} - {error_details}")
        return [types.TextContent(type="text", text=error_msg)]


# =============================================================================
# MCP RESOURCE DEFINITIONS
# =============================================================================

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    Define available MCP resources for status checking and diagnostics.
    
    Resources provide read-only access to service status and configuration.
    
    Returns:
        list[types.Resource]: List of available resources
    """
    return [
        types.Resource(
            uri="wolfram://status",
            name="Wolfram Alpha Service Status",
            description="Check if the Wolfram Alpha service is properly configured and working",
            mimeType="text/plain",
        ),
        types.Resource(
            uri="wolfram://config",
            name="Wolfram Alpha Configuration",
            description="View current configuration and API key status",
            mimeType="text/plain",
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Handle resource reading requests for diagnostics and status information.
    
    Args:
        uri (AnyUrl): The resource URI to read
        
    Returns:
        str: Resource content
        
    Raises:
        ValueError: If the resource URI is not recognized
    """
    uri_str = str(uri)
    
    if uri_str == "wolfram://status":
        import os
        
        # Check API key
        api_key = os.getenv('WOLFRAM_API_KEY')
        api_status = "✅ Set" if api_key else "❌ Not Set"
        
        # Check client initialization
        client_status = "✅ Initialized" if client else "❌ Not Initialized"
        
        # Test a simple query if everything is set up
        test_result = "❓ Not Tested"
        if api_key and client:
            try:
                test_response = await asyncio.to_thread(client.query, "2+2")
                if test_response and hasattr(test_response, 'pods') and test_response.pods:
                    test_result = "✅ Working"
                else:
                    test_result = "⚠️ No Results"
            except Exception as e:
                test_result = f"❌ Error: {str(e)[:50]}..."
        
        status_report = f"""
🔍 WOLFRAM ALPHA SERVICE STATUS

🔑 API Key: {api_status}
🔌 Client: {client_status}
🧪 Test Query: {test_result}

📊 SERVICE DETAILS:
• Tool Name: query-wolfram-alpha
• Client Library: wolframalpha
• Connection: HTTPS to Wolfram Alpha API
• Response Format: XML with images

🔧 CONFIGURATION:
• Environment Variable: WOLFRAM_API_KEY
• API Documentation: https://products.wolframalpha.com/api
• Free Tier Available: 2,000 queries/month

📋 USAGE EXAMPLES:
• Mathematical: "derivative of x^2 + 3x"
• Scientific: "mass of Jupiter"
• Conversions: "100 mph to m/s"
• Factual: "population of Tokyo"

⚡ STATUS: {"READY" if (api_key and client and "Working" in test_result) else "NOT READY"}
        """.strip()
        
        return status_report
    
    elif uri_str == "wolfram://config":
        import os
        
        api_key = os.getenv('WOLFRAM_API_KEY')
        
        config_info = f"""
⚙️ WOLFRAM ALPHA CONFIGURATION

🔑 API KEY STATUS:
• Environment Variable: WOLFRAM_API_KEY
• Status: {"Set (length: " + str(len(api_key)) + ")" if api_key else "Not Set"}
• Validation: {"Appears valid format" if api_key and len(api_key) > 10 else "Invalid or missing"}

🌐 API ENDPOINTS:
• Base URL: http://api.wolframalpha.com/v2/query
• Method: GET with XML response
• Timeout: 30 seconds

📦 DEPENDENCIES:
• wolframalpha: Python client library
• httpx: HTTP client for image downloads
• mcp: Model Context Protocol framework

🔧 SETUP INSTRUCTIONS:
1. Get API key from: https://products.wolframalpha.com/api
2. Set environment variable: WOLFRAM_API_KEY=your_key_here
3. Restart the MCP server
4. Test with simple query like "2+2"

💡 TROUBLESHOOTING:
• Verify API key is correctly set
• Check network connectivity
• Ensure quota isn't exceeded
• Try simpler queries if complex ones fail
        """.strip()
        
        return config_info
    
    else:
        raise ValueError(f"Unknown resource: {uri}")


# =============================================================================
# MAIN SERVER ENTRY POINT
# =============================================================================
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
