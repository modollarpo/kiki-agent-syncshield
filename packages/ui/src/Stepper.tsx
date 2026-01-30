import React from "react";

export interface StepperStep {
  label: string;
  description?: string;
  completed?: boolean;
  current?: boolean;
}

export interface StepperProps {
  steps: StepperStep[];
  className?: string;
}

/**
 * Enterprise Stepper — High-Trust, Dark-Mode, Emerald Accents
 */
export const Stepper: React.FC<StepperProps> = ({ steps, className = "" }) => (
  <nav className={`flex flex-col gap-4 bg-slate-900 p-6 rounded-2xl border border-emerald-500/30 shadow-xl ${className}`} aria-label="Progress">
    <ol className="flex flex-col gap-2">
      {steps.map((step, i) => (
        <li key={i} className="flex items-center gap-4">
          <span
            className={`flex items-center justify-center w-8 h-8 rounded-full border-2 font-bold text-lg transition-all
              ${step.completed ? 'bg-emerald-500 border-emerald-500 text-slate-900' :
                step.current ? 'border-emerald-400 text-emerald-400' :
                'border-slate-700 text-slate-500 bg-slate-800'}`}
          >
            {step.completed ? '✓' : i + 1}
          </span>
          <div className="flex flex-col">
            <span className={`font-semibold ${step.current ? 'text-emerald-400' : 'text-slate-200'}`}>{step.label}</span>
            {step.description && <span className="text-xs text-slate-400">{step.description}</span>}
          </div>
        </li>
      ))}
    </ol>
  </nav>
);

export default Stepper;
