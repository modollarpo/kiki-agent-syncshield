import React from 'react';
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
export declare function Table<T extends object>({ columns, data, emptyText }: TableProps<T>): import("react/jsx-runtime").JSX.Element;
//# sourceMappingURL=Table.d.ts.map