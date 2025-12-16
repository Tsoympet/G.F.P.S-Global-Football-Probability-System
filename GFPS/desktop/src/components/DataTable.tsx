import { palette } from '@theme/palette';
import React from 'react';

interface Column<T> {
  key: keyof T | string;
  header: string;
  render?: (row: T) => React.ReactNode;
}

interface Props<T> {
  columns: Column<T>[];
  data: T[];
}

export function DataTable<T extends Record<string, any>>({ columns, data }: Props<T>) {
  return (
    <div
      style={{
        border: `1px solid ${palette.border}`,
        borderRadius: 12,
        overflow: 'hidden',
        background: palette.card
      }}
    >
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead style={{ background: 'rgba(255,255,255,0.03)' }}>
          <tr>
            {columns.map((col) => (
              <th
                key={col.header}
                style={{
                  textAlign: 'left',
                  padding: '12px 14px',
                  color: palette.textSecondary,
                  fontWeight: 500,
                  borderBottom: `1px solid ${palette.border}`
                }}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx} style={{ borderBottom: `1px solid ${palette.border}` }}>
              {columns.map((col) => (
                <td key={col.header} style={{ padding: '12px 14px', color: palette.textPrimary }}>
                  {col.render ? col.render(row) : (row[col.key as keyof T] as React.ReactNode)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
