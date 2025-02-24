import React, { useState, useEffect } from 'react';
import { Grid, Card, Typography, Box, CircularProgress } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getCategoryDistribution } from '../services/api';
import { prepareChartData, formatNumber } from '../utils/helpers';

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadMetrics = async () => {
      try {
        const data = await getCategoryDistribution();
        console.log('Datos recibidos:', data); // Para debug
        setMetrics(prepareChartData(data.distribution));
        setError(null);
      } catch (error) {
        console.error('Error loading metrics:', error);
        setError('Error al cargar los datos');
      } finally {
        setLoading(false);
      }
    };
    loadMetrics();
  }, []);

  if (loading) return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
      <CircularProgress />
    </Box>
  );

  if (error) return (
    <Box p={3}>
      <Typography color="error">{error}</Typography>
    </Box>
  );

  return (
    <Box p={3}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h4" gutterBottom>
            Dashboard de Marketplace
          </Typography>
        </Grid>
        <Grid item xs={12} md={8}>
          <Card>
            <Box p={2}>
              <Typography variant="h6" gutterBottom>
                Distribución por Categoría
              </Typography>
              <Box height={400}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={metrics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip formatter={(value) => formatNumber(value)} />
                    <Bar dataKey="value" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </Box>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <Box p={2}>
              <Typography variant="h6" gutterBottom>
                Resumen
              </Typography>
              <Typography variant="body1">
                Total de Categorías: {metrics?.length || 0}
              </Typography>
              <Typography variant="body1">
                Total de Productos: {metrics?.reduce((sum, item) => sum + item.value, 0) || 0}
              </Typography>
            </Box>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}