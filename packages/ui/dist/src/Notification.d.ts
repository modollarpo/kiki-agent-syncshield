import React from "react";
export interface NotificationProps {
    type?: "success" | "error" | "warning" | "info";
    title?: string;
    message: string;
    onClose?: () => void;
    className?: string;
}
export declare const Notification: React.FC<NotificationProps>;
export default Notification;
//# sourceMappingURL=Notification.d.ts.map