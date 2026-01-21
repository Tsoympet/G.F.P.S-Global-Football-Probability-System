import { useEffect } from 'react';
import { Sidebar } from '@components/Sidebar';
import { TopBar } from '@components/TopBar';
import { BetSlip } from '@components/BetSlip';
import ErrorBoundary from '@components/ErrorBoundary';
import { useNavigationStore } from '@store/navigation';
import { Dashboard } from '@screens/Dashboard';
import { LiveMatchCenter } from '@screens/LiveMatchCenter';
import { ValueBets } from '@screens/ValueBets';
import { ModelsTraining } from '@screens/ModelsTraining';
import { Performance } from '@screens/Performance';
import { BacktestWorkbench } from '@screens/BacktestWorkbench';
import { Settings } from '@screens/Settings';
import { Instructions } from '@screens/Instructions';
import { AiMonitor } from '@screens/AiMonitor';
import { palette } from '@theme/palette';
import { useSettingsStore } from '@store/settings';
import { useAuthStore } from '@store/auth';
import { useBetSlipStore } from '@store/betslip';

export const App = () => {
  const { section } = useNavigationStore();
  const { hydrate: hydrateSettings, initialized: settingsReady, theme } = useSettingsStore();
  const { hydrate: hydrateAuth, initialized: authReady } = useAuthStore();
  const { hydrate: hydrateBetSlip } = useBetSlipStore();

  useEffect(() => {
    hydrateSettings();
    hydrateAuth();
    hydrateBetSlip();
  }, [hydrateSettings, hydrateAuth, hydrateBetSlip]);

  useEffect(() => {
    document.body.dataset.theme = theme;
  }, [theme]);

  if (!settingsReady || !authReady) {
    return (
      <div
        style={{
          height: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: palette.background,
          color: palette.textSecondary
        }}
      >
        Loading secure workspace...
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div style={{ display: 'flex', height: '100vh', background: palette.background }}>
        <Sidebar />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <TopBar />
          <main style={{ padding: 20, overflow: 'auto', flex: 1 }}>
            {section === 'Dashboard' && <Dashboard />}
            {section === 'Live Match Center' && <LiveMatchCenter />}
            {section === 'Value Bets (EV+)' && <ValueBets />}
            {section === 'Models & Training' && <ModelsTraining />}
            {section === 'Performance' && <Performance />}
            {section === 'Backtest' && <BacktestWorkbench />}
            {section === 'AI Monitor' && <AiMonitor />}
            {section === 'Instructions' && <Instructions />}
            {section === 'Settings' && <Settings />}
          </main>
        </div>
        <BetSlip />
      </div>
    </ErrorBoundary>
  );
};
