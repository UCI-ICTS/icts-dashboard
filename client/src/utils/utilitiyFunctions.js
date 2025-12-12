// utils/utilitiyFunctions.js

import { message } from "antd";

export const dataDownload = ({filename, displayData, visibleKeys, exportFormat, schema}) => {
    
    // Safe checks — no crashes
    if (!displayData || (Array.isArray(displayData) && displayData.length === 0)) {
    message.warning("No data to export.");
    return;
    }

    if ((exportFormat === "TSV" || exportFormat === "CSV") && (!visibleKeys || visibleKeys.length === 0)) {
    message.warning("No columns selected for export.");
    return;
    }


    let fileContent = "";
    let fileExtension = "";
    let mimeType = "";

    if (exportFormat === "TSV" || exportFormat === "CSV") {
      const isTSV = exportFormat === "TSV";
      const delimiter = isTSV ? "\t" : ",";
      fileExtension = isTSV ? "tsv" : "csv";
      mimeType = isTSV
        ? "text/tab-separated-values;charset=utf-8"
        : "text/csv;charset=utf-8";

      // Escape function for CSV/TSV values
      const escapeValue = (value) => {
        if (Array.isArray(value)) {
          return `"${value.map(item => item.toString().trim()).join("|")}"`;
        }
        if (typeof value === "string") {
          let trimmedValue = value.trim();
          if (trimmedValue.includes(delimiter) || trimmedValue.includes('"') || trimmedValue.includes("\n")) {
            // Wrap in quotes if containing delimiter, quotes, or newlines
            trimmedValue = `"${trimmedValue.replace(/"/g, '""')}"`;
          }
          return trimmedValue;
        }
        return value !== undefined ? value : "";
      };

      // Extract column headers
      const getHeaderTitle = (k) =>
        schema?.properties?.[k]?.title || k;

      const keys = visibleKeys;

      const headers = keys
        .map((k) => escapeValue(getHeaderTitle(k), delimiter))
        .join(delimiter);

      // Convert rows to formatted CSV/TSV
      const fileRows = displayData.map((row) =>
        keys.map((k) => escapeValue(row?.[k])).join(delimiter)
      );

      // Combine headers and rows
      fileContent = [headers, ...fileRows].join("\n");
  
    } else if (exportFormat === "JSON") {
      fileExtension = "json";
      mimeType = "application/json;charset=utf-8";
      fileContent = JSON.stringify(displayData, null, 2);
    }
    // Create and trigger download
    const blob = new Blob([fileContent], { type: mimeType });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `${filename}.${fileExtension}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    message.success(`Current data exported as ${exportFormat}`);
    // setExportOpen(false); // Close modal after download
  };