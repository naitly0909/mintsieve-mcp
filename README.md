# mintsieve-mcp

Free MCP server (stdio, Python 3, no dependencies) with nine read-only tools for crypto traders and AI agents. Data and statistics only: no trading signals, not financial advice.

| Tool | What it returns | Source |
|---|---|---|
| `check_token` | Solana Pump.fun token: 0-100 risk score, chance of losing over half within 2 minutes, factors, creator history, funding network | MintSieve API (keyless free tier) |
| `creator_lookup` | Creator wallet record: tokens launched, how many collapsed, funding network (counts only) | MintSieve API |
| `solana_fees` | Jito tip percentiles: what landing fast costs right now | Jito public API |
| `funding_rates` | Most negative and most positive perpetual funding rates, annualized | Binance public API |
| `stablecoin_peg` | Large USD stablecoins trading away from $1 | DefiLlama |
| `defi_yields` | Highest base yields on stablecoin pools with at least 10M USD TVL | DefiLlama |
| `fear_greed` | Crypto Fear and Greed index | alternative.me |
| `check_evm_token` | BNB Chain, Base or Ethereum token: what the owner can do (mint, blacklist, pause, fees, upgrade), ownership, proxy, V2 liquidity. Static heuristics | MintSieve API |
| `trade_cost` | Pump.fun round-trip cost for your size: fees, price impact, tips, break-even move | local calculation |

Market tools call the public APIs directly from your machine; nothing goes through MintSieve.

## Data sources and credit
Jito public API, Binance public API, DefiLlama (defillama.com), alternative.me (Fear and Greed Index, https://alternative.me/crypto/fear-and-greed-index/). Each tool answer names its source. Please respect those services' terms and rate limits; results are cached for a short time.

## Use
```
python3 mcp_server.py
```
Example MCP client config:
```json
{"mcpServers": {"mintsieve": {"command": "python3", "args": ["/path/to/mcp_server.py"]}}}
```
Environment: `MINTSIEVE_URL` (default `https://mintsieve.141-95-95-56.sslip.io`), optional `MINTSIEVE_API_KEY` for higher limits on `check_token` and `creator_lookup`.

## Test
`python3 test_tools.py` (parsers are tested with fixtures).

## License
MIT, see LICENSE. The MintSieve service itself and its model are not part of this repository.
