import React, { useState } from "react";
import PropTypes from "prop-types";
import { Button, Modal, Select, message } from "antd";
import { DownloadOutlined } from "@ant-design/icons";
import "../App.css";

const { Option } = Select;

const DownloadExportButton = ({ rows, headCells, rowID, filename = "table_data", disabled }) => {
  const [openDialog, setOpenDialog] = useState(false);
  const [exportFormat, setExportFormat] = useState("TSV"); // Default format

  const handleDownload = () => {
    if (!rows.length || !headCells.length) {
      message.warning("No data to export.");
      return;
    }

    let fileContent = "";
    let fileExtension = "";
    let mimeType = "";

    if (exportFormat === "TSV" || exportFormat === "CSV") {
      const delimiter = exportFormat === "TSV" ? "\t" : ",";
      fileExtension = exportFormat.toLowerCase();
      mimeType = `text/${exportFormat.toLowerCase()};charset=utf-8`;

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
      const filteredHeadCells = headCells.filter(cell => cell.field !== "actions");
      const headers = filteredHeadCells.map(cell => escapeValue(cell.headerName)).join(delimiter);      

      // Convert rows to formatted CSV/TSV
      const fileRows = rows.map(row =>
        filteredHeadCells.map(cell => escapeValue(row[cell.field])).join(delimiter)
      );      

      // Combine headers and rows
      fileContent = [headers, ...fileRows].join("\n");
    } else if (exportFormat === "JSON") {
      fileExtension = "json";
      mimeType = "application/json;charset=utf-8";
      fileContent = JSON.stringify(rows, null, 2);
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

    message.success(`Exported as ${exportFormat}`);
    setOpenDialog(false); // Close modal after download
  };

  return (
    <>
      {/* Download Button */}
      <Button 
        type="primary" 
        icon={<DownloadOutlined />} 
        onClick={() => setOpenDialog(true)} 
        // disabled={disabled}
      >
        Download
      </Button>

      {/* Modal for Selecting Export Format */}
      <Modal
        title="Select Export Format"
        open={openDialog}
        onCancel={() => setOpenDialog(false)}
        onOk={handleDownload}
        okText="Download"
        cancelText="Cancel"
      >
        <Select 
          value={exportFormat} 
          onChange={setExportFormat} 
          style={{ width: "100%" }}
        >
          <Option value="TSV">TSV</Option>
          <Option value="CSV">CSV</Option>
          <Option value="JSON">JSON</Option>
        </Select>
      </Modal>
    </>
  );
};

DownloadExportButton.propTypes = {
  rows: PropTypes.array.isRequired,
  rowID: PropTypes.string.isRequired,
  headCells: PropTypes.array.isRequired,
  filename: PropTypes.string,
  disabled: PropTypes.bool,
};

export default DownloadExportButton;
