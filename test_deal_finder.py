import unittest
from deal_finder import (
    extract_weight_grams,
    calculate_discount,
    detect_protein_category,
    calculate_cost_per_gram,
    is_valid_powder_supplement,
    parse_vtex_product,
    parse_shopify_suggest_item,
    filter_and_rank_deals,
)


class TestDealFinder(unittest.TestCase):

    def test_extract_weight_grams(self):
        self.assertAlmostEqual(extract_weight_grams("Whey Gold Standard 5 lbs Vainilla"), 2268.0, places=1)
        self.assertAlmostEqual(extract_weight_grams("Dymatize Elite Casein 4lb Chocolate"), 1814.4, places=1)
        self.assertEqual(extract_weight_grams("Winkler Whey 2 kg Frutilla"), 2000.0)
        self.assertEqual(extract_weight_grams("Iso 100 Dymatize 908g"), 908.0)
        self.assertIsNone(extract_weight_grams("Shaker Negro"))

    def test_calculate_discount(self):
        self.assertEqual(calculate_discount(50000.0, 40000.0), 20.0)
        self.assertEqual(calculate_discount(None, 40000.0), 0.0)
        self.assertEqual(calculate_discount(40000.0, 40000.0), 0.0)

    def test_detect_protein_category(self):
        self.assertEqual(detect_protein_category("Gold Standard 100% Casein"), "casein")
        self.assertEqual(detect_protein_category("Dymatize ISO 100"), "isolate")
        self.assertEqual(detect_protein_category("Mutant Whey 5 lbs"), "whey")
        self.assertEqual(detect_protein_category("Creatina"), "default")

    def test_is_valid_powder_supplement(self):
        self.assertTrue(is_valid_powder_supplement("Whey Protein 5 lbs"))
        self.assertTrue(is_valid_powder_supplement("Dymatize Elite Casein 4 lbs"))
        self.assertFalse(is_valid_powder_supplement("Shaker 400ml - Women Whey"))
        self.assertFalse(is_valid_powder_supplement("Protein Water - Bebida líquida 500ml"))
        self.assertFalse(is_valid_powder_supplement("Barra de proteina 60g"))

    def test_calculate_cost_per_gram(self):
        cost = calculate_cost_per_gram(50000.0, 1655.6)
        self.assertAlmostEqual(cost, 30.20, places=2)
        self.assertIsNone(calculate_cost_per_gram(50000.0, 0))

    def test_parse_vtex_product(self):
        raw_product = {
            "productName": "Whey Protein 2lbs - Ghost",
            "link": "https://supletech.cl/whey-ghost/p",
            "items": [
                {
                    "nameComplete": "Whey Protein 2lbs Cereal Milk - Ghost",
                    "sellers": [
                        {
                            "commertialOffer": {
                                "Price": 34990.0,
                                "ListPrice": 58990.0,
                                "AvailableQuantity": 5,
                            }
                        }
                    ],
                }
            ],
        }
        items = parse_vtex_product(raw_product, "Supletech")
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["source"], "Supletech")
        self.assertEqual(item["category"], "whey")
        self.assertAlmostEqual(item["discount_pct"], 40.7, places=1)
        self.assertAlmostEqual(item["weight_grams"], 907.2, places=1)
        self.assertTrue(item["cost_per_gram_clp"] > 0)

    def test_parse_shopify_suggest_item(self):
        raw_item = {
            "title": "Gold Standard, Optimum Nutrition Whey Protein 5 Lb, Original",
            "price": "97190",
            "compare_at_price": "119990",
            "url": "/products/100-whey-protein-5lb-gold-standard",
        }
        item = parse_shopify_suggest_item(raw_item, "All Nutrition", "https://allnutrition.cl")
        self.assertIsNotNone(item)
        self.assertEqual(item["source"], "All Nutrition")
        self.assertEqual(item["category"], "whey")
        self.assertAlmostEqual(item["weight_grams"], 2268.0, places=1)
        self.assertAlmostEqual(item["discount_pct"], 19.0, places=1)
        self.assertTrue(item["cost_per_gram_clp"] > 0)

    def test_filter_and_rank_deals(self):
        products = [
            {"source": "S1", "title": "Creatina", "category": "default", "price": 25000, "discount_pct": 0, "cost_per_gram_clp": None},
            {"source": "S1", "title": "Whey Caro", "category": "whey", "price": 60000, "discount_pct": 5.0, "cost_per_gram_clp": 45.0},
            {"source": "S2", "title": "Whey Bueno", "category": "whey", "price": 38000, "discount_pct": 30.0, "cost_per_gram_clp": 22.5},
            {"source": "S3", "title": "Casein Ganga", "category": "casein", "price": 42000, "discount_pct": 20.0, "cost_per_gram_clp": 27.8},
        ]
        ranked = filter_and_rank_deals(products, target_categories=["whey", "casein"], max_cost_per_gram=35.0)
        self.assertEqual(len(ranked), 2)
        self.assertEqual(ranked[0]["title"], "Whey Bueno")
        self.assertEqual(ranked[1]["title"], "Casein Ganga")


if __name__ == "__main__":
    unittest.main()
