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

interface ProbabilityEvolutionChartProps {
  labels: string[];
  home: number[];
  draw: number[];
  away: number[];
}

export const ProbabilityEvolutionChart = ({ labels, home, draw, away }: ProbabilityEvolutionChartProps) => {
  const safeLabels = labels.length ? labels : ['0'];
  const safeHome = home.length ? home : [0];
  const safeDraw = draw.length ? draw : [0];
  const safeAway = away.length ? away : [0];

  return (
    <Line
      data={{
        labels: safeLabels,
        datasets: [
          {
            label: 'Home',
            data: safeHome,
            borderColor: '#0fd7a1',
            backgroundColor: 'rgba(15,215,161,0.18)',
            tension: 0.3
          },
          {
            label: 'Draw',
            data: safeDraw,
            borderColor: '#f59e0b',
            backgroundColor: 'rgba(245,158,11,0.14)',
            tension: 0.3
          },
          {
            label: 'Away',
            data: safeAway,
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
