import unittest
from analytics import (
    calculate_value_score,
    generate_verdict,
    build_optimal_basket,
    generate_market_insights,
    get_market_benchmark,
    detect_brand,
    get_brand_trust_data,
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
            "title": "Caseína Micelar Winkler 1 kg",
            "price": 42990,
            "original_price": None,
            "discount_pct": 0.0,
            "weight_grams": 1000.0,
            "net_protein_grams": 760.0,
            "cost_per_gram_clp": 56.57,
        }
        self.suspicious_cheap = {
            "source": "Tienda Z",
            "category": "whey",
            "title": "Fit Protein 100% Whey 4.4 lbs",
            "price": 32990,
            "original_price": None,
            "discount_pct": 0.0,
            "weight_grams": 2000.0,
            "net_protein_grams": 1460.0,
            "cost_per_gram_clp": 22.5,
        }

    def test_detect_brand(self):
        self.assertEqual(detect_brand("Optimum Nutrition Gold Standard 5 lbs"), "optimum nutrition")
        self.assertEqual(detect_brand("Dymatize ISO 100 Gourmet"), "dymatize")
        self.assertEqual(detect_brand("Mutant Whey 5 Lb"), "mutant")
        self.assertEqual(detect_brand("BioTechUSA Micellar Casein"), "biotechusa")
        self.assertEqual(detect_brand("Winkler Nutrition Caseína"), "winkler nutrition")
        self.assertEqual(detect_brand("Fit Protein 100% Whey"), "fit protein")

    def test_get_brand_trust_data(self):
        on_trust = get_brand_trust_data("Optimum Nutrition Gold Standard")
        self.assertEqual(on_trust["tier"], "Tier S")
        self.assertEqual(on_trust["spiking_risk"], "Nulo")

        fit_trust = get_brand_trust_data("Fit Protein 100% Whey")
        self.assertEqual(fit_trust["tier"], "Tier C")
        self.assertEqual(fit_trust["spiking_risk"], "Alto")

    def test_calculate_value_score_brand_penalty(self):
        # A certified brand (Mutant, Tier A) should get strong score
        score_mutant = calculate_value_score(self.exceptional_whey)
        self.assertTrue(score_mutant >= 80, f"Expected >= 80, got {score_mutant}")

    def test_generate_verdict_immediate_buy(self):
        verdict = generate_verdict(self.exceptional_whey)
        self.assertEqual(verdict["status"], "COMPRA_INMEDIATA")
        self.assertIn("Tier A", verdict["badge"])

    def test_generate_verdict_suspicious_brand(self):
        verdict = generate_verdict(self.suspicious_cheap)
        self.assertEqual(verdict["status"], "PRECAUCION_MARCA")
        self.assertIn("Sin Certificación", verdict["badge"])

    def test_generate_verdict_fake_or_overpriced(self):
        verdict_fake = generate_verdict(self.fake_deal)
        self.assertEqual(verdict_fake["status"], "INFLADO")

        verdict_overpriced = generate_verdict(self.overpriced_whey)
        self.assertEqual(verdict_overpriced["status"], "NO_CONVIENE")

    def test_build_optimal_basket(self):
        products = [self.exceptional_whey, self.overpriced_whey, self.good_casein, self.suspicious_cheap]
        basket = build_optimal_basket(products, target_months=3)
        self.assertEqual(basket["target_months"], 3)
        self.assertTrue(basket["total_cost_clp"] > 0)
        # Basket should prioritize verified brands (Mutant + Winkler) over unverified Fit Protein
        roles = [item["role"] for item in basket["items"]]
        self.assertEqual(len(roles), 2)
        whey_trust = basket["items"][0]["trust"]
        self.assertIn(whey_trust["tier"], ["Tier S", "Tier A", "Tier B"])

    def test_generate_market_insights(self):
        products = [self.exceptional_whey, self.overpriced_whey, self.good_casein]
        insights = generate_market_insights(products)
        self.assertIn("avg_costs", insights)
        self.assertIn("best_picks", insights)
        self.assertIn("casein_tactical_advice", insights)
        self.assertIn("tier_counts", insights)


if __name__ == "__main__":
    unittest.main()
