import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Card,
  Typography,
  List,
  ListItem,
  Grid
} from '@mui/material';
import { getRecommendations } from '../services/api';

export default function Recommendations() {
  const [productId, setProductId] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    try {
      setError('');
      const data = await getRecommendations(productId);
      setSelectedProduct(data); // Guardamos la info del producto seleccionado
      setRecommendations(data.recommendations);
    } catch (error) {
      setError('Error al obtener recomendaciones. Verifica el ID del producto.');
      setRecommendations([]);
      setSelectedProduct(null);
    }
  };

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Recomendaciones de Productos
      </Typography>
      <Box mb={3}>
        <TextField
          label="ID del Producto"
          value={productId}
          onChange={(e) => setProductId(e.target.value)}
          error={!!error}
          helperText={error}
        />
        <Button 
          variant="contained" 
          onClick={handleSearch}
          sx={{ ml: 2 }}
        >
          Buscar
        </Button>
      </Box>

      {selectedProduct && (
        <Card sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Producto Seleccionado
          </Typography>
          <Box>
            <Typography variant="subtitle1" fontWeight="bold">
              {selectedProduct.title}
            </Typography>
            <Typography>
              Categoría: {selectedProduct.category}
            </Typography>
          </Box>
        </Card>
      )}

      {recommendations.length > 0 && (
        <Card sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Productos Relacionados
          </Typography>
          <List>
            {recommendations.map((rec, index) => (
              <ListItem 
                key={index}
                sx={{
                  border: '1px solid #eee',
                  borderRadius: 1,
                  mb: 1,
                  backgroundColor: '#f9f9f9'
                }}
              >
                <Box width="100%">
                  <Typography variant="subtitle1" fontWeight="bold">
                    {rec.title}
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography>
                        ID: {rec.product_id}
                      </Typography>
                      <Typography>
                        Categoría: {rec.category}
                      </Typography>
                      <Typography>
                        Precio: ${rec.price}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography>
                        Rating: {rec.rating} ⭐
                      </Typography>
                      <Typography>
                        Reviews: {rec.reviews_count}
                      </Typography>
                      <Typography color="primary" fontWeight="bold">
                        Similitud: {(rec.similarity_score * 100).toFixed(1)}%
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>
              </ListItem>
            ))}
          </List>
        </Card>
      )}
    </Box>
  );
}