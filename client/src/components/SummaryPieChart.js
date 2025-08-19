// PieChart.js
import React from 'react';
import { Pie, Doughnut, Bar } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, Title, CategoryScale, LinearScale, BarElement } from 'chart.js';

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  Title,
  CategoryScale,
  LinearScale,
  BarElement);

/**
 * Generic Pie Chart component.
 * Props:
 *  - data: array of { label: string, value: number }
 *  - label: legend label for the dataset
 *  - colors: optional array of background colors (if fewer than data items, colors repeat)
 *  - title: optional chart title
 */
function SummaryPieChart({ data, label, colors = [], title, chartType = "pie" }) {
  // Helper to generate a default palette if no colors are provided

  // const defaultPalette = [
  //   '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
  //   '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
  // ];

  const defaultPalette = [
    '#255799', '#fecc07', '#3f9c35', '#555759','#0083b3',
    '#00b0ca', '#c6beb5', '#d462ad', '#f7eb5f', '#f0ab00'
  ];

  const getColors = () => {
    const palette = colors.length ? colors : defaultPalette;
    // Repeat colors if there are more slices than colors
    return Array.from({ length: data.length }, (_, i) => palette[i % palette.length]);
  };

  const chartData = {
    labels: data.map(item => item.label),
    datasets: [
      {
        label,
        data: data.map(item => item.value),
        backgroundColor: getColors(),
        borderColor: '#ffffff',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    plugins: {
      title: {
        display: !!title,
        text: title,
      },
      legend: {
        display: chartType !== "bar",
        position: 'bottom',
      },
    },
  };

  if (chartType == "pie") {
    return <Pie data={chartData} options={options} />;
  }
  if (chartType == "doughnut") {
    return <Doughnut data={chartData} options={options} />;
  }
  if (chartType == "bar") {
    return <Bar data={chartData} options={options} />;
  }
}

export default SummaryPieChart;
