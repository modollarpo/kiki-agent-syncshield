import { PrismaClient } from '@prisma/client';
import { sendSMS, sendEmail, sendSlack, sendPhoneCall } from './channels';
import { NotificationEvent, Severity, NotificationChannel, ClientPreferences } from './types';

const prisma = new PrismaClient();

// SeverityMap: EventSource -> Severity
const SeverityMap: Record<string, Severity> = {
  SyncShield: 'Critical',
  SyncTwin: 'High',
  SyncFlow: 'Medium',
  SyncBrain: 'Low',
  SyncBill: 'Medium',
};

// ChannelMap: Severity -> Channel
const ChannelMap: Record<Severity, NotificationChannel[]> = {
  Critical: ['SMS', 'PhoneCall'],
  High: ['Slack', 'WhatsApp'],
  Medium: ['Dashboard', 'Email'],
  Low: ['InApp'],
};

// NotificationDispatcher: Main entry point
export class NotificationDispatcher {
  async dispatch(event: NotificationEvent) {
    const severity = SeverityMap[event.source] || 'Low';
    const channels = ChannelMap[severity];
    const prefs = await this.getClientPreferences(event.clientId);

    // Rule: Only SMS for SyncShield if ImpactValue >= 0.5
    if (event.source === 'SyncShield' && event.impactValue >= 0.5) {
      if (this.isAllowedByPrefs('Critical', prefs)) {
        await sendSMS(event.clientId, event.message);
        await sendPhoneCall(event.clientId, event.message);
      }
      return;
    }

    // Rule: SyncFlow low budget warning
    if (event.source === 'SyncFlow' && event.accountBalance < event.dailySpend * 2) {
      if (this.isAllowedByPrefs('Medium', prefs)) {
        await sendEmail(event.clientId, 'Low Budget Warning', event.message);
      }
      return;
    }

    // Rule: Smart Grouping for SyncBrain optimizations
    if (event.source === 'SyncBrain' && event.optimizationCount && event.optimizationCount > 50) {
      if (this.isAllowedByPrefs('Low', prefs)) {
        await sendEmail(event.clientId, 'Hourly Optimization Summary', this.groupOptimizations(event));
      }
      return;
    }

    // Rule: OaaS Hook for SyncBill
    if (event.source === 'SyncBill' && event.settlementFinalized) {
      if (this.isAllowedByPrefs('Medium', prefs)) {
        await sendEmail(event.clientId, 'Success Notification', `Net Profit Uplift: $${event.netProfitUplift}`);
      }
      return;
    }

    // Default: Route by severity and preferences
    for (const channel of channels) {
      if (this.isAllowedByPrefs(severity, prefs)) {
        await this.sendByChannel(channel, event);
      }
    }
  }

  async getClientPreferences(clientId: string): Promise<ClientPreferences> {
    return prisma.clientPreferences.findUnique({ where: { clientId } }) || {};
  }

  isAllowedByPrefs(severity: Severity, prefs: ClientPreferences): boolean {
    // Example: Do not disturb after 8 PM for Medium alerts
    if (severity === 'Medium' && prefs.doNotDisturb && prefs.doNotDisturb.active) {
      const hour = new Date().getHours();
      if (hour >= prefs.doNotDisturb.startHour && hour < prefs.doNotDisturb.endHour) {
        return false;
      }
    }
    return true;
  }

  groupOptimizations(event: NotificationEvent): string {
    // Aggregate optimizations into a summary
    return `SyncBrain made ${event.optimizationCount} optimizations this hour.`;
  }

  async sendByChannel(channel: NotificationChannel, event: NotificationEvent) {
    switch (channel) {
      case 'SMS':
        await sendSMS(event.clientId, event.message);
        break;
      case 'PhoneCall':
        await sendPhoneCall(event.clientId, event.message);
        break;
      case 'Slack':
        await sendSlack(event.clientId, event.message);
        break;
      case 'WhatsApp':
        // Implement WhatsApp send logic
        break;
      case 'Dashboard':
        // In-app dashboard notification
        break;
      case 'Email':
        await sendEmail(event.clientId, 'Notification', event.message);
        break;
      case 'InApp':
        // Silent feed
        break;
    }
  }
}
