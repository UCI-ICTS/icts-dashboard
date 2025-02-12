import React, { useState, useMemo } from "react";
import { DataGrid } from "@mui/x-data-grid";
import { 
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TablePagination,
  Toolbar,
  Tooltip,
  TextField,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import FilterListIcon from "@mui/icons-material/FilterList";
import { useSelector } from "react-redux";
import CircularProgress from "@mui/material/CircularProgress";
import DownloadTSVButton from "./TableDownload";
import FormDialogue from "./FormDialogue";

const TableForm = ({ rows, schema, rowID }) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const loadStatus = useSelector((state) => state.data.status);
  const [openDialog, setOpenDialog] = useState(false)
  const [selectedRow, setSelectedRow] = useState(null);
  const [searchQuery, setSearchQuery] = useState(""); // General Search
  const [selectedColumn, setSelectedColumn] = useState(""); // Column Filter
  const [advancedFilters, setAdvancedFilters] = useState({}); // Advanced Filter State
  const [openFilterDialog, setOpenFilterDialog] = useState(false); // Filter Dialog Toggle
  
  // Open dialogue for row
  const handleRowClick = (params) => {
    setSelectedRow(params.row);
    setOpenDialog(true);
  };  

  // Add new row to table
  const handleAddNewRow = () => {
    const emptyRow = Object.keys(schema.properties).reduce((acc, key) => {
      acc[key] = "";
      return acc;
    }, {});
    setSelectedRow(emptyRow);
    setOpenDialog(true);
  };

  // Define columns with filterable options
  const columns = useMemo(
    () =>
      Object.entries(schema.properties).map(([key, value]) => ({
        field: key,
        headerName: value.label || key,
        width: 150,
        minWidth: 100,
        flex: 0,
        resizable: true,
        sortable: true,
        sortComparator: (v1, v2) => {
          // Convert both values to strings first
          const str1 = v1 ? v1.toString() : "";
          const str2 = v2 ? v2.toString() : "";
        
          // Attempt numerical comparison first
          const num1 = parseFloat(str1);
          const num2 = parseFloat(str2);
        
          if (!isNaN(num1) && !isNaN(num2)) {
            return num1 - num2; // Sort numerically if both are valid numbers
          }
        
          return str1.localeCompare(str2); // Default to string comparison
        },
      })),
    [schema]
  );

  // Advanced Filter Logic
  const applyFilters = (row) => {
    return Object.entries(advancedFilters).every(([column, filterValue]) => {
      if (!filterValue) return true;
      const cellValue = row[column]?.toString().toLowerCase() || "";
      return cellValue.includes(filterValue.toLowerCase());
    });
  };

  // Full Search Logic (Text Query + Advanced Filters)
  const filteredRows = useMemo(() => {
    return rows.filter((row) => {
      const rowString = Object.values(row).join(" ").toLowerCase();
      const searchMatch = searchQuery === "" || rowString.includes(searchQuery.toLowerCase());
      return searchMatch && applyFilters(row);
    });
  }, [rows, searchQuery, advancedFilters]);

  // Visable rows: Search results with pagination
  const visibleRows = useMemo(() => {
    if (rowsPerPage === -1) return filteredRows; // Show all rows
    return filteredRows.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);
  }, [filteredRows, page, rowsPerPage]);

  return (
    <Box >
      <Box className="pagination-container">
      <Button
        variant="outlined"
        color="primary"
        onClick={handleAddNewRow}
        style={{ margin: '10px 0' }}
        // disabled={visibleRows === 0 || searchQuery !== ""}
        >Add Row</Button>
      <TablePagination
        rowsPerPageOptions={[25, 50, 75, 100, { label: 'Show all', value: -1 }]}
        component="div"
        count={filteredRows.length} // Count from filtered rows
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={(event, newPage) => setPage(newPage)}
        onRowsPerPageChange={(event) => setRowsPerPage(parseInt(event.target.value, 10))}
        />
        </Box>
      <Toolbar>
        {/* General Search Input */}
        <SearchIcon />
        <TextField
          id="search"
          label="Search All Fields"
          variant="outlined"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          fullWidth
        />

        {/* Column-Specific Search */}
        {/* <FormControl sx={{ minWidth: 200, marginLeft: 2 }}>
          <InputLabel>Filter by Column</InputLabel>
          <Select
            value={selectedColumn}
            onChange={(e) => setSelectedColumn(e.target.value)}
          >
            {columns.map((col) => (
              <MenuItem key={col.field} value={col.field}>
                {col.headerName}
              </MenuItem>
            ))}
          </Select>
        </FormControl> */}

        {/* Open Advanced Filters */}
        <Tooltip title="Advanced Filters">
          <Button
            startIcon={<FilterListIcon />}
            onClick={() => setOpenFilterDialog(true)}
          >
            Advanced Filters
          </Button>
        </Tooltip>

        {/* Download Button */}
        <DownloadTSVButton 
          rows={filteredRows}
          rowID={rowID}
          headCells={columns} 
          disabled={
            searchQuery === "" && 
            Object.values(advancedFilters).every(value => !value)
          }
        />
      </Toolbar>

      {/* Advanced Filters Dialog */}
      <Dialog open={openFilterDialog} onClose={() => setOpenFilterDialog(false)}>
        <DialogTitle>Advanced Filters</DialogTitle>
        <DialogContent>
          {columns.map((col) => (
            <TextField
              key={col.field}
              label={`Filter by ${col.headerName}`}
              variant="outlined"
              value={advancedFilters[col.field] || ""}
              onChange={(e) =>
                setAdvancedFilters((prev) => ({
                  ...prev,
                  [col.field]: e.target.value,
                }))
              }
              fullWidth
              sx={{ mb: 2 }}
            />
          ))}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAdvancedFilters({})}>Clear</Button>
          <Button onClick={() => setOpenFilterDialog(false)}>Apply</Button>
        </DialogActions>
      </Dialog>

      {/* Data Table */}
      {loadStatus === "loading" ? (
        <Box display="flex" justifyContent="center" mt={4}>
          <CircularProgress />
        </Box>
      ) : (
        <DataGrid
          rows={visibleRows}
          columns={columns}
          getRowId={(row) => row[rowID] || row.participant_id || row.genetic_findings_id}
          disableSelectionOnClick
          onRowClick={handleRowClick}
          checkboxSelection={false}
          pagination={false}
          hideFooter
        />
      )}
      <FormDialogue
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        schema={schema}
        selectedRow={selectedRow}
        rowID={rowID}
      />
    </Box>
  );
};

export default TableForm;
