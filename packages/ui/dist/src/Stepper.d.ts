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
export declare const Stepper: React.FC<StepperProps>;
export default Stepper;
//# sourceMappingURL=Stepper.d.ts.map