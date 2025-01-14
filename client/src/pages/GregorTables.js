// src/pages/GregorTables.js

import React, { useEffect} from "react";
import { useDispatch, useSelector } from "react-redux";
import { getAllParticipants } from "../slices/dataSlice";
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
  const tableData = useSelector(state => state.data[tableView]);
  const formType = "Participant"
  const token = useSelector((state) => state.account.user?.access_token)
  console.log(tableView, tableData)
  // Automatically fetch data if the table is empty
  useEffect(() => {
    if (!tableData || tableData.length === 0) {
      dispatch(getAllParticipants({ token }));
    }
  }, [dispatch, tableData, token]);

  return (
    <Paper>
    <Container>
      <Box display="flex" flexdirection="column" height="100%" >
        <Container className="table-container">
          <Grid item>
            <Typography variant="h4">{formType} Table</Typography>
          </Grid>
          <br/>
          <TableForm
            rows={tableData || []}
            schema={schemas[tableView] || { properties: {} }}
          />
        </Container>
      </Box>
    </Container>
    </Paper>
  );
};

export default Gregor;
