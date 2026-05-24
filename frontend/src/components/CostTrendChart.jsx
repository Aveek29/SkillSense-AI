import React, { useMemo } from 'react'
import Chart from 'react-apexcharts'

const CostTrendChart = React.memo(function CostTrendChart({
  actualData = [],
  forecastData = [],
  categories = [],
  height = 320,
  title = 'Cloud Spending Vector & Prophet Forecasts',
}) {
  const chartOptions = useMemo(() => ({
    chart: {
      id: 'finops-cost-trend',
      toolbar: { show: false },
      background: 'transparent',
      fontFamily: 'Inter, sans-serif',
      animations: {
        enabled: true,
        easing: 'easeinout',
        speed: 800,
        animateGradually: { enabled: true, delay: 150 },
      },
    },
    colors: ['#785aff', '#1ec864'],
    fill: {
      type: 'gradient',
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.45,
        opacityTo: 0.05,
        stops: [0, 90, 100],
      },
    },
    stroke: { curve: 'smooth', width: 3 },
    dataLabels: { enabled: false },
    xaxis: {
      categories: categories.length
        ? categories
        : ['Day 5', 'Day 10', 'Day 15', 'Day 20', 'Day 25', 'Day 30'],
      labels: { style: { colors: '#94a3b8', fontFamily: 'Inter' } },
      axisBorder: { show: false },
      axisTicks: { show: false },
    },
    yaxis: {
      labels: {
        style: { colors: '#94a3b8', fontFamily: 'Inter' },
        formatter: (val) => `$${val}`,
      },
    },
    legend: {
      labels: { colors: '#f1f5f9' },
      position: 'top',
      horizontalAlign: 'right',
      fontFamily: 'Inter',
    },
    grid: {
      borderColor: 'rgba(255, 255, 255, 0.06)',
      strokeDashArray: 4,
      padding: { left: 10, right: 10 },
    },
    tooltip: {
      theme: 'dark',
      style: { fontFamily: 'Inter' },
      y: { formatter: (val) => `$${val.toFixed(2)}` },
    },
  }), [categories])

  const chartSeries = useMemo(() => [
    {
      name: 'Actual Spending ($)',
      data: actualData.length ? actualData : [80, 110, 95, 140, 290, 120],
    },
    {
      name: 'Prophet 30-Day Budget ($)',
      data: forecastData.length ? forecastData : [90, 100, 110, 120, 130, 140],
    },
  ], [actualData, forecastData])

  return (
    <div>
      <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', color: 'hsl(var(--text-primary))' }}>
        {title}
      </h3>
      <Chart options={chartOptions} series={chartSeries} type="area" height={height} />
    </div>
  )
})

export default CostTrendChart
