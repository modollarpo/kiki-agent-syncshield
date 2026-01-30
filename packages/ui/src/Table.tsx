import React from "react";

export interface TableColumn<T> {
  key: keyof T;
  label: string;
  render?: (value: any, row: T) => React.ReactNode;
}

export interface TableProps<T> {
  columns: TableColumn<T>[];
  data: T[];
  className?: string;
}

/**
 * Enterprise Table — High-Trust, Dark-Mode, Emerald Accents
 */
export function Table<T extends object>({ columns, data, className = "" }: TableProps<T>) {
  return (
    <div className={`overflow-x-auto rounded-2xl border border-emerald-500/30 bg-slate-900 shadow-xl ${className}`}>
      <table className="min-w-full divide-y divide-slate-800">
        <thead className="bg-slate-950">
          <tr>
            {columns.map(col => (
              <th
                key={String(col.key)}
                className="px-6 py-4 text-left text-xs font-bold text-emerald-400 uppercase tracking-wider border-b border-emerald-500/20"
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800">
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-6 py-8 text-center text-slate-500">
                No data available
              </td>
            </tr>
          ) : (
            data.map((row, i) => (
              <tr key={i} className="hover:bg-slate-800/60 transition">
                {columns.map(col => (
                  <td
                    key={String(col.key)}
                    className="px-6 py-4 text-slate-200 font-mono"
                  >
                    {col.render ? col.render(row[col.key], row) : row[col.key] as any}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

export default Table;
