# lynxcheck-mcp

Free MCP server (stdio, Python 3, no dependencies) with nineteen read-only tools for crypto traders and AI agents. Data and statistics only: no trading signals, not financial advice.

| Tool | What it returns | Source |
|---|---|---|
| `check_token` | Solana Pump.fun token: 0-100 risk score, chance of losing over half within 2 minutes, factors, creator history, funding network | LynxCheck API (keyless free tier) |
| `creator_lookup` | Creator wallet record: tokens launched, how many collapsed, funding network (counts only) | LynxCheck API |
| `solana_fees` | Jito tip percentiles: what landing fast costs right now | Jito public API |
| `funding_rates` | Most negative and most positive perpetual funding rates, annualized | Binance public API |
| `stablecoin_peg` | Large USD stablecoins trading away from $1 | DefiLlama |
| `defi_yields` | Highest base yields on stablecoin pools with at least 10M USD TVL | DefiLlama |
| `fear_greed` | Crypto Fear and Greed index | alternative.me |
| `check_evm_token` | BNB Chain, Base or Ethereum token: what the owner can do (mint, blacklist, pause, fees, upgrade), ownership, proxy, V2 liquidity. Static heuristics | LynxCheck API |
| `batch_check` | Up to 20 tokens (Solana and EVM) in one call: verdict AVOID / CAUTION / OK-NO-MAJOR-FLAGS, score, top flags, honeypot and tax. Each item counts as one request | LynxCheck API |
| `funding_compare` | Funding rates side by side on Binance, Bybit and OKX: largest differences and extremes. Descriptive only | LynxCheck API (public exchange data) |
| `solana_approvals` | Token accounts of a Solana wallet with an active delegate (permissions you may want to revoke). Read-only | LynxCheck API |
| `wallet_lookup` | Solana wallet ledger statistics (trips, hit rate, whether it persisted). Needs `LYNXCHECK_API_KEY` | LynxCheck API |
| `solana_portfolio` | Risk scores of the tokens a Solana wallet holds (up to 10) | LynxCheck API |
| `data_coverage` | Dates, counts and held-out validation behind the numbers; EVM status | LynxCheck API |
| `exit_check` | What selling a token would really return, from public pool data | LynxCheck API |
| `wallet_health` | Public wallet card: dangerous tokens traded, approvals, look-alike addresses | LynxCheck API |
| `wallet_delegation` | EIP-7702 delegation of an EVM wallet on all 7 chains | LynxCheck API |
| `decode_signature` | Plain-words explanation of a wallet signature request. Nothing is stored | LynxCheck API |
| `trade_cost` | Pump.fun round-trip cost for your size: fees, price impact, tips, break-even move | local calculation |

Market tools call the public APIs directly from your machine; nothing goes through LynxCheck.

## Data sources and credit
Jito public API, Binance public API, DefiLlama (defillama.com), alternative.me (Fear and Greed Index, https://alternative.me/crypto/fear-and-greed-index/). Each tool answer names its source. Please respect those services' terms and rate limits; results are cached for a short time.

## No install
Clients that accept a remote MCP server can use `https://mintsieve.141-95-95-56.sslip.io/v1/mcp`: 10 token and wallet tools, no key needed to start.

## Use
```
python3 mcp_server.py
```
Example MCP client config:
```json
{"mcpServers": {"lynxcheck": {"command": "python3", "args": ["/path/to/mcp_server.py"]}}}
```
Environment: `LYNXCHECK_URL` (default `https://mintsieve.141-95-95-56.sslip.io`), optional `LYNXCHECK_API_KEY` for higher limits on `check_token` and `creator_lookup`.

## Test
`python3 test_tools.py` (parsers are tested with fixtures).

## License
MIT, see LICENSE. The LynxCheck service itself and its model are not part of this repository.
