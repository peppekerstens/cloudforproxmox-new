/**
 * Config store for application-wide configuration.
 * 
 * STUB: Disabled in Phase 1 Batch 2. Real implementation in Phase 8.
 * Provides global config state (API URL, feature flags, etc.)
 */
import { create } from 'zustand';

interface ConfigStore {
  apiUrl: string;
  setApiUrl: (url: string) => void;
}

export const useConfigStore = create<ConfigStore>((set) => ({
  apiUrl: process.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  setApiUrl: (url: string) => set({ apiUrl: url }),
}));
