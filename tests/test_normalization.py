import unittest
from app.normalization import (
    extract_weight_grams,
    calculate_discount,
    detect_protein_category,
    calculate_cost_per_gram,
    is_valid_powder_supplement,
    parse_clean_price,
    estimate_protein_grams,
    normalize_product_record,
)


class TestNormalization(unittest.TestCase):

    def test_extract_weight_grams(self):
        self.assertAlmostEqual(extract_weight_grams("Whey Gold Standard 5 lbs Vainilla"), 2268.0, places=1)
        self.assertAlmostEqual(extract_weight_grams("Dymatize Elite Casein 4lb Chocolate"), 1814.4, places=1)
        self.assertEqual(extract_weight_grams("Winkler Whey 2 kg Frutilla"), 2000.0)
        self.assertEqual(extract_weight_grams("Iso 100 Dymatize 908g"), 908.0)
        self.assertEqual(extract_weight_grams("100% Whey Protein Professional 2.350 g Scitec"), 2350.0)
        self.assertIsNone(extract_weight_grams("Shaker Negro 500ml"))
        self.assertIsNone(extract_weight_grams("Sachet 30g"))

    def test_calculate_discount(self):
        self.assertEqual(calculate_discount(50000.0, 40000.0), 20.0)
        self.assertEqual(calculate_discount(None, 40000.0), 0.0)
        self.assertEqual(calculate_discount(40000.0, 40000.0), 0.0)

    def test_detect_protein_category(self):
        self.assertEqual(detect_protein_category("Gold Standard 100% Casein"), "casein")
        self.assertEqual(detect_protein_category("Dymatize ISO 100"), "isolate")
        self.assertEqual(detect_protein_category("Mutant Whey 5 lbs"), "whey")
        self.assertEqual(detect_protein_category("Creatina Monohidratada"), "default")

    def test_is_valid_powder_supplement(self):
        self.assertTrue(is_valid_powder_supplement("Whey Protein 5 lbs"))
        self.assertTrue(is_valid_powder_supplement("Dymatize Elite Casein 4 lbs"))
        self.assertFalse(is_valid_powder_supplement("Shaker 400ml - Women Whey"))
        self.assertFalse(is_valid_powder_supplement("Protein Water - Bebida líquida 500ml"))
        self.assertFalse(is_valid_powder_supplement("Barra de proteina 60g"))
        self.assertFalse(is_valid_powder_supplement("Creatina Creapure 300g"))

    def test_parse_clean_price(self):
        self.assertEqual(parse_clean_price("$ 42.990"), 42990.0)
        self.assertEqual(parse_clean_price("$42990"), 42990.0)
        self.assertEqual(parse_clean_price("59.990 CLP"), 59990.0)
        self.assertIsNone(parse_clean_price("Agotado"))

    def test_estimate_protein_grams(self):
        # 1000g de whey -> ~730g proteina
        self.assertEqual(estimate_protein_grams(1000.0, "whey"), 730.0)
        # 1000g de isolate -> ~860g proteina
        self.assertEqual(estimate_protein_grams(1000.0, "isolate"), 860.0)
        # 1000g de caseina -> ~760g proteina
        self.assertEqual(estimate_protein_grams(1000.0, "casein"), 760.0)

    def test_calculate_cost_per_gram(self):
        cost = calculate_cost_per_gram(50000.0, 1655.6)
        self.assertAlmostEqual(cost, 30.20, places=2)
        self.assertIsNone(calculate_cost_per_gram(50000.0, 0))

    def test_normalize_product_record(self):
        rec = normalize_product_record(
            source="TestStore",
            title="Gold Standard Whey 5 lbs Vainilla",
            price=60000.0,
            original_price=80000.0,
            permalink="https://test.cl/gs5",
        )
        self.assertEqual(rec["source"], "TestStore")
        self.assertEqual(rec["category"], "whey")
        self.assertAlmostEqual(rec["weight_grams"], 2268.0, places=1)
        self.assertEqual(rec["discount_pct"], 25.0)
        self.assertIsNotNone(rec["cost_per_gram_clp"])


if __name__ == "__main__":
    unittest.main()
