import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Card,
  Typography,
  List,
  ListItem
} from '@mui/material';
import { getRecommendations } from '../services/api';

export default function Recommendations() {
  const [productId, setProductId] = useState('');
  const [recommendations, setRecommendations] = useState([]);

  const handleSearch = async () => {
    try {
      const data = await getRecommendations(productId);
      setRecommendations(data.recommendations);
    } catch (error) {
      console.error('Error:', error);
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
        />
        <Button 
          variant="contained" 
          onClick={handleSearch}
          sx={{ ml: 2 }}
        >
          Buscar
        </Button>
      </Box>
      {recommendations.length > 0 && (
        <Card>
          <List>
            {recommendations.map((rec, index) => (
              <ListItem key={index}>
                <Typography>
                  Producto ID: {rec.product_id} - 
                  Similitud: {(rec.similarity_score * 100).toFixed(1)}%
                </Typography>
              </ListItem>
            ))}
          </List>
        </Card>
      )}
    </Box>
  );
}