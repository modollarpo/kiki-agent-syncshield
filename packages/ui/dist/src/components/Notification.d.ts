import React from 'react';
export interface NotificationProps {
    message: string;
    type?: 'info' | 'success' | 'warning' | 'error';
    onClose?: () => void;
}
export declare const Notification: React.FC<NotificationProps>;
//# sourceMappingURL=Notification.d.ts.map