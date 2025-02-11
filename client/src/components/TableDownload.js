import React, { useState } from "react";
import PropTypes from "prop-types";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from "@mui/material";
import "../App.css";

const DownloadExportButton = ({ rows, headCells, rowID, filename = "table_data", disabled }) => {
  const [openDialog, setOpenDialog] = useState(false);
  const [exportFormat, setExportFormat] = useState("TSV"); // Default format

  const handleDownload = () => {
    if (!rows.length || !headCells.length) {
      console.warn("No data to export.");
      return;
    }

    let fileContent = "";
    let fileExtension = "";
    let mimeType = "";

    if (exportFormat === "TSV" || exportFormat === "CSV") {
      const delimiter = exportFormat === "TSV" ? "\t" : ",";
      fileExtension = exportFormat.toLowerCase();
      mimeType = `text/${exportFormat.toLowerCase()};charset=utf-8`;

      // Extract column headers
      const headers = headCells.map(cell => cell.headerName).join(delimiter);

      // Convert rows to selected format
      const fileRows = rows.map(row =>
        headCells.map(cell => 
          Array.isArray(row[cell.field]) 
            ? row[cell.field].join("|")  // Use "|" if the value is an array
            : row[cell.field] !== undefined 
              ? row[cell.field] 
              : ""
        ).join(delimiter)
      );
      

      // Combine headers and row data
      fileContent = [headers, ...fileRows].join("\n");
    } else if (exportFormat === "JSON") {
      fileExtension = "json";
      mimeType = "application/json;charset=utf-8";

      // Convert rows to JSON format
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

    console.log(`✅ Exported as ${exportFormat}`, rows);
    setOpenDialog(false); // Close dialog after download
  };

  return (
    <>
      {/* Download Button */}
      <Button 
        variant="contained"
        onClick={() => setOpenDialog(true)} 
        disabled={disabled}
        className="button-confirm"
      >
        Download
      </Button>

      {/* Dialog for Selecting Export Format */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Select Export Format</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Format</InputLabel>
            <Select
              value={exportFormat}
              onChange={(e) => setExportFormat(e.target.value)}
              label="Format"
            >
              <MenuItem value="TSV">TSV</MenuItem>
              <MenuItem value="CSV">CSV</MenuItem>
              <MenuItem value="JSON">JSON</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleDownload} variant="contained" color="primary">Download</Button>
        </DialogActions>
      </Dialog>
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
