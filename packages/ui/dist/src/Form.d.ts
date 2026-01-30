import React from "react";
export interface FormField {
    name: string;
    label: string;
    type: "text" | "email" | "password" | "number" | "select" | "checkbox" | "textarea";
    options?: {
        label: string;
        value: string;
    }[];
    required?: boolean;
    placeholder?: string;
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
declare const Form: React.FC<FormProps>;
export default Form;
//# sourceMappingURL=Form.d.ts.map