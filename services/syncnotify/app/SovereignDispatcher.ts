import { Queue, Job } from 'bullmq';
import { TwilioAdapter, SlackAdapter, SendGridAdapter, InAppPushAdapter } from './adapters';
import { NotificationContract, NotificationEvent, Severity, Channel, ClientSovereigntyProfile } from './types';
import { loadClientProfile, logNotificationToLedger } from './db';
import { groupStrategicUpdates, withinTimeWindow } from './utils';

// Main Sovereign Dispatcher
export class SovereignDispatcher {
  private queue: Queue;

  constructor(queue: Queue) {
    this.queue = queue;
  }

  async dispatch(event: NotificationEvent) {
    const profile: ClientSovereigntyProfile = await loadClientProfile(event.clientId);
    const severity = event.severity;
    const now = new Date();

    // Preference-Aware Routing
    if (severity !== 'CRITICAL' && profile.doNotDisturb && withinTimeWindow(now, profile.doNotDisturb)) {
      // Skip non-critical notifications during DND
      return;
    }

    // Intelligent Tiering Logic
    if (severity === 'CRITICAL') {
      if (event.source === 'SyncShield' && event.budgetPausePercent >= 0.5) {
        await TwilioAdapter.sendSMS(event.clientId, event.message);
        await TwilioAdapter.sendCall(event.clientId, event.message);
        await logNotificationToLedger(event, 'SMS/Call');
        return;
      }
      if (event.brandSafetyViolation) {
        await TwilioAdapter.sendSMS(event.clientId, event.message);
        await TwilioAdapter.sendCall(event.clientId, event.message);
        await logNotificationToLedger(event, 'SMS/Call');
        return;
      }
    }

    if (severity === 'HIGH') {
      if (event.source === 'SyncTwin' && event.upliftAmount >= 100000) {
        await SlackAdapter.send(event.clientId, event.message);
        await SlackAdapter.sendApprovalLink(event.clientId, event.approvalUrl);
        await logNotificationToLedger(event, 'Slack');
        return;
      }
    }

    if (severity === 'MEDIUM') {
      if (event.source === 'SyncFlow' && event.optimizationCount > 0) {
        // Smart Batching: Group into daily narrative
        const summary = groupStrategicUpdates(event);
        await SendGridAdapter.sendEmail(event.clientId, 'Strategic Update', summary);
        await logNotificationToLedger(event, 'Email');
        return;
      }
    }

    // Smart Batching (Anti-Fatigue)
    if (!withinTimeWindow(now, profile.lastNotificationTime)) {
      // Only send one non-critical notification per hour
      await InAppPushAdapter.send(event.clientId, event.message);
      await logNotificationToLedger(event, 'InApp');
    }
  }
}

// NotificationContract interface
export interface NotificationContract {
  dispatch(event: NotificationEvent): Promise<void>;
}
