import React, { useState, useMemo } from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  Button, 
  FormControlLabel,
  IconButton,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Toolbar,
  Tooltip,
  TextField,
} from "@material-ui/core";
import "../App.css";
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import { visuallyHidden } from '@mui/utils';
import { useSelector } from 'react-redux';
import FormDialogue from './FormDialogue';
import CircularProgress from '@mui/material/CircularProgress';
import DownloadTSVButton from './TableDownload';

const generateHeadCells = (schema) => {
  return schema
    ? Object.entries(schema.properties).map(([key, value]) => ({
        id: key,
        numeric: value.type === 'number',
        disablePadding: false,
        label: value.label || key,
        description: value.description || key,
      }))
    : [];
};

function descendingComparator(a, b, orderBy) {
  if (b[orderBy] < a[orderBy]) return -1;
  if (b[orderBy] > a[orderBy]) return 1;
  return 0;
}

function getComparator(order, orderBy) {
  return order === 'desc'
    ? (a, b) => descendingComparator(a, b, orderBy)
    : (a, b) => -descendingComparator(a, b, orderBy);
}

function EnhancedTableHead({ headCells, order, orderBy, onRequestSort }) {
  const createSortHandler = (property) => (event) => {
    onRequestSort(event, property);
  };

  return (
    <TableHead>
      <TableRow>
        {headCells.map((headCell) => (
          <TableCell
            key={headCell.id}
            align={headCell.numeric ? 'right' : 'left'}
            padding={headCell.disablePadding ? 'none' : 'normal'}
            sortDirection={orderBy === headCell.id ? order : false}
          >
            <TableSortLabel
              active={orderBy === headCell.id}
              direction={orderBy === headCell.id ? order : 'asc'}
              onClick={createSortHandler(headCell.id)}
            >
              {headCell.label}
              {orderBy === headCell.id ? (
                <Box component="span" sx={visuallyHidden} />
              ) : null}
            </TableSortLabel>
          </TableCell>
        ))}
      </TableRow>
    </TableHead>
  );
}

EnhancedTableHead.propTypes = {
  headCells: PropTypes.array.isRequired,
  onRequestSort: PropTypes.func.isRequired,
  order: PropTypes.oneOf(['asc', 'desc']).isRequired,
  orderBy: PropTypes.string.isRequired,
};

export default function TableForm({ rows, schema, rowID }) {
  const headCells = useMemo(() => generateHeadCells(schema), [schema]);
  const loadStatus = useSelector((state) => state.data.status);
  const [order, setOrder] = useState('asc');
  const [orderBy, setOrderBy] = useState(rowID);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [dense, setDense] = useState(false);
  const [selectedRow, setSelectedRow] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [searchQuery, setSearchQuery] = useState(""); // ✅ **New: State for search query**

  const handleRequestSort = (event, property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleClick = (row) => {
    setSelectedRow(row);
    setOpenDialog(true);
  };

  const handleDialogClose = () => {
    setOpenDialog(false);
    setSelectedRow(null);
  };

  const handleAddNewRow = () => {
    const emptyRow = Object.keys(schema.properties).reduce((acc, key) => {
      acc[key] = "";
      return acc;
    }, {});
    setSelectedRow(emptyRow);
    setOpenDialog(true);
  };

  const handleChangePage = (event, newPage) => setPage(newPage);
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  const handleChangeDense = (event) => setDense(event.target.checked);

  // ✅ **New: Filter rows based on search query**
  const filteredRows = useMemo(() => {
    return rows.filter((row) =>
      Object.values(row).some(
        (value) =>
          value &&
          value.toString().toLowerCase().includes(searchQuery.toLowerCase())
      )
    );
  }, [rows, searchQuery]);

  // ✅ **Updated to use filtered rows**
  const visibleRows = useMemo(() => {
    return filteredRows
      .sort(getComparator(order, orderBy))
      .slice(
        page * (rowsPerPage === -1 ? filteredRows.length : rowsPerPage),
        rowsPerPage === -1 ? filteredRows.length : page * rowsPerPage + rowsPerPage
      );
  }, [filteredRows, order, orderBy, page, rowsPerPage]);

  return (
    <Box sx={{ width: '100%' }}>
      <Box className="box-flex">

        <Button
          variant="outlined"
          color="primary"
          onClick={handleAddNewRow}
          style={{ margin: '10px 0' }}
          disabled={visibleRows.length === 0 || searchQuery !== ""}
        >
          Add Row
        </Button>

        <TablePagination
          rowsPerPageOptions={[25, 50, 75, 100, { label: 'Show all', value: -1 }]}
          component="div"
          count={filteredRows.length} // Count from filtered rows
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />

        <Toolbar>
          <SearchIcon />
          <TextField
            id="search"
            label="Search"
            variant="standard"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            fullWidth
          />
          <Tooltip title="Advanced Search">
            <IconButton>
              <FilterListIcon />
            </IconButton>
          </Tooltip>
        </Toolbar>

        <Box className="box-flex">
          <DownloadTSVButton 
            rows={filteredRows}
            headCells={headCells}
            disabled={searchQuery == ""}
          />
        </Box>
      </Box>

      <TableContainer>
        {loadStatus === "loading" ? (
          <Box className="box-flex">
            <CircularProgress />
          </Box>
        ) : (
          <Table sx={{ minWidth: 750 }} aria-labelledby="tableTitle" size={dense ? 'small' : 'medium'}>
            <EnhancedTableHead headCells={headCells} order={order} orderBy={orderBy} onRequestSort={handleRequestSort} />
            <TableBody>
              {visibleRows.map((row, index) => (
                <TableRow hover onClick={() => handleClick(row)} key={row[rowID]} sx={{ cursor: 'pointer' }}>
                  {headCells.map((cell) => (
                    <TableCell key={cell.id} align={cell.numeric ? 'right' : 'left'}>
                      {row[cell.id] || ""}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </TableContainer>

      <FormControlLabel control={<Switch checked={dense} onChange={handleChangeDense} />} label="Dense padding" />

      <FormDialogue open={openDialog} onClose={handleDialogClose} schema={schema} selectedRow={selectedRow} rowID={rowID} identifier={headCells.length > 0 ? headCells[0].label : ""} />
    </Box>
  );
}
