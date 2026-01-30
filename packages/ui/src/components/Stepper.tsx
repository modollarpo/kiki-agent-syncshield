import React from 'react';
import { colors, spacing } from '../theme';

export interface Step {
  label: string;
  completed?: boolean;
  active?: boolean;
}

export interface StepperProps {
  steps: Step[];
  current: number;
}

export const Stepper: React.FC<StepperProps> = ({ steps, current }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: spacing.lg }}>
    {steps.map((step, i) => (
      <React.Fragment key={step.label}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: '50%',
              background: i < current ? colors.success : i === current ? colors.primary[500] : colors.neutral[300],
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              fontSize: 16,
              marginBottom: 4,
            }}
          >
            {i + 1}
          </div>
          <span style={{ fontSize: 13, color: colors.neutral[600], textAlign: 'center' }}>{step.label}</span>
        </div>
        {i < steps.length - 1 && (
          <div style={{ flex: 1, height: 2, background: colors.neutral[300] }} />
        )}
      </React.Fragment>
    ))}
  </div>
);
