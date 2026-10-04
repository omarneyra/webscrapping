import unittest
from app.analytics import (
    detect_brand,
    get_brand_trust_data,
    calculate_value_score,
    generate_verdict,
    build_optimal_basket,
    generate_market_insights,
)


class TestAnalytics(unittest.TestCase):

    def test_detect_brand(self):
        self.assertEqual(detect_brand("Gold Standard 100% Whey 5 lbs"), "optimum nutrition")
        self.assertEqual(detect_brand("Dymatize ISO 100 5 Lbs"), "dymatize")
        self.assertEqual(detect_brand("Mutant Whey 5 Lbs"), "mutant")
        self.assertEqual(detect_brand("BioTechUSA Micellar Casein 2.2kg"), "biotechusa")
        self.assertEqual(detect_brand("Winkler Nutrition Whey 2kg"), "winkler nutrition")
        self.assertEqual(detect_brand("Proteina Desconocida 1kg"), "default")

    def test_brand_trust_tiers(self):
        on_trust = get_brand_trust_data("Optimum Nutrition Gold Standard")
        self.assertEqual(on_trust["tier"], "Tier S")
        self.assertGreaterEqual(on_trust["trust_score"], 95)

        mutant_trust = get_brand_trust_data("Mutant Whey")
        self.assertEqual(mutant_trust["tier"], "Tier A")

        winkler_trust = get_brand_trust_data("Winkler Nutrition 2kg")
        self.assertEqual(winkler_trust["tier"], "Tier B")

        fit_trust = get_brand_trust_data("Fit Protein 4.4 lbs")
        self.assertEqual(fit_trust["tier"], "Tier C")
        self.assertEqual(fit_trust["spiking_risk"], "Alto")

    def test_calculate_value_score(self):
        # Producto excelente con marca auditada
        good_product = {
            "title": "Mutant Whey 5 lbs",
            "category": "whey",
            "price": 56990.0,
            "cost_per_gram_clp": 34.42,
            "discount_pct": 25.0,
            "weight_grams": 2268.0,
        }
        score_good = calculate_value_score(good_product)
        self.assertGreaterEqual(score_good, 75)

        # Producto caro sobrevalorado
        bad_product = {
            "title": "Proteina Cara Tier C 908g",
            "category": "whey",
            "price": 60000.0,
            "cost_per_gram_clp": 90.5,
            "discount_pct": 0.0,
            "weight_grams": 908.0,
        }
        score_bad = calculate_value_score(bad_product)
        self.assertLess(score_bad, 50)

    def test_generate_verdict(self):
        # Caso Ganga Certificada
        deal = {
            "title": "Optimum Nutrition Gold Standard 5 lbs",
            "category": "whey",
            "price": 55000.0,
            "cost_per_gram_clp": 33.2,
            "discount_pct": 30.0,
            "weight_grams": 2268.0,
        }
        verdict = generate_verdict(deal)
        self.assertEqual(verdict["status"], "COMPRA_INMEDIATA")
        self.assertEqual(verdict["badge_color"], "emerald")

        # Caso sospechosa barata Tier C (riesgo amino spiking)
        suspicious = {
            "title": "Fit Protein 4.4 lbs Vainilla",
            "category": "whey",
            "price": 32990.0,
            "cost_per_gram_clp": 22.64,
            "discount_pct": 10.0,
            "weight_grams": 2000.0,
        }
        verdict_susp = generate_verdict(suspicious)
        self.assertEqual(verdict_susp["status"], "PRECAUCION_MARCA")
        self.assertEqual(verdict_susp["badge_color"], "amber")

    def test_build_optimal_basket(self):
        products = [
            {
                "title": "Mutant Whey 5 lbs",
                "category": "whey",
                "price": 56990.0,
                "cost_per_gram_clp": 34.42,
                "discount_pct": 25.0,
                "weight_grams": 2268.0,
                "net_protein_grams": 1655.6,
            },
            {
                "title": "BioTechUSA Casein 2.27 kg",
                "category": "casein",
                "price": 85990.0,
                "cost_per_gram_clp": 49.84,
                "discount_pct": 15.0,
                "weight_grams": 2270.0,
                "net_protein_grams": 1725.2,
            },
            {
                "title": "Fit Protein 4.4 lbs Barata",
                "category": "whey",
                "price": 30000.0,
                "cost_per_gram_clp": 20.0,
                "discount_pct": 5.0,
                "weight_grams": 2000.0,
                "net_protein_grams": 1500.0,
            },
        ]

        basket = build_optimal_basket(products, target_months=3)
        self.assertEqual(basket["target_months"], 3)
        self.assertEqual(len(basket["items"]), 2)
        # Debe haber elegido Mutant Whey (Tier A) y no Fit Protein (Tier C)
        whey_item = [it for it in basket["items"] if "Whey" in it["role"]][0]
        self.assertIn("Mutant", whey_item["product"]["title"])
        self.assertGreater(basket["total_cost_clp"], 0)
        self.assertGreater(basket["total_protein_grams"], 0)

    def test_generate_market_insights(self):
        products = [
            {
                "title": "Mutant Whey 5 lbs",
                "category": "whey",
                "price": 56990.0,
                "cost_per_gram_clp": 34.42,
                "discount_pct": 25.0,
                "weight_grams": 2268.0,
            },
            {
                "title": "BioTechUSA Casein 2.27 kg",
                "category": "casein",
                "price": 85990.0,
                "cost_per_gram_clp": 49.84,
                "discount_pct": 15.0,
                "weight_grams": 2270.0,
            },
        ]
        insights = generate_market_insights(products)
        self.assertIn("avg_costs", insights)
        self.assertIn("best_picks", insights)
        self.assertEqual(insights["avg_costs"]["whey"], 34.42)
        self.assertEqual(insights["avg_costs"]["casein"], 49.84)


if __name__ == "__main__":
    unittest.main()
