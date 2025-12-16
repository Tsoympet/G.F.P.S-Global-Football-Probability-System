import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler);

export const MomentumChart = () => {
  const labels = Array.from({ length: 15 }).map((_, idx) => `${idx * 6}'`);
  const data = labels.map((_, idx) => Math.sin(idx / 3) * 30 + 50);

  return (
    <Line
      data={{
        labels,
        datasets: [
          {
            label: 'Momentum',
            data,
            borderColor: '#1f9ae5',
            backgroundColor: 'rgba(31,154,229,0.12)',
            fill: true,
            tension: 0.4
          }
        ]
      }}
      options={{
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
          y: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } }
        }
      }}
    />
  );
};
