import React, { useEffect, useState } from 'react';

/**
 * ProfitTransparency Component
 * 
 * Purpose: Display Net Profit Uplift breakdown for KIKI clients
 * Shows: Revenue increase, ad spend increase, net profit, KIKI fee, client gain
 * 
 * Integration: Fetches data from SyncBill Profit Transparency API
 * Endpoint: GET /profit-transparency/store/{storeId}/current
 * 
 * Business Model:
 * - Net Profit = (Revenue Increase) - (Ad Spend Increase)
 * - KIKI Fee = Net Profit × 20%
 * - Client Net Gain = Net Profit × 80%
 * - Client ROI = Client Gain / KIKI Fee
 */

export interface ProfitData {
  storeId: number;
  storeName: string;
  period: {
    start: string;
    end: string;
    label: string; // e.g., "Jan 2026"
  };
  baseline: {
    revenue: number;
    adSpend: number;
    netProfit: number;
  };
  current: {
    revenue: number;
    adSpend: number;
    netProfit: number;
  };
  uplift: {
    revenue: number;
    adSpend: number;
    netProfit: number;
    percentIncrease: number;
  };
  fees: {
    kikiSuccessFee: number; // 20% of net profit uplift
    clientNetGain: number;  // 80% of net profit uplift
    clientROI: number;       // Client gain / KIKI fee
  };
}

export interface ProfitTransparencyProps {
  storeId: number;
  apiEndpoint?: string; // Default: http://syncbill:8000/profit-transparency
  refreshInterval?: number; // Auto-refresh interval in ms (default: 60000 = 1 min)
  showDetailedBreakdown?: boolean; // Show "Before KIKI" vs "With KIKI" table
  showTrendChart?: boolean; // Show 12-month trend chart
  className?: string;
}

export const ProfitTransparency: React.FC<ProfitTransparencyProps> = ({
  storeId,
  apiEndpoint = 'http://syncbill:8000/profit-transparency',
  refreshInterval = 60000,
  showDetailedBreakdown = true,
  showTrendChart = false,
  className = '',
}) => {
  const [data, setData] = useState<ProfitData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch profit data from SyncBill API
  const fetchProfitData = async () => {
    try {
      const response = await fetch(`${apiEndpoint}/store/${storeId}/current`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const profitData = await response.json();
      setData(profitData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load profit data');
      console.error('ProfitTransparency: API fetch error', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfitData();

    // Auto-refresh if interval provided
    if (refreshInterval > 0) {
      const interval = setInterval(fetchProfitData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [storeId, apiEndpoint, refreshInterval]);

  if (loading) {
    return (
      <div className={`profit-transparency-loading ${className}`}>
        <div className="spinner">Loading profit breakdown...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`profit-transparency-error ${className}`}>
        <p className="error-message">⚠️ {error}</p>
        <button onClick={fetchProfitData}>Retry</button>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className={`profit-transparency ${className}`}>
      {/* Header */}
      <div className="profit-header">
        <h2>💰 Net Profit Transparency</h2>
        <p className="period">{data.period.label}</p>
      </div>

      {/* Key Metrics Summary */}
      <div className="metrics-summary">
        <div className="metric-card net-profit">
          <h3>Net Profit Uplift</h3>
          <p className="amount">${data.uplift.netProfit.toLocaleString()}</p>
          <p className="change">
            ↑ {data.uplift.percentIncrease.toFixed(1)}% from baseline
          </p>
        </div>

        <div className="metric-card kiki-fee">
          <h3>KIKI Success Fee (20%)</h3>
          <p className="amount">${data.fees.kikiSuccessFee.toLocaleString()}</p>
          <p className="note">Only paid on profit increase</p>
        </div>

        <div className="metric-card client-gain">
          <h3>Your Net Gain (80%)</h3>
          <p className="amount highlight">${data.fees.clientNetGain.toLocaleString()}</p>
          <p className="roi">{data.fees.clientROI.toFixed(1)}x ROI on KIKI fee</p>
        </div>
      </div>

      {/* Detailed Breakdown Table */}
      {showDetailedBreakdown && (
        <div className="detailed-breakdown">
          <h3>📊 Before vs. With KIKI</h3>
          <table>
            <thead>
              <tr>
                <th>Metric</th>
                <th>Before KIKI</th>
                <th>With KIKI</th>
                <th>Uplift</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Revenue</td>
                <td>${data.baseline.revenue.toLocaleString()}</td>
                <td>${data.current.revenue.toLocaleString()}</td>
                <td className="positive">+${data.uplift.revenue.toLocaleString()}</td>
              </tr>
              <tr>
                <td>Ad Spend</td>
                <td>${data.baseline.adSpend.toLocaleString()}</td>
                <td>${data.current.adSpend.toLocaleString()}</td>
                <td className="negative">+${data.uplift.adSpend.toLocaleString()}</td>
              </tr>
              <tr className="net-row">
                <td><strong>Net Profit</strong></td>
                <td><strong>${data.baseline.netProfit.toLocaleString()}</strong></td>
                <td><strong>${data.current.netProfit.toLocaleString()}</strong></td>
                <td className="positive"><strong>+${data.uplift.netProfit.toLocaleString()}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
      )}

      {/* Fee Breakdown */}
      <div className="fee-breakdown">
        <h3>💸 How We Split the Profit</h3>
        <div className="fee-split">
          <div className="split-bar">
            <div className="client-portion" style={{ width: '80%' }}>
              <span>You keep: ${data.fees.clientNetGain.toLocaleString()} (80%)</span>
            </div>
            <div className="kiki-portion" style={{ width: '20%' }}>
              <span>KIKI: ${data.fees.kikiSuccessFee.toLocaleString()} (20%)</span>
            </div>
          </div>
          <p className="zero-risk">
            ⚡ <strong>Zero-Risk Guarantee:</strong> If net profit doesn't increase, KIKI fee = $0
          </p>
        </div>
      </div>

      {/* Explanation */}
      <div className="profit-explanation">
        <h4>🧮 How We Calculate Net Profit</h4>
        <ol>
          <li>
            <strong>Revenue Increase:</strong> ${data.current.revenue.toLocaleString()} (now) - ${data.baseline.revenue.toLocaleString()} (before) = <span className="highlight">${data.uplift.revenue.toLocaleString()}</span>
          </li>
          <li>
            <strong>Ad Spend Increase:</strong> ${data.current.adSpend.toLocaleString()} (now) - ${data.baseline.adSpend.toLocaleString()} (before) = <span className="highlight">${data.uplift.adSpend.toLocaleString()}</span>
          </li>
          <li>
            <strong>Net Profit Uplift:</strong> ${data.uplift.revenue.toLocaleString()} (revenue) - ${data.uplift.adSpend.toLocaleString()} (ad spend) = <span className="highlight">${data.uplift.netProfit.toLocaleString()}</span>
          </li>
          <li>
            <strong>Your Net Gain:</strong> ${data.uplift.netProfit.toLocaleString()} × 80% = <span className="highlight">${data.fees.clientNetGain.toLocaleString()}</span>
          </li>
        </ol>
      </div>

      {/* Footer */}
      <div className="transparency-footer">
        <p>
          📈 All calculations are immutable and auditable via SyncLedger™
        </p>
        <a href={`/ledger/store/${storeId}/audit`} className="audit-link">
          View Full Audit Trail →
        </a>
      </div>
    </div>
  );
};

export default ProfitTransparency;
