import { NotificationEvent } from './types';

export interface NotificationContract {
  dispatch(event: NotificationEvent): Promise<void>;
}
