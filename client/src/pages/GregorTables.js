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
import { setTableView } from '../slices/dataSlice';

const tables = [
  {name:"Participants", schema:"participants", identifier:"participant_id"},
  {name:"Families", schema:"families", identifier:"family_id"},
  {name:"Genetic Findings", schema:"genetic_findings", identifier:"genetic_findings_id"},
  {name:"Analytes", schema:"analytes", identifier:"analyte_id"},
  {name:"Phenotypes", schema:"phenotypes", identifier:"phenotype_id"},
  {name:"Experiments", schema:"experiments", identifier:"experiment_id"}
]

const Gregor = () => {
  const dispatch = useDispatch();
  const tableView = useSelector(state => state.data['tableView']);
  const tableData = useSelector(state => state.data[tableView]);
  const rowID = useSelector(state => state.data['tableID']);
  const token = useSelector((state) => state.account.user?.access_token)
  

  
  // Automatically fetch data if the table is empty
  useEffect(() => {
    if (!tableData || tableData.length === 0) {
      dispatch(getAllTables({ token }));
    }
  }, [dispatch, tableData, token]);

  return (  
    <Container className="table-container">
      <Grid item>
      <Typography variant="h4">Select GREGoR table to view:</Typography>
        <Typography variant="h4">{tables.map((table) => (
                <Button
                  key={table.name}
                  onClick={event => dispatch(setTableView(table))}
                  sx={{ my: 2, color: 'white', display: 'block' }}
                >
                  {table.name}
                </Button>
              ))}</Typography>
      </Grid>
      <br/>
      <TableForm
        rows={tableData || []}
        schema={schemas[tableView] || { properties: {} }}
        rowID={rowID || ""}
      />
    </Container>
      
    
    
  );
};

export default Gregor;
