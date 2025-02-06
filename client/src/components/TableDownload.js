import React from "react";
import PropTypes from "prop-types";
import { Button } from "@material-ui/core";
import "../App.css";

const DownloadTSVButton = ({ rows, headCells, filename = "table_data.tsv", disabled }) => {
  const convertToTSV = () => {
    if (!rows.length || !headCells.length) {
      console.warn("No data to export.");
      return;
    }

    // Extract column headers
    const headers = headCells.map(cell => cell.label).join("\t");

    // Convert rows to TSV format
    const tsvRows = rows.map(row =>
      headCells.map(cell => (row[cell.id] !== undefined ? row[cell.id] : "")).join("\t")
    );

    // Combine headers and row data
    const tsvContent = [headers, ...tsvRows].join("\n");

    // Create a Blob and trigger download
    const blob = new Blob([tsvContent], { type: "text/tab-separated-values;charset=utf-8" });
    const url = URL.createObjectURL(blob);

    // Create a temporary <a> element for download
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    // Clean up the URL object
    URL.revokeObjectURL(url);
  };

  return (
    <Button 
      variant="contained"
      onClick={convertToTSV} 
      disabled={disabled}
      className="button-confirm"
    >
      Download Search Results
    </Button>
  );
};

DownloadTSVButton.propTypes = {
  rows: PropTypes.array.isRequired,
  headCells: PropTypes.array.isRequired,
  filename: PropTypes.string,
  disabled: PropTypes.bool,
};

export default DownloadTSVButton;
