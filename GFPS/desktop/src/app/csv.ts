export const escapeCsvField = (value: string | number | undefined | null) => {
  const str = value === undefined || value === null ? '' : String(value);
  const safe = str.replace(/"/g, '""');
  return `"${safe}"`;
};
