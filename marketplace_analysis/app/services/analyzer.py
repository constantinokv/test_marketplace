# app/services/analyzer.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class ProductAnalyzer:
    def __init__(self):
        self.price_scaler = MinMaxScaler()
        
    def load_data(self, file_path):
        """Cargar y realizar limpieza inicial de datos"""
        self.df = pd.read_csv(file_path)
        print("Columnas disponibles:", self.df.columns.tolist())  # Para debug
        return self.df
    
    def clean_text(self, text):
        """Limpieza básica de texto"""
        if pd.isna(text):
            return ""
        text = str(text).lower().strip()
        return text
    
    def normalize_features(self):
        """Normalizar características numéricas"""
        # Normalizar precio
        self.df['price_normalized'] = self.price_scaler.fit_transform(
            self.df[['price']].values
        )
        
        # Normalizar otros campos numéricos si existen
        for col in ['rating', 'reviews_count', 'sales_last_30_days']:
            if col in self.df.columns:
                self.df[f'{col}_normalized'] = self.price_scaler.fit_transform(
                    self.df[[col]].values
                )
        return self.df
    
    def extract_features(self):
        """Extraer características adicionales"""
        # Procesar título
        self.df['title_clean'] = self.df['title'].apply(self.clean_text)
        
        # Procesar descripción si existe
        if 'description' in self.df.columns:
            self.df['description_clean'] = self.df['description'].apply(self.clean_text)
        
        # Extraer categoría principal
        self.df['main_category'] = self.df['category'].apply(
            lambda x: x.split('/')[0] if pd.notna(x) else "Unknown"
        )
        
        return self.df

    def calculate_product_score(self):
        """Calcular puntuación del producto basada en múltiples factores"""
        # Inicializar score con precio normalizado
        self.df['product_score'] = self.df['price_normalized']
        
        # Añadir otros factores si están disponibles
        if 'rating' in self.df.columns:
            self.df['product_score'] += self.df['rating_normalized'] * 0.3
            
        if 'reviews_count' in self.df.columns:
            self.df['product_score'] += self.df['reviews_count_normalized'] * 0.2
            
        if 'sales_last_30_days' in self.df.columns:
            self.df['product_score'] += self.df['sales_last_30_days_normalized'] * 0.2
            
        return self.df