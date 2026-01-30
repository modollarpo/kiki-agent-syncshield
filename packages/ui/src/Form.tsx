import React, { useState } from "react";

export interface FormField {
  name: string;
  label: string;
  type: "text" | "email" | "password" | "number" | "select" | "checkbox" | "textarea";
  options?: { label: string; value: string }[];
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

const Form: React.FC<FormProps> = ({
  fields,
  onSubmit,
  submitLabel = "Submit",
  initialValues = {},
  loading = false,
  error,
  className = "",
}) => {
  const [values, setValues] = useState<Record<string, any>>(initialValues);
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    let fieldValue: any = value;
    if (type === "checkbox" && e.target instanceof HTMLInputElement) {
      fieldValue = e.target.checked;
    }
    setValues((prev) => ({
      ...prev,
      [name]: fieldValue,
    }));
    setTouched((prev) => ({ ...prev, [name]: true }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(values);
  };

  return (
    <form
      className={`bg-zinc-900 rounded-lg p-6 shadow-lg space-y-4 ${className}`}
      onSubmit={handleSubmit}
      autoComplete="off"
    >
      {fields.map((field) => (
        <div key={field.name} className="flex flex-col gap-1">
          <label htmlFor={field.name} className="text-zinc-200 font-medium">
            {field.label}
            {field.required && <span className="text-red-500 ml-1">*</span>}
          </label>
          {field.type === "textarea" ? (
            <textarea
              id={field.name}
              name={field.name}
              required={field.required}
              placeholder={field.placeholder}
              value={values[field.name] || ""}
              onChange={handleChange}
              className="bg-zinc-800 text-zinc-100 rounded px-3 py-2 border border-zinc-700 focus:border-blue-500 focus:outline-none"
            />
          ) : field.type === "select" ? (
            <select
              id={field.name}
              name={field.name}
              required={field.required}
              value={values[field.name] || ""}
              onChange={handleChange}
              className="bg-zinc-800 text-zinc-100 rounded px-3 py-2 border border-zinc-700 focus:border-blue-500 focus:outline-none"
            >
              <option value="" disabled>
                {field.placeholder || "Select..."}
              </option>
              {field.options?.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          ) : (
            <input
              id={field.name}
              name={field.name}
              type={field.type}
              required={field.required}
              placeholder={field.placeholder}
              value={field.type === "checkbox" ? undefined : values[field.name] || ""}
              checked={field.type === "checkbox" ? !!values[field.name] : undefined}
              onChange={handleChange}
              className={`bg-zinc-800 text-zinc-100 rounded px-3 py-2 border border-zinc-700 focus:border-blue-500 focus:outline-none ${
                field.type === "checkbox" ? "w-5 h-5 mt-1" : ""
              }`}
            />
          )}
        </div>
      ))}
      {error && <div className="text-red-500 text-sm">{error}</div>}
      <button
        type="submit"
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded disabled:opacity-60"
        disabled={loading}
      >
        {loading ? "Loading..." : submitLabel}
      </button>
    </form>
  );
};

export default Form;
