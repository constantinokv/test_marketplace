from pydantic import BaseModel
from typing import List, Optional

class ProductBase(BaseModel):
    title: str
    description: str
    category: str
    price: float
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    sales_last_30_days: Optional[int] = None
    stock: Optional[int] = None
    seller_rating: Optional[float] = None
    shipping_time_days: Optional[int] = None

class ProductRecommendation(BaseModel):
    product_id: int
    title: str
    price: float
    rating: float
    category: str
    reviews_count: int
    similarity_score: float

class RecommendationResponse(BaseModel):
    product_id: int
    title: str           # Cambiado de product_title
    category: str        # Cambiado de product_category
    recommendations: List[ProductRecommendation]

# Si necesitas la respuesta de productos similares
class SimilarProductsResponse(BaseModel):
    product_id: int
    title: str
    category: str
    recommendations: List[ProductRecommendation]

# Para la distribución de categorías
class CategoryDistribution(BaseModel):
    distribution: dict[str, int]
    total_products: int