
> Be careful with the path, must realtive/absolut link to target folder/file


  "mcpServers": {
    "google-map": {
      "transport": "stdio",
      "enabled": true,
      "command": "node",
      "args": [
        "mcp-google-map/dist/index.cjs"
      ],
      "env": {
        "GOOGLE_MAPS_API_KEY": ""
      },
      "url": null,
      "headers": null
    }
  }
}

{
  "mcpServers": {
    "website-verifier": {
      "transport": "stdio",
      "enabled": true,
      "command": "node",
      "args": [
        "MCP_Website_Verification/dist/index.cjs"
      ],
      "env": {},
      "url": null,
      "headers": null
    }
  }
}


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

{
  "mcpServers": {
    "news-factcheck": {
      "transport": "stdio",
      "enabled": true,
      "command": "python",
      "args": [
        "-m",
        "factcheck.news_factcheck"
      ],
      "env": {
        "GEMINI_API_KEY": "",
        "NEWS_API_KEY": "",
        "PYTHONPATH": "news-factchecker-mcp/src"
      },
      "url": null,
      "headers": null
    }
  }
}