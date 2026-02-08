import type { Meta, StoryObj } from '@storybook/react';
import { ProfitTransparency, ProfitData } from './ProfitTransparency';
import './ProfitTransparency.css';

const meta: Meta<typeof ProfitTransparency> = {
  title: 'KIKI/ProfitTransparency',
  component: ProfitTransparency,
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
  },
};

export default meta;
type Story = StoryObj<typeof ProfitTransparency>;

// Mock profit data for Storybook
const mockProfitData: ProfitData = {
  storeId: 123,
  storeName: 'Acme Store',
  period: {
    start: '2026-01-01',
    end: '2026-01-31',
    label: 'January 2026',
  },
  baseline: {
    revenue: 100000,
    adSpend: 20000,
    netProfit: 80000,
  },
  current: {
    revenue: 150000,
    adSpend: 30000,
    netProfit: 120000,
  },
  uplift: {
    revenue: 50000,
    adSpend: 10000,
    netProfit: 40000,
    percentIncrease: 50.0,
  },
  fees: {
    kikiSuccessFee: 8000,  // 20% of $40k net profit
    clientNetGain: 32000,  // 80% of $40k net profit
    clientROI: 4.0,        // $32k / $8k = 4x
  },
};

const mockProfitDataSmall: ProfitData = {
  storeId: 456,
  storeName: 'Small Store',
  period: {
    start: '2026-01-01',
    end: '2026-01-31',
    label: 'January 2026',
  },
  baseline: {
    revenue: 50000,
    adSpend: 10000,
    netProfit: 40000,
  },
  current: {
    revenue: 65000,
    adSpend: 12000,
    netProfit: 53000,
  },
  uplift: {
    revenue: 15000,
    adSpend: 2000,
    netProfit: 13000,
    percentIncrease: 32.5,
  },
  fees: {
    kikiSuccessFee: 2600,  // 20% of $13k
    clientNetGain: 10400,  // 80% of $13k
    clientROI: 4.0,
  },
};

// Mock API endpoint with fake delay
const mockApiEndpoint = (data: ProfitData) => {
  // Override global fetch for this story
  global.fetch = async (url: string) => {
    await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
    return {
      ok: true,
      status: 200,
      json: async () => data,
    } as Response;
  };
  return 'http://mock-api';
};

export const Default: Story = {
  args: {
    storeId: 123,
    apiEndpoint: mockApiEndpoint(mockProfitData),
    showDetailedBreakdown: true,
    showTrendChart: false,
  },
};

export const SmallBusiness: Story = {
  args: {
    storeId: 456,
    apiEndpoint: mockApiEndpoint(mockProfitDataSmall),
    showDetailedBreakdown: true,
  },
};

export const MinimalView: Story = {
  args: {
    storeId: 123,
    apiEndpoint: mockApiEndpoint(mockProfitData),
    showDetailedBreakdown: false,
    showTrendChart: false,
  },
};

export const Loading: Story = {
  args: {
    storeId: 789,
    apiEndpoint: 'http://loading-forever',
  },
  parameters: {
    docs: {
      description: {
        story: 'Simulates the loading state when API is slow to respond',
      },
    },
  },
};

export const ErrorState: Story = {
  args: {
    storeId: 999,
    apiEndpoint: 'http://error-endpoint',
  },
  parameters: {
    docs: {
      description: {
        story: 'Simulates an API error (404 or 500)',
      },
    },
  },
  beforeEach: () => {
    global.fetch = async () => {
      throw new Error('Network error: Unable to connect to SyncBill API');
    };
  },
};
