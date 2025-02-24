import pytest
import logging

# Configurar logging
logger = logging.getLogger(__name__)

def test_root(client):
    """Probar la ruta raíz"""
    logger.info("Probando la ruta raíz")
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Marketplace Analysis API v1.0"

def test_get_recommendations(client, auth_headers, setup_test_recommender):
    """Probar obtención de recomendaciones con producto válido"""
    logger.info("Probando la ruta de recomendaciones")
    
    # Obtener un ID válido del CSV
    valid_id = list(setup_test_recommender.product_indices.keys())[0]
    
    response = client.get(
        f"/products/{valid_id}/recommendations",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "product_id" in data
    assert "title" in data  # Cambiado de product_title
    assert "category" in data  # Cambiado de product_category
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) > 0
    
    # Verificar estructura de las recomendaciones
    for rec in data["recommendations"]:
        assert "product_id" in rec
        assert "title" in rec
        assert "price" in rec
        assert "rating" in rec
        assert "category" in rec
        assert "reviews_count" in rec
        assert "similarity_score" in rec
        assert isinstance(rec["product_id"], int)
        assert isinstance(rec["similarity_score"], float)
        assert rec["product_id"] != valid_id

def test_get_recommendations_invalid_product(client, auth_headers, setup_test_recommender):
    """Probar obtención de recomendaciones con producto inválido"""
    logger.info("Probando la ruta de recomendaciones con producto inválido")
    
    # Usar un ID que definitivamente no existe
    max_id = max(setup_test_recommender.product_indices.keys())
    invalid_id = max_id + 1000
    
    response = client.get(
        f"/products/{invalid_id}/recommendations",
        headers=auth_headers
    )
    assert response.status_code == 404

def test_get_recommendations_without_token(client):
    """Probar acceso sin token de autenticación"""
    logger.info("Probando la ruta de recomendaciones sin token")
    response = client.get("/products/1/recommendations")
    assert response.status_code == 401

def test_get_similar_products(client, auth_headers, setup_test_recommender):
    """Probar obtención de productos similares"""
    logger.info("Probando la ruta de productos similares")
    
    valid_id = list(setup_test_recommender.product_indices.keys())[0]
    
    for by_category in [True, False]:
        response = client.get(
            f"/products/{valid_id}/similar",
            params={"by_category": by_category},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "product_id" in data
        assert "title" in data  # Cambiado de product_title
        assert "category" in data  # Cambiado de product_category
        assert isinstance(data["recommendations"], list)
        assert len(data["recommendations"]) > 0
        
        for rec in data["recommendations"]:
            assert "product_id" in rec
            assert "title" in rec
            assert "price" in rec
            assert "rating" in rec
            assert "category" in rec
            assert "reviews_count" in rec
            assert "similarity_score" in rec
            
            if by_category:
                assert rec["category"] == data["category"]  

def test_get_category_distribution(client, auth_headers):
    """Probar obtención de distribución de categorías"""
    logger.info("Probando la ruta de distribución de categorías")
    
    response = client.get(
        "/metrics/category_distribution",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "distribution" in data
    assert "total_products" in data
    assert isinstance(data["distribution"], dict)
    assert isinstance(data["total_products"], int)
    assert data["total_products"] > 0

def test_invalid_token(client):
    """Probar acceso con token inválido"""
    logger.info("Probando acceso con token inválido")
    
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.get(
        "/products/1/recommendations",
        headers=headers
    )
    assert response.status_code == 401

@pytest.mark.parametrize("n_recommendations", [3, 5, 10])
def test_different_recommendation_counts(
    client,
    auth_headers,
    setup_test_recommender,
    n_recommendations
):
    """Probar diferentes cantidades de recomendaciones"""
    logger.info(f"Probando obtención de {n_recommendations} recomendaciones")
    
    valid_id = list(setup_test_recommender.product_indices.keys())[0]
    
    response = client.get(
        f"/products/{valid_id}/recommendations",
        params={"n_recommendations": n_recommendations},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "product_id" in data
    assert "title" in data
    assert "category" in data
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) == n_recommendations
    
    # Verificar estructura de cada recomendación
    for rec in data["recommendations"]:
        assert "product_id" in rec
        assert "title" in rec
        assert "price" in rec
        assert "rating" in rec
        assert "category" in rec
        assert "reviews_count" in rec
        assert "similarity_score" in rec