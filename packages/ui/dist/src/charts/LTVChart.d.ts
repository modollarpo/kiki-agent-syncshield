import React from 'react';
export interface LTVChartProps {
    data: {
        date: string;
        ltv: number;
        roas?: number;
    }[];
    height?: number;
}
export declare const LTVChart: React.FC<LTVChartProps>;
//# sourceMappingURL=LTVChart.d.ts.map