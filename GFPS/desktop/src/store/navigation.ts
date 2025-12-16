import { create } from 'zustand';

export type Section =
  | 'Dashboard'
  | 'Live Match Center'
  | 'Value Bets (EV+)'
  | 'Models & Training'
  | 'Settings';

interface NavigationState {
  section: Section;
  setSection: (section: Section) => void;
}

export const useNavigationStore = create<NavigationState>((set) => ({
  section: 'Dashboard',
  setSection: (section) => set({ section })
}));
