import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { getAllTables } from "../slices/dataSlice";
import TableForm from "../components/TableForm";
import "../App.css";
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Container,
  Grid,
  Typography
} from "@material-ui/core";
import schemas from "../schemas/v1.7schemas.json";
import { setTableView } from '../slices/dataSlice';

const tables = [
  { name: "Participants", schema: "participants", identifier: "participant_id" },
  { name: "Families", schema: "families", identifier: "family_id" },
  { name: "Genetic Findings", schema: "genetic_findings", identifier: "genetic_findings_id" },
  { name: "Analytes", schema: "analytes", identifier: "analyte_id" },
  { name: "Phenotypes", schema: "phenotypes", identifier: "phenotype_id" },
  { name: "Experiments", schema: "experiments", identifier: "experiment_id" },
  { name: "DNA Short Read", schema: "experiment_dna_short_read", identifier: "experiment_dna_short_read_id" },
  { name: "RNA Short Read", schema: "experiment_rna_short_read", identifier: "experiment_rna_short_read_id" },
  { name: "PacBio", schema: "experiment_pac_bio", identifier: "experiment_pac_bio_id" },
  { name: "NanoPore", schema: "experiment_nanopore", identifier: "experiment_nanopore_id" }
];

const Gregor = () => {
  const dispatch = useDispatch();
  const tableName = useSelector(state => state.data.tableName);
  const tableView = useSelector(state => state.data['tableView']);
  const tableData = useSelector(state => state.data[tableView]);
  const dataStatus = useSelector(state => state.data.status);
  const rowID = useSelector(state => state.data['tableID']);
  const token = useSelector((state) => state.account.user?.access_token);
  
  const handleChange = (value) => {
    const selectedTable = tables.find(table => table.schema === value);
    dispatch(setTableView(selectedTable));
};


  // Automatically fetch data if the table is empty
  useEffect(() => {
    if (!tableData || (tableData.length === 0 && dataStatus === "idle")) {
      dispatch(getAllTables({ token }));
    }
  }, [dispatch, tableData, token]);

  return (  
    <Container className="table-container">
      {/* Centered Grid for Logo and Table Selector */}
      <Grid container direction="column" alignItems="center" justifyContent="center" spacing={2}>
        <Grid item>
          <img src="../GREGoR_Final_Logo.png" alt="Logo" />
        </Grid>
        <Grid item container alignItems="center" justifyContent="center" spacing={2} style={{ width: "auto" }}>
          <Grid item>
            <Typography variant="h4">{tableName} Table</Typography>
          </Grid>
          <Grid item>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel id="table-select-label">Select Table</InputLabel>
              <Select
                labelId="table-select-label"
                id="table-select"
                value={tableView} 
                onChange={(event) => handleChange(event.target.value)}
                sx={{ backgroundColor: "rgba(255, 255, 255, 0.1)" }}
              >
                {tables.map((table) => (
                  <MenuItem key={table.name} value={table.schema}>
                    {table.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Grid>

      <br/>

      {/* TableForm Component */}
      <TableForm
        rows={tableData || []}
        schema={schemas[tableView] || { properties: {} }}
        rowID={rowID || ""}
      />
    </Container>  
  );
};

export default Gregor;
