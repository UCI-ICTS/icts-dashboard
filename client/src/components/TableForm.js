import React from 'react';
import PropTypes from 'prop-types';
import "../App.css";
import { alpha } from '@mui/material/styles';
import {
  Box,
  Button, 
  FormControlLabel,
  IconButton,
  Paper,
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
  Typography,
} from "@material-ui/core";

import DeleteIcon from '@mui/icons-material/Delete';
import FilterListIcon from '@mui/icons-material/FilterList';
import { visuallyHidden } from '@mui/utils';
import { useDispatch, useSelector } from 'react-redux';
import FormDialogue from './FormDialogue';
import CircularProgress from '@mui/material/CircularProgress';

// Generate headCells dynamically from schema
const generateHeadCells = (schema) => {
  return schema
  ? Object.entries(schema.properties).map(([key, value]) => ({
      id: key,
      numeric: value.type === 'number', // Set numeric based on type
      disablePadding: false,
      label: value.label || key, // Use description or fallback to key
      description: value.description || key, // Use description or fallback to key
    }))
  : [];
};

function descendingComparator(a, b, orderBy) {
  if (b[orderBy] < a[orderBy]) {
    return -1;
  }
  if (b[orderBy] > a[orderBy]) {
    return 1;
  }
  return 0;
}

function getComparator(order, orderBy) {
  return order === 'desc'
    ? (a, b) => descendingComparator(a, b, orderBy)
    : (a, b) => -descendingComparator(a, b, orderBy);
}

function EnhancedTableHead({headCells, ...props}) {
  const { order, orderBy, numSelected, rowCount, onRequestSort } =
    props;
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
                <Box component="span" sx={visuallyHidden}>
                  {/* {order === 'desc' ? 'sorted descending' : 'sorted ascending'} */}
                </Box>
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
  numSelected: PropTypes.number.isRequired,
  onRequestSort: PropTypes.func.isRequired,
  order: PropTypes.oneOf(['asc', 'desc']).isRequired,
  orderBy: PropTypes.string.isRequired,
  rowCount: PropTypes.number.isRequired,
};

function EnhancedTableToolbar(props) {
  const { numSelected } = props;
  return (
    <Toolbar
      sx={[
        {
          pl: { sm: 2 },
          pr: { xs: 1, sm: 1 },
        },
        numSelected > 0 && {
          bgcolor: (theme) =>
            alpha(theme.palette.primary.main, theme.palette.action.activatedOpacity),
        },
      ]}
    >
      {numSelected > 0 ? (
        <Typography
          sx={{ flex: '1 1 100%' }}
          color="inherit"
          variant="subtitle1"
          component="div"
        >
          {numSelected} selected
        </Typography>
      ) : (
        <Typography
          sx={{ flex: '1 1 100%' }}
          variant="h6"
          id="tableTitle"
          component="div"
        >
          **CHANGE THIS TO SEARCH FEATURES**
        </Typography>
      )}
      {numSelected > 0 ? (
        <Tooltip title="Delete">
          <IconButton>
            <DeleteIcon />
          </IconButton>
        </Tooltip>
      ) : (
        <Tooltip title="Filter list">
          <IconButton>
            <FilterListIcon />
          </IconButton>
        </Tooltip>
      )}
    </Toolbar>
  );
}

EnhancedTableToolbar.propTypes = {
  numSelected: PropTypes.number.isRequired,
};

export default function TableForm({rows, schema, rowID}) {
  const headCells = React.useMemo(() => generateHeadCells(schema), [schema]);
  const loadStatus = useSelector((state) => state.data.status);
  const [order, setOrder] = React.useState('asc');
  const [orderBy, setOrderBy] = React.useState(rowID);
  const [selected, setSelected] = React.useState([]);
  const [page, setPage] = React.useState(0);
  const [dense, setDense] = React.useState(false);
  const [rowsPerPage, setRowsPerPage] = React.useState(25);
  const [selectedRow, setSelectedRow] = React.useState(null); // Holds the row data for the dialog
  const [openDialog, setOpenDialog] = React.useState(false); // Controls dialog visibility
  
  const handleRequestSort = (event, property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleClick = (row) => {
   setSelectedRow(row); // Save the clicked row data
   setOpenDialog(true); // Open the dialog
  };

  const handleDialogClose = () => {
    setOpenDialog(false);
    setSelectedRow(null);
  };
  
  const handleAddNewRow = () => {
    // Create an empty row structure based on schema
    const emptyRow = Object.keys(schema.properties).reduce((acc, key) => {
      acc[key] = ""; // Set all fields to empty
      return acc;
    }, {});

    setSelectedRow(emptyRow); // Open dialog with empty row
    setOpenDialog(true);
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    const value = parseInt(event.target.value, 10);
    setRowsPerPage(value);
    setPage(0);
    // If "All" is selected, show all rows
    if (value === -1) {
      setPage(0);
    }
  };

  const handleChangeDense = (event) => {
    setDense(event.target.checked);
  };

  // Avoid a layout jump when reaching the last page with empty rows.
  const emptyRows =
    page > 0 ? Math.max(0, (1 + page) * rowsPerPage - rows.length) : 0;

  const visibleRows = React.useMemo(
    () =>
      rows
        ? [...rows]
          .sort(getComparator(order, orderBy))
          .slice(
            page * (rowsPerPage === -1 ? rows.length : rowsPerPage), 
            rowsPerPage === -1 ? rows.length : page * rowsPerPage + rowsPerPage
          )
        : [],
    [rows, order, orderBy, page, rowsPerPage],
  );

  return (
    <Box sx={{ width: '100%' }}>
      <Paper sx={{ width: '100%', mb: 2 }}>
        <Box className='box-flex' >
          <Button
            variant="outlined"
            color="primary"
            onClick={handleAddNewRow}
            style={{ margin: '10px 0' }}
            disabled={visibleRows === 0}
          >
            Add Row
          </Button>
          <TablePagination
            rowsPerPageOptions={[25, 50, 75, 100, { label: 'Show all', value: -1 }]}
            component="div"
            count={rows.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
          <EnhancedTableToolbar numSelected={selected.length} />
        </Box>
        <TableContainer>
          {loadStatus === "loading" ? (
            <Box className='box-flex'>
              <CircularProgress />
            </Box>
          ) : (
            <Table
            sx={{ minWidth: 750 }}
            aria-labelledby="tableTitle"
            size={dense ? 'small' : 'medium'}
          >
            <EnhancedTableHead
              headCells={headCells}
              numSelected={selected.length}
              order={order}
              orderBy={orderBy}
              onRequestSort={handleRequestSort}
              rowCount={rows.length}
            />
            <TableBody>
              {visibleRows.map((row, index) => {
                return (
                  <TableRow
                    hover
                    onClick={() => handleClick(row)}
                    key={row[rowID]}
                    sx={{ cursor: 'pointer' }}
                  >
                    {headCells.map((cell) => (
                      <TableCell key={cell.id} align={cell.numeric ? 'right' : 'left'}>
                        {row[cell.id] || ""}
                      </TableCell>
                    ))}
                  </TableRow>
                );
              })}
              {emptyRows > 0 && (
                <TableRow
                  style={{
                    height: (dense ? 33 : 53) * emptyRows,
                  }}
                >
                  <TableCell colSpan={6} />
                </TableRow>
              )}
            </TableBody>
          </Table>
          )}
        </TableContainer>

      </Paper>
      <FormControlLabel
        control={<Switch checked={dense} onChange={handleChangeDense} />}
        label="Dense padding"
      />
      <FormDialogue
        open={openDialog}
        onClose={handleDialogClose}
        schema={schema} // Ensure schema includes the 'title' property
        selectedRow={selectedRow}
        rowID={rowID}
      />
    </Box>
  );
}