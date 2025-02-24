import unittest
import pandas as pd
from app.services.recommender import ProductRecommender
from app.services.analyzer import ProductAnalyzer

class TestProductRecommender(unittest.TestCase):
    def setUp(self):
        """Preparar datos para cada test"""
        # Preparar datos procesados para el recomendador
        self.analyzer = ProductAnalyzer()
        self.df = self.analyzer.load_data('data/raw/products.csv')
        self.df = self.analyzer.extract_features()
        self.df = self.analyzer.normalize_features()
        
        self.recommender = ProductRecommender()
        
    def test_model_training(self):
        """Probar que el modelo se entrena correctamente"""
        self.recommender.fit(self.df)
        self.assertIsNotNone(self.recommender.similarity_matrix)
        self.assertIsNotNone(self.recommender.df)
        self.assertTrue(len(self.recommender.product_indices) > 0)
        
    def test_recommendations(self):
        """Probar que se generan recomendaciones"""
        self.recommender.fit(self.df)
        first_product_id = self.df['product_id'].iloc[0]
        response = self.recommender.get_recommendations(first_product_id)
        
        # Verificar estructura de respuesta
        self.assertIn('product_id', response)
        self.assertIn('product_title', response)
        self.assertIn('product_category', response)
        self.assertIn('recommendations', response)
        
        # Verificar que el producto original es correcto
        self.assertEqual(response['product_id'], first_product_id)
        self.assertEqual(
            response['product_title'],
            self.df[self.df['product_id'] == first_product_id]['title'].iloc[0]
        )
        
        # Verificar recomendaciones
        recommendations = response['recommendations']
        self.assertEqual(len(recommendations), 5)
        
        for rec in recommendations:
            # Verificar estructura de cada recomendación
            self.assertIn('product_id', rec)
            self.assertIn('title', rec)
            self.assertIn('price', rec)
            self.assertIn('rating', rec)
            self.assertIn('category', rec)
            self.assertIn('reviews_count', rec)
            self.assertIn('similarity_score', rec)
            
            # Verificar tipos de datos
            self.assertIsInstance(rec['product_id'], int)
            self.assertIsInstance(rec['title'], str)
            self.assertIsInstance(rec['price'], float)
            self.assertIsInstance(rec['rating'], float)
            self.assertIsInstance(rec['category'], str)
            self.assertIsInstance(rec['reviews_count'], int)
            self.assertIsInstance(rec['similarity_score'], float)
            
            # Verificar que no recomienda el mismo producto
            self.assertNotEqual(rec['product_id'], first_product_id)
            
            # Verificar rangos válidos
            self.assertGreater(rec['similarity_score'], 0)
            self.assertLessEqual(rec['similarity_score'], 1)
            self.assertGreaterEqual(rec['rating'], 0)
            self.assertGreaterEqual(rec['price'], 0)
            self.assertGreaterEqual(rec['reviews_count'], 0)
            
    def test_similar_products_by_category(self):
        """Probar recomendaciones filtradas por categoría"""
        self.recommender.fit(self.df)
        first_product_id = self.df['product_id'].iloc[0]
        response = self.recommender.get_similar_products(
            first_product_id, 
            by_category=True
        )
        
        # Verificar estructura de respuesta
        self.assertIn('product_id', response)
        self.assertIn('product_title', response)
        self.assertIn('product_category', response)
        self.assertIn('recommendations', response)
        
        # Obtener categoría del producto original
        product_category = self.df[
            self.df['product_id'] == first_product_id
        ]['category'].iloc[0]
        
        # Verificar que las recomendaciones son de la misma categoría
        for rec in response['recommendations']:
            self.assertEqual(rec['category'], product_category)
            
    def test_invalid_product_id(self):
        """Probar manejo de ID de producto inválido"""
        self.recommender.fit(self.df)
        invalid_id = 999999  # ID que no existe
        
        with self.assertRaises(ValueError):
            self.recommender.get_recommendations(invalid_id)
            
    def test_model_persistence(self):
        """Probar guardado y carga del modelo"""
        import tempfile
        import os
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            # Entrenar y guardar modelo
            self.recommender.fit(self.df)
            self.recommender.save_model(tmp.name)
            
            # Cargar modelo en nueva instancia
            loaded_recommender = ProductRecommender.load_model(tmp.name)
            
            # Verificar que el modelo cargado funciona
            first_product_id = self.df['product_id'].iloc[0]
            recommendations = loaded_recommender.get_recommendations(first_product_id)
            
            self.assertIsNotNone(recommendations)
            self.assertIn('recommendations', recommendations)
            
        # Limpiar archivo temporal
        os.unlink(tmp.name)

if __name__ == '__main__':
    unittest.main()