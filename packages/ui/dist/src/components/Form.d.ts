import React from 'react';
export interface FormField {
    name: string;
    label: string;
    type: 'text' | 'email' | 'password' | 'number' | 'select' | 'checkbox' | 'textarea';
    required?: boolean;
    placeholder?: string;
    options?: {
        label: string;
        value: string;
    }[];
}
export interface FormProps {
    fields: FormField[];
    onSubmit: (values: Record<string, any>) => void;
    submitLabel?: string;
    initialValues?: Record<string, any>;
    loading?: boolean;
    error?: string;
    className?: string;
}
export declare const Form: React.FC<FormProps>;
//# sourceMappingURL=Form.d.ts.map