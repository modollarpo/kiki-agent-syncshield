import { ClientSovereigntyProfile } from './types';

export async function loadClientProfile(clientId: string): Promise<ClientSovereigntyProfile> {
  // Load from Postgres (stub)
  return {
    clientId,
    doNotDisturb: {
      active: true,
      startHour: 20,
      endHour: 8,
    },
    lastNotificationTime: new Date(),
  };
}

export async function logNotificationToLedger(event: any, channel: string) {
  // Log notification event to SyncLedger (stub)
}
