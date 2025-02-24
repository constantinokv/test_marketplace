import unittest
import pandas as pd
from app.services.analyzer import ProductAnalyzer

class TestProductAnalyzer(unittest.TestCase):
    def setUp(self):
        """Se ejecuta antes de cada test"""
        self.analyzer = ProductAnalyzer()
        self.df = self.analyzer.load_data('data/raw/products.csv')

    def test_data_loading(self):
        """Probar que los datos se cargan correctamente"""
        self.assertIsNotNone(self.df)
        self.assertGreater(len(self.df), 0)
        
    def test_feature_extraction(self):
        """Probar la extracción de características"""
        processed_df = self.analyzer.extract_features()
        self.assertIn('title_clean', processed_df.columns)
        self.assertIn('main_category', processed_df.columns)

    def test_normalization(self):
        """Probar la normalización de características"""
        normalized_df = self.analyzer.normalize_features()
        self.assertIn('price_normalized', normalized_df.columns)
        self.assertTrue(all(normalized_df['price_normalized'].between(0, 1)))

if __name__ == '__main__':
    unittest.main()