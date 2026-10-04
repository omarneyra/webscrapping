import unittest
from analytics import (
    calculate_value_score,
    generate_verdict,
    build_optimal_basket,
    generate_market_insights,
    get_market_benchmark,
)


class TestAnalytics(unittest.TestCase):

    def setUp(self):
        self.exceptional_whey = {
            "source": "All Nutrition",
            "category": "whey",
            "title": "Mutant Whey 5 Lb",
            "price": 61590,
            "original_price": 76990,
            "discount_pct": 20.0,
            "weight_grams": 2268.0,
            "net_protein_grams": 1655.6,
            "cost_per_gram_clp": 37.20,
        }
        self.overpriced_whey = {
            "source": "Tienda X",
            "category": "whey",
            "title": "Whey Cara 2 Lb",
            "price": 50000,
            "original_price": 52000,
            "discount_pct": 3.8,
            "weight_grams": 907.0,
            "net_protein_grams": 662.0,
            "cost_per_gram_clp": 75.5,
        }
        self.fake_deal = {
            "source": "Tienda Y",
            "category": "whey",
            "title": "Whey Inflada Pre-Cyber 5 Lb",
            "price": 95000,
            "original_price": 125000,
            "discount_pct": 24.0,
            "weight_grams": 2268.0,
            "net_protein_grams": 1655.0,
            "cost_per_gram_clp": 57.4,
        }
        self.good_casein = {
            "source": "Winkler",
            "category": "casein",
            "title": "Caseína Micelar 1 kg",
            "price": 42990,
            "original_price": None,
            "discount_pct": 0.0,
            "weight_grams": 1000.0,
            "net_protein_grams": 760.0,
            "cost_per_gram_clp": 56.57,
        }

    def test_calculate_value_score(self):
        score_good = calculate_value_score(self.exceptional_whey)
        score_bad = calculate_value_score(self.overpriced_whey)
        self.assertTrue(score_good > 75, f"Expected >75 but got {score_good}")
        self.assertTrue(score_bad < 45, f"Expected <45 but got {score_bad}")

    def test_generate_verdict_immediate_buy(self):
        verdict = generate_verdict(self.exceptional_whey)
        self.assertIn(verdict["status"], ["COMPRA_INMEDIATA", "BUENA_OPCION"])
        self.assertIn("badge", verdict)
        self.assertIn("reason", verdict)

    def test_generate_verdict_fake_or_overpriced(self):
        verdict_fake = generate_verdict(self.fake_deal)
        self.assertIn(verdict_fake["status"], ["INFLADO", "NO_CONVIENE"])

        verdict_overpriced = generate_verdict(self.overpriced_whey)
        self.assertEqual(verdict_overpriced["status"], "NO_CONVIENE")

    def test_build_optimal_basket(self):
        products = [self.exceptional_whey, self.overpriced_whey, self.good_casein]
        basket = build_optimal_basket(products, target_months=3)
        self.assertEqual(basket["target_months"], 3)
        self.assertTrue(basket["total_cost_clp"] > 0)
        self.assertTrue(basket["total_protein_grams"] > 0)
        self.assertTrue(basket["avg_cost_per_gram_clp"] < 50.0)
        # Should pick exceptional whey and good casein
        roles = [item["role"] for item in basket["items"]]
        self.assertEqual(len(roles), 2)

    def test_generate_market_insights(self):
        products = [self.exceptional_whey, self.overpriced_whey, self.good_casein]
        insights = generate_market_insights(products)
        self.assertIn("avg_costs", insights)
        self.assertIn("best_picks", insights)
        self.assertIn("casein_tactical_advice", insights)
        self.assertIn("store_rankings", insights)
        self.assertTrue(insights["avg_costs"]["whey"] > 0)


if __name__ == "__main__":
    unittest.main()
