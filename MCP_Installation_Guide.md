# MCP Tools Installation and Usage Guide

## Prerequisites
- **Python**: 3.8+ 
- **Node.js**: 16+ (for TypeScript tools)

## Python-based MCP Tools

### Wolfram Alpha & News Fact-Checker
```bash
# Navigate to tool directory
cd MCP/[tool-name]

# Install requirements
uv pip install -r requirements.txt

```

## TypeScript-based MCP Tools

### Website Verification & Google Maps
**Pre-compiled files provided**: `dist/index.cjs` files are ready to use.

**If recompilation needed**:
```bash
cd MCP/[tool-name]
npm install
npm run build
```

## Configuration

### For Standard MCP Protocol (DIVE)
Use configurations from `DIVE_Config_Summary.md`

### For CLI Tools
Use example configurations from `Mcp_json/` folder:
- `1.json.example` - Website Verification
- `2.json.example` - Wolfram Alpha  
- `3.json.example` - Google Maps
- `4.json.example` - News Fact-Checker

## API Keys Required

| Tool | API Key | Get From |
|------|---------|----------|
| Wolfram Alpha | `WOLFRAM_API_KEY` | [Wolfram Developer Portal](https://developer.wolframalpha.com/) |
| News Fact-Checker | `GEMINI_API_KEY`, `NEWS_API_KEY` | [Google AI Studio](https://makersuite.google.com/), [NewsAPI](https://newsapi.org/) |
| Google Maps | `GOOGLE_MAPS_API_KEY` | [Google Cloud Console](https://console.cloud.google.com/) |
| Website Verification | None | - |

## Quick Test
```bash
# Python tools
python -m mcp_wolfram_alpha
python -m factcheck.news_factcheck

# TypeScript tools  
node MCP/MCP_Website_Verification/dist/index.cjs
node MCP/mcp-google-map/dist/index.cjs
```

## Troubleshooting
- **Module not found**: Check PYTHONPATH in configuration
- **Command not found**: Ensure Node.js installed, recompile if needed
- **API errors**: Verify API keys are set correctly
