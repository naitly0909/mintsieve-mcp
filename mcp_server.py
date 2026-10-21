#!/usr/bin/env python3
"""MintSieve MCP server v0.2 (stdio, standard library only). Free tools for crypto traders and AI agents.

Tools (all read-only; market tools call free public APIs straight from your machine, nothing goes through MintSieve):
  check_token, creator_lookup      Solana Pump.fun risk (MintSieve API; keyless free tier)
  solana_fees                      Jito tip percentiles = what landing fast costs right now
  funding_rates                    perpetual funding rates (Binance), extremes and annualized
  stablecoin_peg                   USD stablecoins trading away from $1 (DefiLlama)
  defi_yields                      top stable yields on sizeable pools (DefiLlama)
  fear_greed                       crypto Fear and Greed index (alternative.me)
  check_evm_token                  EVM token contract capabilities (7 networks)
  funding_compare                  funding rates compared across Binance, Bybit and OKX
  solana_approvals                 token delegates on a Solana wallet (permissions to revoke)
  trade_cost                       Pump.fun round-trip cost for your size
Data and statistics only. Not financial advice. No trading signals.
Env: MINTSIEVE_URL, MINTSIEVE_API_KEY (optional)."""
import json, os, sys, time, urllib.request

URL = os.environ.get("MINTSIEVE_URL", "https://mintsieve.141-95-95-56.sslip.io").rstrip("/")
KEY = os.environ.get("MINTSIEVE_API_KEY")
NOTE = "Data and statistics only, not financial advice."
_cache = {}


def http_json(url, ttl=60, headers=None):
    hit = _cache.get(url)
    if hit and time.time() - hit[0] < ttl:
        return hit[1]
    req = urllib.request.Request(url, headers={"User-Agent": "mintsieve-mcp/0.2", **(headers or {})})
    with urllib.request.urlopen(req, timeout=45) as r:
        data = json.load(r)
    _cache[url] = (time.time(), data)
    return data


# ---- pure parsers (unit-tested with fixtures) ----
def parse_jito(rows):
    r = rows[0]
    return {"time": r["time"], "landed_tip_sol": {"p25": r["landed_tips_25th_percentile"], "p50": r["landed_tips_50th_percentile"], "p75": r["landed_tips_75th_percentile"],
            "p95": r["landed_tips_95th_percentile"], "p99": r["landed_tips_99th_percentile"]},
            "source": "Jito public API (bundles.jito.wtf)", "meaning": "Tips (SOL) of bundles that landed. Winning a race against bots needs the high percentiles; a patient trade can use the median."}


def parse_funding(rows, top=5, min_abs=0.0):
    items = []
    for x in rows:
        try:
            fr = float(x["lastFundingRate"])
        except (KeyError, ValueError, TypeError):
            continue
        if x["symbol"].endswith("USDT"):
            items.append({"symbol": x["symbol"], "funding_8h_pct": round(fr * 100, 4), "annualized_pct": round(fr * 3 * 365 * 100, 1), "mark": float(x.get("markPrice") or 0)})
    items.sort(key=lambda i: i["funding_8h_pct"])
    return {"most_negative": items[:top], "most_positive": items[-top:][::-1], "count": len(items),
            "source": "Binance public futures API", "meaning": "Positive funding: longs pay shorts (crowded longs). Negative: shorts pay longs. A description of positioning, not a forecast."}


def parse_stables(data, top=40, min_dev=0.005):
    out = []
    for a in data.get("peggedAssets", []):
        cap = ((a.get("circulating") or {}).get("peggedUSD")) or 0
        p = a.get("price")
        if a.get("pegType") == "peggedUSD" and p and cap:
            out.append({"symbol": a.get("symbol"), "name": a.get("name"), "price": round(p, 4), "deviation_pct": round((p - 1) * 100, 2), "market_cap_usd": round(cap)})
    out.sort(key=lambda i: -i["market_cap_usd"])
    top_assets = out[:top]
    return {"off_peg": [i for i in top_assets if abs(i["deviation_pct"]) >= min_dev * 100], "checked": len(top_assets),
            "source": "DefiLlama stablecoins API (defillama.com)", "meaning": f"Top {len(top_assets)} USD stablecoins by size; listed if the price is more than {min_dev*100:.1f}% from $1."}


def parse_yields(data, min_tvl=1e7, stable_only=True, top=10):
    rows = [p for p in data.get("data", []) if (p.get("tvlUsd") or 0) >= min_tvl and p.get("apy") is not None and (p.get("stablecoin") or not stable_only)]
    rows.sort(key=lambda p: -(p.get("apyBase") or 0))
    return {"pools": [{"chain": p["chain"], "project": p["project"], "symbol": p["symbol"], "tvl_usd": round(p["tvlUsd"]), "apy_pct": round(p["apy"], 2),
                       "apy_base_pct": round(p.get("apyBase") or 0, 2), "il_risk": p.get("ilRisk")} for p in rows[:top]],
            "source": "DefiLlama yields API (defillama.com)", "meaning": "Highest base APY among pools with sizeable TVL. High yield means high risk; check the protocol before using it."}


def parse_fng(data):
    d = data["data"][0]
    return {"value": int(d["value"]), "classification": d["value_classification"], "timestamp": int(d["timestamp"]),
            "source": "alternative.me Fear and Greed Index (https://alternative.me/crypto/fear-and-greed-index/)", "meaning": "0 extreme fear, 100 extreme greed. A sentiment gauge, not a signal."}


def trade_cost(size_sol, virtual_sol=34.0, tip_sol=0.0005, priority_sol=0.00005):
    fees = 2 * 0.0125; impact = 1.5 * size_sol / virtual_sol; tips = 2 * (tip_sol + priority_sol) / size_sol
    return {"size_sol": size_sol, "fees_pct": round(fees * 100, 2), "price_impact_pct": round(impact * 100, 2), "tips_pct": round(tips * 100, 2),
            "break_even_move_pct": round((fees + impact + tips) * 100, 2), "total_cost_sol": round((fees + impact + tips) * size_sol, 5),
            "meaning": "Round-trip cost on Pump.fun: fees exact (1.25% per side), impact an empirical estimate (about 1.5 x size / virtual SOL), tips as you set them."}


# ---- tools ----
def mintsieve(path):
    req = urllib.request.Request(URL + path, headers={"User-Agent": "mintsieve-mcp/0.2", **({"X-API-Key": KEY} if KEY else {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def t_check_token(a):
    d = mintsieve(f"/v1/token/{a['mint']}?scan=1"); rm = d.get("risk_model") or {}
    return {"available": rm.get("available"), "score_0_100": rm.get("score_0_100"), "p_lose_gt_50": rm.get("p_lose_gt_50"), "band": rm.get("band_v2"),
            "factors": [f.get("label") for f in rm.get("top_factors", [])], "creator_history": d.get("creator_reputation"),
            "funding_network": d.get("funder_reputation"), "message": d.get("message"), "limit_note": d.get("scan_limit"), "disclaimer": d.get("disclaimer")}


TOOLS = {
    "check_token": ("Risk check for a Solana Pump.fun token: 0-100 score, chance of losing over half within 2 minutes, factors, creator history and funding network.",
                    {"mint": {"type": "string", "description": "token mint address (base58)"}}, ["mint"], t_check_token),
    "creator_lookup": ("Record of a Pump.fun creator wallet: tokens launched in our data, how many collapsed, and its funding network (counts only).",
                       {"wallet": {"type": "string"}}, ["wallet"], lambda a: mintsieve(f"/v1/creator/{a['wallet']}?scan=1")),
    "solana_fees": ("Current Jito tip percentiles on Solana: what it costs to land a bundle fast right now.", {}, [], lambda a: parse_jito(http_json("https://bundles.jito.wtf/api/v1/bundles/tip_floor", 20))),
    "funding_rates": ("Perpetual futures funding rates (Binance USDT-margined): the most negative and most positive, annualized.",
                      {"top": {"type": "integer", "description": "how many per side (default 5)"}}, [], lambda a: parse_funding(http_json("https://fapi.binance.com/fapi/v1/premiumIndex", 60), int(a.get("top", 5)))),
    "stablecoin_peg": ("USD stablecoins among the largest that trade away from $1 right now (DefiLlama).", {}, [], lambda a: parse_stables(http_json("https://stablecoins.llama.fi/stablecoins?includePrices=true", 300))),
    "defi_yields": ("Highest base yields on stablecoin pools with at least 10M USD TVL (DefiLlama). Data only.", {"top": {"type": "integer"}}, [],
                    lambda a: parse_yields(http_json("https://yields.llama.fi/pools", 900), top=int(a.get("top", 10)))),
    "fear_greed": ("Crypto Fear and Greed index (alternative.me).", {}, [], lambda a: parse_fng(http_json("https://api.alternative.me/fng/", 600))),
    "check_evm_token": ("Static contract check for a BNB Chain, Base, Ethereum, Arbitrum, Polygon, Optimism or Avalanche token: what the owner can do (mint, blacklist, pause, fees, upgrade), ownership, proxy and V2 liquidity. Heuristics, not a score.",
                        {"chain": {"type": "string", "enum": ["bsc", "base", "eth", "arb", "polygon", "op", "avax"]}, "address": {"type": "string"}}, ["chain", "address"],
                        lambda a: mintsieve(f"/v1/evm/{a['chain']}/{a['address']}")),
    "funding_compare": ("Perpetual funding rates side by side on Binance, Bybit and OKX: the largest differences between exchanges and the most extreme averages. Descriptive only.", {}, [], lambda a: mintsieve("/v1/funding")),
    "solana_approvals": ("Token accounts of a Solana wallet that have an active delegate (an address allowed to move that token). Read-only; helps find permissions to revoke.",
                         {"wallet": {"type": "string"}}, ["wallet"], lambda a: mintsieve(f"/v1/approvals/solana/{a['wallet']}")),
    "trade_cost": ("Round-trip cost of a Pump.fun trade for your size: fees, price impact, tips, and the break-even price move.",
                   {"size_sol": {"type": "number"}, "virtual_sol": {"type": "number"}, "tip_sol": {"type": "number"}, "priority_sol": {"type": "number"}}, ["size_sol"],
                   lambda a: trade_cost(float(a["size_sol"]), float(a.get("virtual_sol", 34)), float(a.get("tip_sol", 0.0005)), float(a.get("priority_sol", 0.00005)))),
}


def run_tool(name, args):
    if name not in TOOLS:
        return {"error": "unknown tool"}
    try:
        out = TOOLS[name][3](args or {})
        return dict(out, note=NOTE) if isinstance(out, dict) else {"result": out, "note": NOTE}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:160]}"}


def reply(i, result=None, error=None):
    m = {"jsonrpc": "2.0", "id": i}; m.update({"error": error} if error else {"result": result})
    sys.stdout.write(json.dumps(m) + "\n"); sys.stdout.flush()


def main():
    for line in sys.stdin:
        try:
            r = json.loads(line)
        except Exception:
            continue
        i, m = r.get("id"), r.get("method")
        if m == "initialize":
            reply(i, {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "mintsieve", "version": "0.2"}})
        elif m == "tools/list":
            reply(i, {"tools": [{"name": n, "description": d, "inputSchema": {"type": "object", "properties": p, "required": req}} for n, (d, p, req, _) in TOOLS.items()]})
        elif m == "tools/call":
            p = r.get("params") or {}
            reply(i, {"content": [{"type": "text", "text": json.dumps(run_tool(p.get("name"), p.get("arguments")))}]})
        elif i is not None:
            reply(i, error={"code": -32601, "message": "method not found"})


if __name__ == "__main__":
    main()
