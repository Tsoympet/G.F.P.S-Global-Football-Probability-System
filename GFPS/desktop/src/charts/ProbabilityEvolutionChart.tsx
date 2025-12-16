import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

export const ProbabilityEvolutionChart = () => {
  const labels = Array.from({ length: 10 }).map((_, idx) => `${idx * 10}'`);
  const random = () => labels.map(() => Math.max(5, Math.min(90, 40 + Math.random() * 20)));

  return (
    <Line
      data={{
        labels,
        datasets: [
          {
            label: 'Home',
            data: random(),
            borderColor: '#0fd7a1',
            backgroundColor: 'rgba(15,215,161,0.18)',
            tension: 0.3
          },
          {
            label: 'Draw',
            data: random(),
            borderColor: '#f59e0b',
            backgroundColor: 'rgba(245,158,11,0.14)',
            tension: 0.3
          },
          {
            label: 'Away',
            data: random(),
            borderColor: '#1f9ae5',
            backgroundColor: 'rgba(31,154,229,0.18)',
            tension: 0.3
          }
        ]
      }}
      options={{
        plugins: { legend: { labels: { color: '#e5e7eb' } } },
        scales: {
          x: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
          y: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' }, min: 0, max: 100 }
        }
      }}
    />
  );
};
