# 🧮 Wolfram Alpha MCP Server


A powerful Model Context Protocol (MCP) server that bridges AI assistants with Wolfram Alpha's computational intelligence engine. Access mathematical computations, scientific data, unit conversions, and factual information directly through your AI conversations.

## ✨ Features

### 🧮 **Mathematical Excellence**
- Solve complex equations and systems
- Calculate derivatives, integrals, and limits
- Matrix operations and linear algebra
- Step-by-step solution explanations
- Graph plotting and visualization

### 📊 **Scientific Intelligence**
- Real-time scientific and statistical data
- Chemical formulas and molecular structures
- Physical constants and properties
- Astronomical data and calculations
- Weather and climate information

### 🔢 **Universal Conversions**
- Currency exchange rates (real-time)
- Unit conversions (metric, imperial, scientific)
- Temperature, distance, weight, volume
- Time zones and date calculations
- Number base conversions

### 📈 **Data Analysis**
- Statistical analysis and computations
- Data visualization and plotting
- Comparative analysis
- Historical trends and patterns
- Economic indicators and metrics

### 🌍 **Knowledge Engine**
- Factual information with citations
- Historical data and events
- Geographic and demographic data
- Language translations and linguistics
- Cultural and reference information

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** - Required for modern async features
- **Wolfram Alpha API Key** - Get yours [here](https://developer.wolframalpha.com/)

### Installation

```bash
# Navigate to the project directory
cd MCP-wolfram-alpha

# Install in development mode (recommended)
pip install -e .

# Or install normally
pip install .

# Verify installation
python -m mcp_wolfram_alpha
```

### API Key Configuration(only for TEST purpose, for MCP usage set up API key in json)

1. **Get your API key** from [Wolfram Alpha Developer Portal](https://developer.wolframalpha.com/)
2. **Set environment variable**:
   
   **Windows (PowerShell):**
   ```powershell
   $env:WOLFRAM_API_KEY="your_api_key_here"
   ```
   
   **Linux/macOS:**
   ```bash
   export WOLFRAM_API_KEY="your_api_key_here"
   ```

3. **Alternative: .env file**
   ```bash
   echo "WOLFRAM_API_KEY=your_api_key_here" > .env
   ```

## 🔧 Configuration

### MCP Client Setup

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "wolfram-alpha": {
      "transport": "stdio",
      "enabled": true,
      "command": "python",
      "args": [
        "-m",
        "mcp_wolfram_alpha"
      ],
      "env": {
        "WOLFRAM_API_KEY": "-",
        "PYTHONPATH": "MCP-wolfram-alpha/src"
      },
      "url": null,
      "headers": null
    }
  }
}
```

## 🛠️ Available Tools

### `query-wolfram-alpha`

**Description:** Query Wolfram Alpha's computational knowledge engine

**Parameters:**
- `query` (string, required): Your question or calculation

**Example Queries:**

```text
Mathematics:
• "What is the derivative of x^2 + 3x + 2?"
• "Solve the system: 2x + 3y = 7, x - y = 1"
• "Integrate sin(x)*cos(x) from 0 to π"
• "Plot y = x^2 - 4x + 3"

Science:
• "What is the molecular formula of caffeine?"
• "Distance from Earth to Alpha Centauri"
• "Half-life of Carbon-14"
• "Boiling point of water at 2000m altitude"

Conversions:
• "Convert 100 USD to EUR"
• "25°C to Fahrenheit and Kelvin"
• "5 feet 10 inches to meters"
• "1 gallon to liters"

Data & Facts:
• "Population of Tokyo in 2024"
• "GDP of Germany vs France"
• "Weather in New York today"
• "Stock price of AAPL"
```

## 📋 Available Prompts

### `wa` - Wolfram Alpha Query Assistant

**Description:** Generate optimized queries for Wolfram Alpha's computational intelligence

**Arguments:**
- `query` (required): Your question or calculation

**What it helps with:**
- 🧮 Mathematical problem formulation
- 📊 Scientific data research
- 🔢 Unit conversion queries
- 📈 Data analysis requests
- 🌍 Factual information retrieval

**Usage Examples:**
```text
User: "wa: How do I calculate compound interest?"
Assistant: Generates optimized Wolfram Alpha queries for compound interest calculations

User: "wa: Compare renewable energy usage between countries"
Assistant: Creates structured queries for international energy data comparison
```



### Running Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_wolfram_alpha

# Run specific test
pytest test/test_server.py -v
```

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd MCP-wolfram-alpha

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest
```

## 🛡️ Error Handling & Troubleshooting

### Comprehensive Error Management

- ✅ **API Key Validation** - Automatic verification on startup
- ✅ **Query Validation** - Input sanitization and format checking
- ✅ **Rate Limiting** - Graceful handling of API limits
- ✅ **Network Resilience** - Retry logic and connection handling
- ✅ **Response Parsing** - Detailed error messages for failures

### Common Issues & Solutions

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Missing API Key** | `WOLFRAM_API_KEY environment variable not set` | Set your API key in environment variables |
| **Import Errors** | `ModuleNotFoundError: No module named 'mcp_wolfram_alpha'` | Install package: `pip install -e .` |
| **Rate Limits** | `API rate limit exceeded` | Wait before retry or upgrade API plan |
| **Network Issues** | `Failed to connect to Wolfram Alpha` | Check internet connection and firewall |
| **Invalid Query** | `Query format not recognized` | Rephrase query or check examples |

### Debug Mode

Enable detailed logging:

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Or use .env file
echo "LOG_LEVEL=DEBUG" >> .env
```

## 📊 Performance & Limits

### API Limits (Free Tier)
- **2,000 queries/month** - Free tier limit
- **1 query/second** - Rate limit
- **Basic results** - Limited output format

### Optimization Tips
- 🎯 Use specific, focused queries
- 📝 Cache frequently used results
- ⚡ Batch related calculations
- 🔄 Use step-by-step for complex problems


## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
