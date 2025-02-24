import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from typing import Dict, List, Optional
import pickle
import os
import logging

# Configurar logging con más detalle
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductRecommender:
    def __init__(self):
        """Inicializar el sistema de recomendación"""
        logger.info("Inicializando sistema de recomendación")
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.similarity_matrix = None
        self.feature_matrix = None  # Cambiado de product_features
        self.tfidf_matrix = None    # Agregado para mantener la matriz TF-IDF
        self.product_indices = {}
        self.inverse_indices = {}
        self.df = None
        self.model_data = {}

    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Obtener información de un producto por su ID"""
        try:
            if product_id not in self.product_indices:
                logger.warning(f"Producto {product_id} no encontrado")
                return None
                
            product_info = self.df.loc[self.df['product_id'] == product_id].iloc[0]
            
            return {
                "product_id": int(product_id),
                "title": str(product_info["title"]),
                "price": float(product_info["price"]),
                "rating": float(product_info.get("rating", 0)),
                "category": str(product_info["category"]),                           
                "reviews_count": int(product_info.get("reviews_count", 0))
            }
        except Exception as e:
            logger.error(f"Error al obtener producto {product_id}: {str(e)}")
            return None
        
    def _preprocess_text(self, text):
        """Preprocesar texto para TF-IDF"""
        if not isinstance(text, str):
            return ""
        return text.lower().strip()

    def fit(self, df):
        """Entrenar el sistema de recomendaciones"""
        logger.info("Iniciando entrenamiento del sistema de recomendaciones")
        
        try:
            # Validar datos de entrada
            required_columns = ['product_id', 'title', 'category', 'price', 'rating', 'reviews_count']
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"DataFrame debe contener las columnas: {required_columns}")

            # Guardar el DataFrame
            self.df = df.copy()
            logger.info(f"DataFrame cargado con {len(df)} registros")
            
            # Crear mapeo de índices
            self.product_indices = {pid: idx for idx, pid in enumerate(df['product_id'])}
            self.inverse_indices = {idx: pid for pid, idx in self.product_indices.items()}
            logger.info(f"Índices creados para {len(self.product_indices)} productos")
            
            # Preparar características textuales
            text_features = df.apply(
                lambda row: ' '.join([
                    self._preprocess_text(str(row['title'])),
                    self._preprocess_text(str(row.get('description', ''))),
                    self._preprocess_text(str(row['category']))
                ]),
                axis=1
            )
            logger.info("Características textuales preparadas")
            
            # Crear matriz TF-IDF
            self.tfidf_matrix = self.tfidf.fit_transform(text_features)
            logger.info(f"Matriz TF-IDF creada con forma {self.tfidf_matrix.shape}")
            
            # Preparar características numéricas
            numeric_features = []
            
            # Normalizar características numéricas básicas
            scaler = MinMaxScaler()
            
            # Normalizar precio
            if 'price' in df.columns:
                df['price_normalized'] = scaler.fit_transform(df[['price']].fillna(0))
                numeric_features.append('price_normalized')
                
            # Normalizar rating
            if 'rating' in df.columns:
                df['rating_normalized'] = scaler.fit_transform(df[['rating']].fillna(0))
                numeric_features.append('rating_normalized')
                
            # Normalizar reviews_count
            if 'reviews_count' in df.columns:
                df['reviews_count_normalized'] = scaler.fit_transform(df[['reviews_count']].fillna(0))
                numeric_features.append('reviews_count_normalized')
                
            # Normalizar características adicionales si existen
            additional_features = [
                'sales_last_30_days',
                'stock',
                'seller_rating',
                'shipping_time_days'
            ]
            
            for feature in additional_features:
                if feature in df.columns:
                    normalized_name = f"{feature}_normalized"
                    df[normalized_name] = scaler.fit_transform(df[[feature]].fillna(0))
                    numeric_features.append(normalized_name)
            
            logger.info(f"Características numéricas normalizadas: {numeric_features}")
            
            # Combinar características
            if numeric_features:
                numeric_matrix = df[numeric_features].fillna(0).values
                self.feature_matrix = np.hstack((
                    self.tfidf_matrix.toarray(),
                    numeric_matrix
                ))
                logger.info(f"Matriz de características combinada: {self.feature_matrix.shape}")
            else:
                logger.warning("No se encontraron características numéricas. Usando solo TF-IDF.")
                self.feature_matrix = self.tfidf_matrix.toarray()
            
            # Calcular matriz de similitud
            logger.info("Calculando matriz de similitud")
            self.similarity_matrix = cosine_similarity(self.feature_matrix)
            logger.info(f"Matriz de similitud calculada: {self.similarity_matrix.shape}")
            
            # Guardar datos del modelo
            self.model_data = {
                'df': self.df,
                'product_indices': self.product_indices,
                'inverse_indices': self.inverse_indices,
                'similarity_matrix': self.similarity_matrix,
                'feature_matrix': self.feature_matrix,
                'tfidf': self.tfidf
            }
            
            logger.info("Entrenamiento completado exitosamente")
            return self
            
        except Exception as e:
            logger.error(f"Error durante el entrenamiento: {str(e)}")
            raise
    
    def get_recommendations(self, product_id: int, n_recommendations: int = 5) -> Dict:
        """Obtener recomendaciones para un producto"""
        logger.info(f"Obteniendo recomendaciones para el producto {product_id}")
        
        if self.df is None:
            raise ValueError("El modelo no ha sido entrenado")
            
        if product_id not in self.product_indices:
            raise ValueError(f"Producto {product_id} no encontrado")
            
        # Obtener información del producto original
        product_info = self.get_product_by_id(product_id)
        if not product_info:
            raise ValueError(f"No se pudo obtener información del producto {product_id}")
        
        idx = self.product_indices[product_id]
        similarity_scores = list(enumerate(self.similarity_matrix[idx]))
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        recommendations = similarity_scores[1:n_recommendations+1]
        
        recommended_products = []
        for rec in recommendations:
            rec_id = self.inverse_indices[rec[0]]
            rec_info = self.get_product_by_id(rec_id)
            if rec_info:
                recommended_products.append({
                    'product_id': int(rec_info['product_id']),
                    'title': str(rec_info['title']),
                    'category': str(rec_info['category']),
                    'price': float(rec_info['price']),
                    'rating': float(rec_info['rating']),
                    'reviews_count': int(rec_info['reviews_count']),
                    'similarity_score': float(rec[1])
                })
        
        return {
            'product_id': int(product_info['product_id']),
            'title': str(product_info['title']),
            'category': str(product_info['category']),
            'recommendations': recommended_products
        }
    
    def save_model(self, filepath):
        """Guardar modelo entrenado"""
        logger.info(f"Guardando modelo en {filepath}")
        if not self.model_data:
            raise ValueError("No hay modelo para guardar")
        
        with open(filepath, 'wb') as f:
            pickle.dump(self.model_data, f)
        logger.info("Modelo guardado exitosamente")
    
    @classmethod
    def load_model(cls, filepath):
        """Cargar modelo guardado"""
        logger.info(f"Cargando modelo desde {filepath}")
        instance = cls()
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        instance.df = model_data['df']
        instance.product_indices = model_data['product_indices']
        instance.inverse_indices = model_data['inverse_indices']
        instance.similarity_matrix = model_data['similarity_matrix']
        instance.feature_matrix = model_data['feature_matrix']  # Cambiado de product_features
        instance.tfidf = model_data['tfidf']
        instance.model_data = model_data
        
        logger.info("Modelo cargado exitosamente")
        return instance

    def get_similar_products(self, product_id: int, by_category: bool = True, n_recommendations: int = 5) -> Dict:
        """Obtener productos similares con filtro opcional por categoría"""
        logger.info(f"Obteniendo productos similares para {product_id}")
        
        if self.df is None:
            raise ValueError("El modelo no ha sido entrenado")
            
        # Obtener información del producto original
        product_info = self.get_product_by_id(product_id)
        if not product_info:
            raise ValueError(f"No se pudo obtener información del producto {product_id}")
            
        recommendations = self.get_recommendations(product_id, n_recommendations * 2)
        
        if by_category:
            filtered_recommendations = [
                rec for rec in recommendations['recommendations']
                if rec['category'] == product_info['category']
            ]
            recommendations['recommendations'] = filtered_recommendations[:n_recommendations]
        else:
            recommendations['recommendations'] = recommendations['recommendations'][:n_recommendations]
        
        return recommendations