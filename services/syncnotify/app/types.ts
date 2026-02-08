export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type Channel = 'SMS' | 'Call' | 'Slack' | 'WhatsApp' | 'Email' | 'InApp';

export interface NotificationEvent {
  clientId: string;
  source: string;
  severity: Severity;
  message: string;
  budgetPausePercent?: number;
  brandSafetyViolation?: boolean;
  upliftAmount?: number;
  approvalUrl?: string;
  optimizationCount?: number;
  lastNotificationTime?: Date;
}

export interface ClientSovereigntyProfile {
  clientId: string;
  doNotDisturb?: {
    active: boolean;
    startHour: number;
    endHour: number;
  };
  lastNotificationTime?: Date;
}
