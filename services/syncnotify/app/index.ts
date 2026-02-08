import { SovereignDispatcher } from './SovereignDispatcher';
import { Queue } from 'bullmq';

const queue = new Queue('notifications');
const dispatcher = new SovereignDispatcher(queue);

// Example event
const event = {
  clientId: 'client-001',
  source: 'SyncShield',
  severity: 'CRITICAL',
  message: 'SyncShield triggered a 60% budget pause due to risk.',
  budgetPausePercent: 0.6,
};

dispatcher.dispatch(event);
