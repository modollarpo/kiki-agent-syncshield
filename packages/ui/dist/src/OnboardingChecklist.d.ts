import React from "react";
export type ChecklistItem = {
    id: number;
    task: string;
    status: "PENDING" | "WAITING" | "LOCKED" | "COMPLETE";
    desc: string;
};
export declare const OnboardingChecklist: React.FC;
export default OnboardingChecklist;
//# sourceMappingURL=OnboardingChecklist.d.ts.map