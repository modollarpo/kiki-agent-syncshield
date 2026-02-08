export function groupStrategicUpdates(event: any): string {
  // Aggregate optimizations into a summary narrative
  return `KIKI made ${event.optimizationCount} optimizations this morning, resulting in a projected $${event.upliftAmount} LTV increase.`;
}

export function withinTimeWindow(now: Date, window: { startHour: number; endHour: number }): boolean {
  const hour = now.getHours();
  if (window.active && (hour >= window.startHour || hour < window.endHour)) {
    return true;
  }
  return false;
}
