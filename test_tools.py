import unittest
import mcp_server as m

class T(unittest.TestCase):
    def test_jito(self):
        r = m.parse_jito([{"time": "t", "landed_tips_25th_percentile": 1e-6, "landed_tips_50th_percentile": 5e-6, "landed_tips_75th_percentile": 9e-5, "landed_tips_95th_percentile": 5e-3, "landed_tips_99th_percentile": 6e-3}])
        self.assertEqual(r["landed_tip_sol"]["p95"], 5e-3)
    def test_funding_sorted_and_annualized(self):
        rows = [{"symbol": "AAAUSDT", "lastFundingRate": "0.0001", "markPrice": "1"}, {"symbol": "BBBUSDT", "lastFundingRate": "-0.0005", "markPrice": "2"},
                {"symbol": "CCCUSDT", "lastFundingRate": "0.0010", "markPrice": "3"}, {"symbol": "BTCUSD_PERP", "lastFundingRate": "0.5"}, {"symbol": "XUSDT", "lastFundingRate": "bad"}]
        r = m.parse_funding(rows, top=1)
        self.assertEqual(r["most_positive"][0]["symbol"], "CCCUSDT"); self.assertEqual(r["most_negative"][0]["symbol"], "BBBUSDT")
        self.assertAlmostEqual(r["most_positive"][0]["annualized_pct"], 0.0010 * 3 * 365 * 100, places=1); self.assertEqual(r["count"], 3)
    def test_stables(self):
        d = {"peggedAssets": [{"symbol": "USDT", "name": "Tether", "pegType": "peggedUSD", "price": 1.0003, "circulating": {"peggedUSD": 1e11}},
                              {"symbol": "XUSD", "name": "X", "pegType": "peggedUSD", "price": 0.97, "circulating": {"peggedUSD": 5e8}},
                              {"symbol": "EURS", "pegType": "peggedEUR", "price": 1.1, "circulating": {"peggedEUR": 1e9}}]}
        r = m.parse_stables(d); self.assertEqual([x["symbol"] for x in r["off_peg"]], ["XUSD"]); self.assertEqual(r["checked"], 2)
    def test_yields_filters(self):
        d = {"data": [{"chain": "A", "project": "p", "symbol": "S", "tvlUsd": 5e7, "apy": 8, "apyBase": 6, "stablecoin": True},
                      {"chain": "B", "project": "q", "symbol": "T", "tvlUsd": 1e5, "apy": 900, "apyBase": 900, "stablecoin": True},
                      {"chain": "C", "project": "r", "symbol": "U", "tvlUsd": 5e8, "apy": 30, "apyBase": 30, "stablecoin": False}]}
        r = m.parse_yields(d); self.assertEqual([p["chain"] for p in r["pools"]], ["A"])
    def test_fng(self):
        self.assertEqual(m.parse_fng({"data": [{"value": "23", "value_classification": "Extreme Fear", "timestamp": "5"}]})["value"], 23)
    def test_trade_cost_matches_calculator(self):
        r = m.trade_cost(1.0, 34, 0.001, 0.0); self.assertAlmostEqual(r["fees_pct"], 2.5); self.assertAlmostEqual(r["price_impact_pct"], 4.41, places=2); self.assertAlmostEqual(r["tips_pct"], 0.2, places=2)
    def test_unknown_tool_and_errors_are_contained(self):
        self.assertIn("error", m.run_tool("nope", {})); self.assertIn("error", m.run_tool("trade_cost", {}))
if __name__ == "__main__": unittest.main()
