import { create } from 'zustand';

interface OnboardingState {
  brandUrl: string;
  prompt: string;
  dna: any;
  creatives: any[];
  adCopy: string[];
  sim: any;
  accounts: Record<string, boolean>;
  setBrandUrl: (url: string) => void;
  setPrompt: (prompt: string) => void;
  setDna: (dna: any) => void;
  setCreatives: (creatives: any[]) => void;
  setAdCopy: (adCopy: string[]) => void;
  setSim: (sim: any) => void;
  setAccount: (provider: string, linked: boolean) => void;
}

export const useOnboardingStore = create<OnboardingState>(set => ({
  brandUrl: '',
  prompt: '',
  dna: null,
  creatives: [],
  adCopy: [],
  sim: null,
  accounts: {},
  setBrandUrl: url => set({ brandUrl: url }),
  setPrompt: prompt => set({ prompt }),
  setDna: dna => set({ dna }),
  setCreatives: creatives => set({ creatives }),
  setAdCopy: adCopy => set({ adCopy }),
  setSim: sim => set({ sim }),
  setAccount: (provider, linked) => set(state => ({ accounts: { ...state.accounts, [provider]: linked } })),
}));
