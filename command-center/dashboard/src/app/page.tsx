"use client";

import Image from "next/image";
import { Skeleton } from "@/components/ui/skeleton";
import { NeuralLog } from "@/components/NeuralLog";
import { useEffect, useState } from "react";

type Preferences = {
	theme: string;
	notifications: boolean;
	layout: string;
	weatherLocation: string;
};

type User = {
	name: string;
	role: string;
	settings?: Partial<Preferences>;
};

const navLinks = [
	{ name: "Dashboard", href: "/" },
	{ name: "Analytics", href: "/analytics" },
	{ name: "Logs", href: "/logs" },
	{ name: "Settings", href: "/settings" },
];

const integrations = [
	{ name: "SyncBrain", icon: "🧠", api: "http://localhost:8001/health" },
	{ name: "SyncValue", icon: "💡", api: "http://localhost:8002/health" },
	{ name: "CRM", icon: "📇", api: "http://localhost:8003/health" },
	{ name: "Ads", icon: "📢", api: "http://localhost:8004/health" },
];

const users: User[] = [
	{ name: "Alex", role: "Architect", settings: { theme: "dark", notifications: true } },
	{ name: "Jordan", role: "Ops", settings: { theme: "light", notifications: false } },
	{ name: "Morgan", role: "Analyst", settings: { theme: "light", notifications: true } },
];

const defaultPreferences: Preferences = {
	theme: "light",
	notifications: true,
	layout: "grid",
	weatherLocation: "New York",
};

export default function HomePage() {
	const [user, setUser] = useState<User>(users[0]);
	const [stats, setStats] = useState([
		{ label: "Active Users", value: 0 },
		{ label: "Revenue (YTD)", value: "$0" },
		{ label: "Log Events (24h)", value: 0 },
		{ label: "Alerts", value: 0 },
	]);
	const [integrationStatus, setIntegrationStatus] = useState<Record<string, string>>({});
	const [health, setHealth] = useState({ cpu: 0, mem: 0, disk: 0 });
	const [recent, setRecent] = useState<string[]>([]);
	const [tasks, setTasks] = useState<Array<{ task: string; done: boolean }>>([]);
	const [notifications, setNotifications] = useState<string[]>([]);
	const [preferences, setPreferences] = useState<Preferences>({
		...defaultPreferences,
		...(user.settings ?? {}),
	});

	useEffect(() => {
		setPreferences({ ...defaultPreferences, ...(user.settings ?? {}) });
	}, [user]);
	const [weather, setWeather] = useState<{ temp: string; desc: string }>({ temp: "--", desc: "Loading..." });
	const [calendar, setCalendar] = useState<string[]>([]);
	const [apiStatus, setApiStatus] = useState<Record<string, string>>({});

	useEffect(() => {
		// Fetch real stats
		fetch("/api/analytics")
			.then(res => res.json())
			.then(d => {
				if (Array.isArray(d.analytics)) {
					setStats([
						{ label: "Active Users", value: d.analytics[0]?.active_users ?? 128 },
						{ label: "Revenue (YTD)", value: d.analytics[0]?.revenue ?? "$1.2M" },
						{ label: "Log Events (24h)", value: d.analytics[0]?.log_events ?? 4521 },
						{ label: "Alerts", value: d.analytics[0]?.alerts ?? 3 },
					]);
				}
			});
		// Fetch system health
		fetch("/api/health")
			.then(res => res.json())
			.then(d => setHealth({ cpu: d.cpu, mem: d.mem, disk: d.disk }));
		// Fetch recent activity
		fetch("/api/activity")
			.then(res => res.json())
			.then(d => setRecent(d.activity || []));
		// Fetch tasks
		fetch(`/api/tasks?user=${user.name}`)
			.then(res => res.json())
			.then(d => setTasks(d.tasks || []));
		// Fetch notifications
		if (preferences.notifications) {
			fetch(`/api/notifications?user=${user.name}`)
				.then(res => res.json())
				.then(d => setNotifications(d.notifications || []));
		} else {
			setNotifications([]);
		}
		// Integrations
		integrations.forEach((i) => {
			fetch(i.api)
				.then((res) => res.ok ? "Connected" : "Not Connected")
				.catch(() => "Not Connected")
				.then((status) => setIntegrationStatus((prev) => ({ ...prev, [i.name]: status })));
		});
		// Fetch weather
		fetch(`/api/weather?location=${preferences.weatherLocation}`)
			.then(res => res.json())
			.then(d => setWeather({ temp: d.temp, desc: d.desc }));
		// Fetch calendar
		fetch(`/api/calendar?user=${user.name}`)
			.then(res => res.json())
			.then(d => setCalendar(d.events || []));
		// Fetch API status for integrations
		integrations.forEach((i) => {
			fetch(i.api.replace("/health", "/status"))
				.then(res => res.json())
				.then(d => setApiStatus(prev => ({ ...prev, [i.name]: d.status })));
		});
	}, [user, preferences]);

	return (
		<div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
			<main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-between py-32 px-16 bg-white dark:bg-black sm:items-start">
				<Image
					className="dark:invert"
					src="/next.svg"
					alt="Next.js logo"
					width={100}
					height={20}
					priority
				/>
				<div className="flex flex-col items-center gap-6 text-center sm:items-start sm:text-left">
					<h1 className="max-w-xs text-3xl font-semibold leading-10 tracking-tight text-black dark:text-zinc-50">
						To get started, edit the page.tsx file.
					</h1>
					<p className="max-w-md text-lg leading-8 text-zinc-600 dark:text-zinc-400">
						Looking for a starting point or more instructions? Head over to{" "}
						<a
							href="https://vercel.com/templates?framework=next.js&utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
							className="font-medium text-zinc-950 dark:text-zinc-50"
						>
							Templates
						</a>{" "}
						or the{" "}
						<a
							href="https://nextjs.org/learn?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
							className="font-medium text-zinc-950 dark:text-zinc-50"
						>
							Learning
						</a>{" "}
						center.
					</p>
				</div>
				<div className="flex flex-col gap-4 text-base font-medium sm:flex-row">
					<a
						className="flex h-12 w-full items-center justify-center gap-2 rounded-full bg-foreground px-5 text-background transition-colors hover:bg-[#383838] dark:hover:bg-[#ccc] md:w-[158px]"
						href="https://vercel.com/new?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
						target="_blank"
						rel="noopener noreferrer"
					>
						<Image
							className="dark:invert"
							src="/vercel.svg"
							alt="Vercel logomark"
							width={16}
							height={16}
						/>
						Deploy Now
					</a>
					<a
						className="flex h-12 w-full items-center justify-center rounded-full border border-solid border-black/[.08] px-5 transition-colors hover:border-transparent hover:bg-black/[.04] dark:border-white/[.145] dark:hover:bg-[#1a1a1a] md:w-[158px]"
						href="https://nextjs.org/docs?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
						target="_blank"
						rel="noopener noreferrer"
					>
						Documentation
					</a>
				</div>
				<div className="space-y-8">
					<nav className="mb-6 flex gap-4">
						{navLinks.map((link) => (
							<a
								key={link.name}
								href={link.href}
								className="px-3 py-2 rounded text-sidebar-accent-foreground bg-sidebar-accent hover:bg-primary transition-colors"
							>
								{link.name}
							</a>
						))}
					</nav>
					<h1 className="text-3xl font-bold text-primary mb-4">
						KIKI Command Center
					</h1>
					<section>
						<h2 className="text-xl font-semibold mb-2">Neural Log (Live)</h2>
						<NeuralLog />
					</section>
					<section>
						<h2 className="text-xl font-semibold mb-2">Analytics</h2>
						<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
							<div className="bg-card p-4 rounded-lg border border-border">
								<Skeleton className="h-40 w-full" />
							</div>
							<div className="bg-card p-4 rounded-lg border border-border">
								<Skeleton className="h-40 w-full" />
							</div>
						</div>
					</section>
					<div className="space-y-8">
						<div className="flex items-center gap-4">
							<div className="text-3xl font-bold">Welcome, {user.name}!</div>
							<span className="px-2 py-1 rounded bg-primary text-primary-foreground text-xs">
								{user.role}
							</span>
							<select
								className="ml-4 px-2 py-1 rounded border text-xs"
								value={user.name}
								onChange={e => setUser(users.find(u => u.name === e.target.value) || users[0])}
							>
								{users.map(u => <option key={u.name} value={u.name}>{u.name} ({u.role})</option>)}
							</select>
						</div>
						<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
							{stats.map((s) => (
								<div
									key={s.label}
									className="bg-card border border-border rounded-lg p-4 text-center shadow"
								>
									<div className="text-lg font-semibold mb-1">{s.label}</div>
									<div className="text-2xl font-bold text-primary">
										{s.value}
									</div>
								</div>
							))}
						</div>
						<div className="grid grid-cols-1 md:grid-cols-4 gap-4">
							<div className="bg-card border border-border rounded-lg p-4 shadow">
								<div className="font-semibold mb-2">System Health</div>
								<div className="text-sm">CPU: <span className="font-mono text-primary">{health.cpu}%</span></div>
								<div className="text-sm">Memory: <span className="font-mono text-secondary">{health.mem}%</span></div>
								<div className="text-sm">Disk: <span className="font-mono text-accent">{health.disk}%</span></div>
							</div>
							<div className="bg-card border border-border rounded-lg p-4 shadow">
								<div className="font-semibold mb-2">Recent Activity</div>
								<ul className="text-sm list-disc pl-4">
									{recent.map((r, i) => <li key={i}>{r}</li>)}
								</ul>
							</div>
							<div className="bg-card border border-border rounded-lg p-4 shadow">
								<div className="font-semibold mb-2">Tasks</div>
								<ul className="text-sm">
									{tasks.map((t, i) => (
										<li key={i} className="flex items-center gap-2">
											<input type="checkbox" checked={t.done} onChange={() => setTasks(tasks.map((tt, idx) => idx === i ? { ...tt, done: !tt.done } : tt))} />
											{t.task}
										</li>
									))}
								</ul>
							</div>
							<div className="bg-card border border-border rounded-lg p-4 shadow">
								<div className="font-semibold mb-2">Notifications</div>
								<ul className="text-sm list-disc pl-4">
									{notifications.length === 0 ? <li>No notifications</li> : notifications.map((n, i) => <li key={i}>{n}</li>)}
								</ul>
							</div>
						</div>
						<div className="grid grid-cols-1 md:grid-cols-4 gap-4">
							<div className="bg-card border border-border rounded-lg p-4 shadow">
								<div className="font-semibold mb-2">Weather</div>
								<div className="text-sm">{preferences.weatherLocation}: <span className="font-mono text-primary">{weather.temp}°</span></div>
								<div className="text-xs text-muted-foreground">{weather.desc}</div>
							</div>
							<div className="bg-card border border-border rounded-lg p-4 shadow">
								<div className="font-semibold mb-2">Calendar</div>
								<ul className="text-sm list-disc pl-4">
									{calendar.length === 0 ? <li>No events</li> : calendar.map((e, i) => <li key={i}>{e}</li>)}
								</ul>
							</div>
							<div className="bg-card border border-border rounded-lg p-4 shadow">
								<div className="font-semibold mb-2">Quick Actions</div>
								<button className="px-2 py-1 rounded bg-primary text-primary-foreground text-xs mb-2" onClick={() => alert("Sync triggered!")}>Trigger Sync</button>
								<button className="px-2 py-1 rounded bg-secondary text-secondary-foreground text-xs" onClick={() => alert("Export started!")}>Export Data</button>
							</div>
						</div>
						<div>
							<h2 className="text-xl font-bold mb-2">Integrations</h2>
							<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
								{integrations.map((i) => (
									<div key={i.name} className="bg-card border border-border rounded-lg p-4 flex flex-col items-center shadow">
										<div className="text-4xl mb-2">{i.icon}</div>
										<div className="font-semibold mb-1">{i.name}</div>
										<div className={`text-xs px-2 py-1 rounded ${integrationStatus[i.name] === "Connected" ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}>{integrationStatus[i.name] || "Checking..."}</div>
										<div className="text-xs mt-1">API: {apiStatus[i.name] || "Loading..."}</div>
										<button className="mt-2 px-2 py-1 rounded bg-accent text-accent-foreground text-xs" onClick={() => alert(`Sync ${i.name} triggered!`)}>Sync Now</button>
									</div>
								))}
							</div>
						</div>
						<div className="bg-card border border-border rounded-lg p-4 mt-8">
							<h2 className="text-lg font-semibold mb-2">User Preferences</h2>
							<div className="flex gap-4 mb-2">
								<label className="flex items-center gap-2 text-sm">
									Theme:
									<select value={preferences.theme} onChange={e => setPreferences({ ...preferences, theme: e.target.value })} className="px-2 py-1 rounded border text-xs">
										<option value="light">Light</option>
										<option value="dark">Dark</option>
									</select>
								</label>
								<label className="flex items-center gap-2 text-sm">
									Notifications:
									<input type="checkbox" checked={preferences.notifications} onChange={e => setPreferences({ ...preferences, notifications: e.target.checked })} />
								</label>
								<label className="flex items-center gap-2 text-sm">
									Layout:
									<select value={preferences.layout} onChange={e => setPreferences({ ...preferences, layout: e.target.value })} className="px-2 py-1 rounded border text-xs">
										<option value="grid">Grid</option>
										<option value="list">List</option>
									</select>
								</label>
								<label className="flex items-center gap-2 text-sm">
									Weather Location:
									<input type="text" value={preferences.weatherLocation} onChange={e => setPreferences({ ...preferences, weatherLocation: e.target.value })} className="px-2 py-1 rounded border text-xs w-24" />
								</label>
							</div>
						</div>
					</div>
				</div>
			</main>
		</div>
	);
}
