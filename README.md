# mintsieve-mcp

A tiny MCP server (stdio, no dependencies, Python 3) that lets AI agents check a Solana Pump.fun token before acting on it.

Tool: `check_token(mint)` returns the chance that the token loses more than half of its value within 2 minutes after its 10th trade, a risk band, the main factors, and the creator's history. The numbers are historical statistics from past launches (validated on tokens the model had not seen, AUC about 0.88). They are not financial advice and not a prediction for any single token.

## Use
```
python3 mcp_server.py
```
Environment: `MINTSIEVE_URL` (default `https://mintsieve.141-95-95-56.sslip.io`), optional `MINTSIEVE_API_KEY` for higher limits. The keyless free tier answers known tokens always and fresh on-demand checks a few times per hour.

Example MCP client config:
```json
{"mcpServers": {"mintsieve": {"command": "python3", "args": ["/path/to/mcp_server.py"]}}}
```

## License
MIT, see LICENSE. The MintSieve service itself and its model are not part of this repository.
