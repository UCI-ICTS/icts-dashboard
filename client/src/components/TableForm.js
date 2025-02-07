import React, { useState, useMemo } from "react";
import { DataGrid } from "@mui/x-data-grid";
import { 
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
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
  const loadStatus = useSelector((state) => state.data.status);
  const [openDialog, setOpenDialog] = useState(false)
  const [selectedRow, setSelectedRow] = useState(null);
  const [searchQuery, setSearchQuery] = useState(""); // General Search
  const [selectedColumn, setSelectedColumn] = useState(""); // Column Filter
  const [advancedFilters, setAdvancedFilters] = useState({}); // Advanced Filter State
  const [openFilterDialog, setOpenFilterDialog] = useState(false); // Filter Dialog Toggle
  
  const handleRowClick = (params) => {
    setSelectedRow(params.row);
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

  return (
    <Box sx={{ width: "100%", height: 600 }}>
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
          rows={filteredRows}
          columns={columns}
          getRowId={(row) => row[rowID] || row.participant_id || row.genetic_findings_id}
          pageSize={25}
          rowsPerPageOptions={[25, 50, 100]}
          disableSelectionOnClick
          onRowClick={handleRowClick}
          checkboxSelection={false}
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
