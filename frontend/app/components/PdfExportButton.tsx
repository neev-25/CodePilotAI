"use client";

import { Download } from "lucide-react";
import { useState } from "react";

interface PdfExportButtonProps {
    targetId: string;
    filename?: string;
    className?: string;
}

export default function PdfExportButton({ targetId, filename = "analyzed-report.pdf", className = "" }: PdfExportButtonProps) {
    const [downloading, setDownloading] = useState(false);

    const handleExport = async () => {
        const element = document.getElementById(targetId);
        if (!element) {
            alert("Report content not found!");
            return;
        }

        setDownloading(true);
        try {
            // Dynamically import to avoid Next.js SSR window errors
            const html2pdf = (await import("html2pdf.js")).default;

            await html2pdf()
                .set({
                    margin: [10, 10, 10, 10],
                    filename,
                    image: { type: "jpeg", quality: 0.98 },
                    html2canvas: { scale: 1.5, useCORS: true, letterRendering: true },
                    jsPDF: { unit: "mm", format: "a4", orientation: "portrait" },
                })
                .from(element)
                .save();
        } catch (e) {
            console.error("PDF Export failed", e);
            alert("Failed to export PDF.");
        } finally {
            setDownloading(false);
        }
    };

    return (
        <button
            onClick={handleExport}
            disabled={downloading}
            className={`flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-white bg-blue-600 rounded-lg shadow hover:bg-blue-700 transition disabled:opacity-50 ${className}`}
        >
            <Download size={16} />
            {downloading ? "Exporting..." : "Export PDF"}
        </button>
    );
}
