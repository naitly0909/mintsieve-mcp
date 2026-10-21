#!/usr/bin/env python3
"""MintSieve MCP server (stdio, no dependencies). One tool: check_token(mint) -> risk probability, band, creator history.
Config: MINTSIEVE_URL (default https://mintsieve.141-95-95-56.sslip.io), optional MINTSIEVE_API_KEY. Statistics from past launches, not advice."""
import json, os, sys, urllib.request
URL = os.environ.get("MINTSIEVE_URL", "https://mintsieve.141-95-95-56.sslip.io").rstrip("/")
KEY = os.environ.get("MINTSIEVE_API_KEY")
TOOL = {"name": "check_token", "description": "Risk check for a Solana Pump.fun token: probability of losing more than half of its value within 2 minutes after the 10th trade, risk band, main factors and the creator's history. Historical statistics, not financial advice.",
        "inputSchema": {"type": "object", "properties": {"mint": {"type": "string", "description": "token mint address (base58)"}}, "required": ["mint"]}}
def call(mint):
    req = urllib.request.Request(f"{URL}/v1/token/{mint}?scan=1", headers={"User-Agent": "mintsieve-mcp/1", **({"X-API-Key": KEY} if KEY else {})})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=60))
    except Exception as e:
        return {"error": str(e)[:200]}
    rm = d.get("risk_model") or {}
    return {"available": rm.get("available"), "p_lose_gt_50": rm.get("p_lose_gt_50"), "band": rm.get("band_v2"), "factors": [f.get("label") for f in rm.get("top_factors", [])],
            "creator_history": d.get("creator_reputation"), "message": d.get("message"), "disclaimer": d.get("disclaimer")}
def reply(i, result=None, error=None):
    m = {"jsonrpc": "2.0", "id": i}; m.update({"error": error} if error else {"result": result})
    sys.stdout.write(json.dumps(m) + "\n"); sys.stdout.flush()
for line in sys.stdin:
    try: r = json.loads(line)
    except Exception: continue
    i, m = r.get("id"), r.get("method")
    if m == "initialize": reply(i, {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "mintsieve", "version": "0.1"}})
    elif m == "tools/list": reply(i, {"tools": [TOOL]})
    elif m == "tools/call":
        a = (r.get("params") or {}).get("arguments") or {}
        out = call(str(a.get("mint", ""))) if (r.get("params") or {}).get("name") == "check_token" else {"error": "unknown tool"}
        reply(i, {"content": [{"type": "text", "text": json.dumps(out)}]})
    elif i is not None: reply(i, error={"code": -32601, "message": "method not found"})
