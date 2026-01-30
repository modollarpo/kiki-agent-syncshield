"use client";
import React from "react";
import { OnboardingChecklist, LegalConsent, OaasCalculator, ImpactAuditForm } from "@kiki/ui";

export default function OnboardingPage() {
  return (
    <div className="max-w-3xl mx-auto py-12 space-y-10">
      <h1 className="text-3xl font-bold text-emerald-400 mb-8 text-center">Welcome to KIKI Agent™ Onboarding</h1>
      <OnboardingChecklist />
      <OaasCalculator />
      <ImpactAuditForm />
      <LegalConsent />
    </div>
  );
}
