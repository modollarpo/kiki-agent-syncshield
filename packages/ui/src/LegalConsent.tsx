"use client";

import React, { useEffect, useMemo, useState } from "react";

export type LegalConsentValue = {
	terms: boolean;
	privacy: boolean;
};

export type LegalConsentProps = {
	value?: LegalConsentValue;
	onValueChange?: (value: LegalConsentValue) => void;
	onConsentChange?: (consented: boolean, value: LegalConsentValue) => void;
	onFinalize?: () => void;
	buttonLabel?: string;
	storageKey?: string;
	persist?: boolean;
	className?: string;
};


export const LegalConsent: React.FC<LegalConsentProps> = ({
	value,
	onValueChange,
	onConsentChange,
	onFinalize,
	buttonLabel = "Finalize & Deploy Council of Nine",
	storageKey = "kiki:legalConsent",
	persist = true,
	className = "",
}) => {
	const [internal, setInternal] = useState<LegalConsentValue>({
		terms: false,
		privacy: false,
	});

	useEffect(() => {
		if (!persist) return;
		if (typeof window === "undefined") return;
		try {
			const raw = window.localStorage.getItem(storageKey);
			if (!raw) return;
			const parsed = JSON.parse(raw) as Partial<LegalConsentValue>;
			if (value !== undefined) return; // controlled mode: don't override
			setInternal({
				terms: Boolean(parsed.terms),
				privacy: Boolean(parsed.privacy),
			});
		} catch {
			// ignore
		}
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [persist, storageKey]);

	const current = value ?? internal;
	const consented = useMemo(
		() => Boolean(current.terms && current.privacy),
		[current.terms, current.privacy]
	);

	useEffect(() => {
		onConsentChange?.(consented, current);
	}, [consented, current, onConsentChange]);

	const update = (next: LegalConsentValue) => {
		if (value === undefined) setInternal(next);
		onValueChange?.(next);
		if (persist && typeof window !== "undefined") {
			try {
				window.localStorage.setItem(storageKey, JSON.stringify(next));
			} catch {
				// ignore
			}
		}
	};

	return (
		<div className={"space-y-4 p-6 bg-slate-800 rounded-lg " + className}>
			<div className="flex items-start gap-3">
				<input
					type="checkbox"
					id="terms"
					className="mt-1"
					checked={current.terms}
					onChange={(e) => update({ ...current, terms: e.target.checked })}
				/>
				<label htmlFor="terms" className="text-sm text-slate-300">
					I authorize KIKI to manage my ad spend and generate creative assets 
					based on the <b>Risk Appetite</b> I have configured.
				</label>
			</div>
			<div className="flex items-start gap-3">
				<input
					type="checkbox"
					id="privacy"
					className="mt-1"
					checked={current.privacy}
					onChange={(e) => update({ ...current, privacy: e.target.checked })}
				/>
				<label htmlFor="privacy" className="text-sm text-slate-300">
					I understand that my data will be processed by 9 autonomous agents 
					to optimize LTV, as described in the <b>Privacy Policy</b>.
				</label>
			</div>
			<button
				type="button"
				disabled={!consented}
				onClick={() => {
					if (!consented) return;
					onFinalize?.();
				}}
				className="w-full py-3 bg-emerald-500 hover:bg-emerald-600 disabled:opacity-40 text-white font-bold rounded-lg transition-all"
			>
				{buttonLabel}
			</button>
		</div>
	);
}

export default LegalConsent;

