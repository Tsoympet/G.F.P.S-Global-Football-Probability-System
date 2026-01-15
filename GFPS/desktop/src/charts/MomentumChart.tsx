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

interface MomentumChartProps {
  points: { label: string; value: number }[];
}

export const MomentumChart = ({ points }: MomentumChartProps) => {
  const labels = points.map((p) => p.label);
  const data = points.map((p) => p.value);

  if (!labels.length) {
    labels.push('0');
    data.push(0);
  }

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
          y: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' }, min: -50, max: 100 }
        }
      }}
    />
  );
};
