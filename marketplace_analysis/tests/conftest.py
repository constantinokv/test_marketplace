import pytest
from fastapi.testclient import TestClient   
import logging
import os
from pathlib import Path
from app.api.routes import app
from app.services.analyzer import ProductAnalyzer
from app.services.recommender import ProductRecommender

# Configuraciones
MODEL_PATH = Path('models/trained/recommender.pkl')
DATA_PATH = Path('data/raw/products.csv')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def client():
    """Cliente de pruebas para la API"""
    return TestClient(app)

@pytest.fixture(scope="session")
def auth_headers():
    """Headers de autenticación para las pruebas"""
    return {"Authorization": "Bearer test-token"}

@pytest.fixture(scope="session")
def test_data_path():
    """Ruta al archivo de datos de prueba"""
    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'data', 
        'raw', 
        'products.csv'
    )
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Archivo de datos no encontrado: {csv_path}")
    return csv_path

@pytest.fixture(scope="session")
def analyzer():
    """Instancia del analizador de productos"""
    return ProductAnalyzer()

@pytest.fixture(scope="session")
def setup_test_recommender(client, test_data_path, analyzer):
    """Configurar el recomendador con datos reales de prueba"""
    logger.info("Configurando el recomendador con datos reales de prueba")
    
    try:
        # Cargar y procesar datos
        df = analyzer.load_data(test_data_path)
        df = analyzer.extract_features()
        df = analyzer.normalize_features()
        
        # Inicializar y entrenar recomendador
        recommender = ProductRecommender()
        recommender.fit(df)
        
        # Verificar inicialización correcta
        if not hasattr(recommender, 'product_indices'):
            raise ValueError("Recomendador no inicializado correctamente: falta product_indices")
        if not hasattr(recommender, 'similarity_matrix'):
            raise ValueError("Recomendador no inicializado correctamente: falta similarity_matrix")
        if len(recommender.product_indices) == 0:
            raise ValueError("Recomendador no tiene productos en el índice")
        
        # Guardar en el estado de la aplicación
        app.state.recommender = recommender
        logger.info("Recomendador configurado exitosamente")
        
        # Guardar modelo si se requiere
        if not MODEL_PATH.parent.exists():
            os.makedirs(MODEL_PATH.parent, exist_ok=True)
            recommender.save_model(MODEL_PATH)
            logger.info(f"Modelo guardado en {MODEL_PATH}")
        
        return recommender
        
    except Exception as e:
        logger.error(f"Error en setup_test_recommender: {str(e)}")
        raise

@pytest.fixture(scope="session")
def test_product_id(setup_test_recommender):
    """ID de producto válido para pruebas"""
    try:
        return list(setup_test_recommender.product_indices.keys())[0]
    except Exception as e:
        logger.error(f"Error obteniendo ID de prueba: {e}")
        raise