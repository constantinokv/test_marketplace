from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List
import os
import logging
from pathlib import Path

from app.services.analyzer import ProductAnalyzer
from app.services.recommender import ProductRecommender
from .models import ProductBase, RecommendationResponse

# Configuraciones
MODEL_PATH = Path('models/trained/recommender.pkl')
VALID_TOKENS = {"test-token"}

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,  # Cambiado a DEBUG para más detalle
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejador del ciclo de vida de la aplicación"""
    try:
        logger.info("Iniciando inicialización de la aplicación")
        
        # Inicializar analyzer
        app.state.analyzer = ProductAnalyzer()
        logger.info("Analyzer inicializado")
        
        # Intentar cargar modelo guardado
        model_path = MODEL_PATH
        if model_path.exists():
            logger.info(f"Cargando modelo desde {model_path}")
            app.state.recommender = ProductRecommender.load_model(model_path)
            logger.info("Modelo cargado exitosamente")
        else:
            logger.info("Entrenando nuevo modelo...")
            # Cargar y procesar datos
            analyzer = app.state.analyzer
            df = analyzer.load_data('data/raw/products.csv')
            logger.info(f"Datos cargados: {df.shape} registros")
            
            df = analyzer.extract_features()
            df = analyzer.normalize_features()
            logger.info("Features procesadas")
            
            # Entrenar nuevo recomendador
            recommender = ProductRecommender()
            recommender.fit(df)
            app.state.recommender = recommender
            logger.info("Modelo entrenado")
            
            # Guardar el modelo
            os.makedirs(model_path.parent, exist_ok=True)
            recommender.save_model(model_path)
            logger.info(f"Modelo guardado en {model_path}")
        
        logger.info("Inicialización completada exitosamente")
        yield
    except Exception as e:
        logger.error(f"Error durante la inicialización: {str(e)}")
        raise
    finally:
        logger.info("Limpieza de recursos")

app = FastAPI(
    title="Marketplace Analysis API",
    description="API para análisis y recomendaciones de productos",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de seguridad
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def verify_token(token: str = Depends(oauth2_scheme)):
    """Verificar que el token sea válido"""
    if token not in VALID_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

@app.get("/")
async def root():
    """Endpoint de prueba"""
    logger.info("Acceso al endpoint raíz")
    return {"message": "Marketplace Analysis API v1.0"}

@app.get("/products/{product_id}/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    product_id: int,
    request: Request,
    token: str = Depends(verify_token),
    n_recommendations: int = 5
):
    """Obtener recomendaciones para un producto específico"""
    logger.info(f"Solicitando recomendaciones para producto {product_id}")
    
    try:
        recommender = request.app.state.recommender
        if not hasattr(recommender, 'product_indices'):
            logger.error("Recomendador no inicializado correctamente")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Recomendador no inicializado correctamente"
            )
        
        # Obtener recomendaciones
        recommendations = recommender.get_recommendations(product_id, n_recommendations)
        logger.info(f"Recomendaciones generadas: {len(recommendations['recommendations'])} items")
        
        return recommendations
        
    except ValueError as e:
        logger.warning(f"Producto no encontrado: {product_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error al obtener recomendaciones: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/products/{product_id}/similar", response_model=RecommendationResponse)
async def get_similar_products(
    product_id: int,
    request: Request,
    by_category: bool = True,
    token: str = Depends(verify_token),
    n_recommendations: int = 5
):
    """Obtener productos similares"""
    logger.info(f"Solicitando productos similares a {product_id}")
    try:
        recommender = request.app.state.recommender
        recommendations = recommender.get_similar_products(
            product_id,
            by_category=by_category,
            n_recommendations=n_recommendations
        )
        logger.info(f"Productos similares encontrados: {len(recommendations)}")
        return {
            "product_id": product_id,
            "recommendations": recommendations
        }
    except ValueError as e:
        logger.warning(f"Producto no encontrado: {product_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error en get_similar_products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@app.get("/metrics/category_distribution")
async def get_category_distribution(
    request: Request,
    token: str = Depends(verify_token),
):
    """Obtener distribución de categorías"""
    logger.info("Solicitando distribución de categorías")
    try:
        recommender = request.app.state.recommender
        if not recommender:
            logger.error("Recomendador no encontrado")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Recomendador no inicializado"
            )
            
        df = recommender.df
        if df is None:
            logger.error("DataFrame no encontrado")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Datos no disponibles"
            )
            
        logger.info(f"DataFrame shape: {df.shape}")
        logger.info(f"Columnas disponibles: {df.columns.tolist()}")
        
        if 'category' not in df.columns:
            logger.error("Columna 'category' no encontrada")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Columna 'category' no encontrada en los datos"
            )
            
        distribution = df['category'].value_counts().to_dict()
        logger.info(f"Distribución calculada: {len(distribution)} categorías")
        
        return {
            "distribution": distribution,
            "total_products": len(df)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la distribución de categorías: {str(e)}"
        )