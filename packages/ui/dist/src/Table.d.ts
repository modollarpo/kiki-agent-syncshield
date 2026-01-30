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
export declare function Table<T extends object>({ columns, data, className }: TableProps<T>): import("react/jsx-runtime").JSX.Element;
export default Table;
//# sourceMappingURL=Table.d.ts.map