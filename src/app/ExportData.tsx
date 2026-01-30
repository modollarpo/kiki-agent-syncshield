"use client";
"use client";
import jsPDF from "jspdf";

export function ExportData({ data, filename }: { data: any[]; filename: string }) {
  const handleExportCSV = () => {
    const csv = [Object.keys(data[0]).join(",")].concat(data.map(row => Object.values(row).join(","))).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename + ".csv";
    a.click();
    URL.revokeObjectURL(url);
  };
  const handleExportJSON = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename + ".json";
    a.click();
    URL.revokeObjectURL(url);
  };
  const handleExportPDF = () => {
    const doc = new jsPDF();
    doc.text(JSON.stringify(data, null, 2), 10, 10);
    doc.save(filename + ".pdf");
  };
  return (
    <div className="flex gap-2 mt-2">
      <button className="px-3 py-1 rounded bg-emerald-700 text-white text-xs" onClick={handleExportCSV}>Export CSV</button>
      <button className="px-3 py-1 rounded bg-emerald-700 text-white text-xs" onClick={handleExportJSON}>Export JSON</button>
      <button className="px-3 py-1 rounded bg-emerald-700 text-white text-xs" onClick={handleExportPDF}>Export PDF</button>
    </div>
  );
}
