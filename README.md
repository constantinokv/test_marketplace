# Marketplace Analysis System

Sistema de análisis y recomendaciones para productos de marketplace, con capacidad de identificar patrones de éxito y ofrecer recomendaciones automatizadas para optimizar listings.

## Estructura del Proyecto

marketplace_analysis/
├── app/
│   ├── api/
│   │   └── routes.py
│   └── services/
├── logs/
│   └── app.log
└── tests/
marketplace-dashboard/
├── src/
│   ├── components/
│   └── services/
└── package.json




## Requisitos

- Python 3.9+
- FastAPI
- scikit-learn
- pandas
- numpy
- spacy
- Node.js (para el dashboard)

## Instalación

1. Clonar el repositorio:
```bash
git clone [url-del-repositorio]
cd marketplace_analysis
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Iniciar el servidor:
```bash
uvicorn app.api.routes:app --reload --log-level debug
```

4. Iniciar el dashboard:
```bash
cd marketplace-dashboard
npm install
npm start
```


##5.Monitoreo de Logs
# Windows
Get-Content -Path ".\logs\app.log" -Wait

# Linux/Mac
tail -f logs/app.log


##Endpints API
##Get Recommendations
[GET /products/{product_id}/recommendations](http://localhost:8000/products/1/recommendations?n_recommendations=2)
or
http://localhost:8000/products/1/recommendations   

Postman - Headers:
- Authorization: Bearer {TOKEN}

Query Params:
- n_recommendations (optional): Número de recomendaciones a retornar (default: 5)

Response 200:
{
    "product_id": 1,
    "title": "iPhone 13 Pro 128GB",
    "category": "Electronics/Phones",
    "recommendations": [
        {
            "product_id": 856,
            "title": "iPhone 13 Pro 128GB",
            "price": 686.08,
            "rating": 3.83,
            "category": "Electronics/Phones",
            "reviews_count": 574,
            "similarity_score": 0.97
        },
        ...
    ]
}