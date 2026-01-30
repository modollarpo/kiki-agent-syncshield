import React from 'react';
import { colors, radii, spacing, typography } from '../theme';

export interface TableColumn<T> {
  key: keyof T;
  label: string;
  align?: 'left' | 'center' | 'right';
  render?: (row: T) => React.ReactNode;
}

export interface TableProps<T> {
  columns: TableColumn<T>[];
  data: T[];
  emptyText?: string;
}

export function Table<T extends object>({ columns, data, emptyText = 'No data' }: TableProps<T>) {
  return (
    <div style={{ overflowX: 'auto' }}>
      <table
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontFamily: typography.fontFamily,
          fontSize: 15,
        }}
      >
        <thead>
          <tr>
            {columns.map(col => (
              <th
                key={String(col.key)}
                style={{
                  textAlign: col.align || 'left',
                  padding: spacing.sm,
                  background: colors.neutral[200],
                  color: colors.neutral[600],
                  fontWeight: typography.headings.fontWeight,
                  borderBottom: `2px solid ${colors.neutral[300]}`,
                }}
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} style={{ textAlign: 'center', padding: spacing.lg }}>
                {emptyText}
              </td>
            </tr>
          ) : (
            data.map((row, i) => (
              <tr key={i} style={{ background: i % 2 ? colors.neutral[100] : '#fff' }}>
                {columns.map(col => (
                  <td
                    key={String(col.key)}
                    style={{
                      textAlign: col.align || 'left',
                      padding: spacing.sm,
                      borderBottom: `1px solid ${colors.neutral[200]}`,
                    }}
                  >
                    {col.render ? col.render(row) : String(row[col.key])}
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
