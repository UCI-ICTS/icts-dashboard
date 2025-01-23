// src/pages/GregorTables.js

import React, { useEffect} from "react";
import { useDispatch, useSelector } from "react-redux";
import { getAllTables } from "../slices/dataSlice";
import TableForm from "../components/TableForm";
import "../App.css";
import {
  Box,
  Button,
  Container,
  Grid,
  Typography,
  Paper
} from "@material-ui/core";
import schemas from "../components/schemas.json";

const Gregor = () => {
  const dispatch = useDispatch();
  const tableView = useSelector(state => state.data['tableView']);
  const tableName = useSelector(state => state.data['tableName']);
  const tableData = useSelector(state => state.data[tableView]);
  const rowID = useSelector(state => state.data['tableID']);
  const formType = "Participant"
  const token = useSelector((state) => state.account.user?.access_token)
  
  // Automatically fetch data if the table is empty
  useEffect(() => {
    if (!tableData || tableData.length === 0) {
      dispatch(getAllTables({ token }));
    }
  }, [dispatch, tableData, token]);

  return (
    
    <Container>
      <Box display="flex" flexdirection="column" height="100%" >
        <Container className="table-container">
          <Grid item>
            <Typography variant="h4">{tableName} Table</Typography>
          </Grid>
          <br/>
          <TableForm
            rows={tableData || []}
            schema={schemas[tableView] || { properties: {} }}
            rowID={rowID || ""}
          />
        </Container>
      </Box>
    </Container>
    
  );
};

export default Gregor;
