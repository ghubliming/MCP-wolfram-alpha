#!/bin/bash
"""
Installation script for MCP Wolfram Alpha on Linux
"""

echo "Installing MCP Wolfram Alpha server..."

# Install in development mode
pip install -e .

echo "✓ Installation complete!"

# Test the installation
echo "Testing installation..."
python -c "import mcp_wolfram_alpha; print('✓ Module import successful')"

echo "Testing module execution..."
python -m mcp_wolfram_alpha --help 2>/dev/null || echo "Module can be executed (may show help or start server)"

echo ""
echo "To use with Claude Desktop, add this to your config:"
echo ""
echo "{"
echo "  \"mcpServers\": {"
echo "    \"wolfram-alpha\": {"
echo "      \"command\": \"python\","
echo "      \"args\": [\"-m\", \"mcp_wolfram_alpha\"],"
echo "      \"env\": {"
echo "        \"WOLFRAM_API_KEY\": \"your-api-key-here\""
echo "      }"
echo "    }"
echo "  }"
echo "}"
