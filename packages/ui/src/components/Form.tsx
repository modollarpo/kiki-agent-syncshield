import React from 'react';
import { Input } from './Input';
import { Button } from './Button';
import { spacing } from '../theme';

export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'number' | 'select' | 'checkbox' | 'textarea';
  required?: boolean;
  placeholder?: string;
  options?: { label: string; value: string }[]; // for select
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

export const Form: React.FC<FormProps> = ({
  fields,
  onSubmit,
  submitLabel = 'Submit',
  initialValues = {},
  loading = false,
  error,
  className = '',
}) => {
  const [values, setValues] = React.useState<Record<string, any>>(initialValues);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setValues(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(values);
  };

  return (
    <form className={className} onSubmit={handleSubmit} autoComplete="off" style={{ marginBottom: spacing.lg }}>
      {fields.map(field => (
        <Input
          key={field.name}
          label={field.label}
          name={field.name}
          type={field.type}
          required={field.required}
          placeholder={field.placeholder}
          value={values[field.name] || ''}
          onChange={handleChange}
        />
      ))}
      {error && <div style={{ color: 'red', fontSize: 13 }}>{error}</div>}
      <Button type="submit" disabled={loading} style={{ width: '100%' }}>
        {loading ? 'Loading...' : submitLabel}
      </Button>
    </form>
  );
};
