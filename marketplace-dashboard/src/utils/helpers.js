// Formatear números
export const formatNumber = (number) => {
  return new Intl.NumberFormat().format(number);
};

// Formatear porcentajes
export const formatPercentage = (value) => {
  return `${(value * 100).toFixed(1)}%`;
};

// Preparar datos para gráficos
export const prepareChartData = (distribution) => {
  return Object.entries(distribution).map(([category, count]) => ({
    name: category,
    value: count
  }));
};