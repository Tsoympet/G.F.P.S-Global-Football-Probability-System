import { Sidebar } from '@components/Sidebar';
import { TopBar } from '@components/TopBar';
import { useNavigationStore } from '@store/navigation';
import { Dashboard } from '@screens/Dashboard';
import { LiveMatchCenter } from '@screens/LiveMatchCenter';
import { ValueBets } from '@screens/ValueBets';
import { ModelsTraining } from '@screens/ModelsTraining';
import { Settings } from '@screens/Settings';
import { palette } from '@theme/palette';

export const App = () => {
  const { section } = useNavigationStore();

  return (
    <div style={{ display: 'flex', height: '100vh', background: palette.background }}>
      <Sidebar />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <TopBar />
        <main style={{ padding: 20, overflow: 'auto', flex: 1 }}>
          {section === 'Dashboard' && <Dashboard />}
          {section === 'Live Match Center' && <LiveMatchCenter />}
          {section === 'Value Bets (EV+)' && <ValueBets />}
          {section === 'Models & Training' && <ModelsTraining />}
          {section === 'Settings' && <Settings />}
        </main>
      </div>
    </div>
  );
};
