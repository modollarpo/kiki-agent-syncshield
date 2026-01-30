export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>
      <div className="bg-card p-4 rounded-lg border border-border">
        <p className="text-sm text-muted-foreground">
          Configure backend endpoints for log and analytics data in{" "}
          <code>src/app/api/logs/route.ts</code> and{" "}
          <code>src/app/api/analytics/route.ts</code>.
        </p>
      </div>
      <div className="bg-card p-4 rounded-lg border border-border mt-4">
        <h2 className="text-lg font-semibold mb-2">Theme</h2>
        <p className="text-sm text-muted-foreground mb-2">
          Switch between light and dark mode from the dashboard header.
        </p>
        <h2 className="text-lg font-semibold mt-4 mb-2">Dashboard Features</h2>
        <ul className="list-disc pl-6 text-sm text-muted-foreground">
          <li>Chart export (CSV, PNG)</li>
          <li>Log export (CSV, TXT, JSON)</li>
          <li>Log filtering</li>
          <li>Zoom/pan and custom tooltips in charts</li>
        </ul>
      </div>
    </div>
  );
}
