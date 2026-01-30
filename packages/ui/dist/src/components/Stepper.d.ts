import React from 'react';
export interface Step {
    label: string;
    completed?: boolean;
    active?: boolean;
}
export interface StepperProps {
    steps: Step[];
    current: number;
}
export declare const Stepper: React.FC<StepperProps>;
//# sourceMappingURL=Stepper.d.ts.map