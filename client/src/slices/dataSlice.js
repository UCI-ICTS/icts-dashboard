// slices/dataSlice.js
import dataService from "../services/data.service";
import { combineSlices, createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { setMessage } from "./messageSlice";
import { useSelector } from "react-redux";

const initialState = {
  tableView: "genetic_findings",
  tableID: "genetic_findings_id",
  tableName: "Genetic Findings",
  jsonData: [],
  participants: [],
  families: [],
  genetic_findings: [],
  analytes: [],
  phenotypes: [],
  experiments: [],
  status: "idle"
};

export const dataSlice = createSlice({
  name: 'data',
  initialState,
  reducers: {
    setJsonData: (state, action) => {
      state.jsonData = action.payload;
    },
    setTableView: (state, action) => {
      state.tableView = action.payload.schema;
      state.tableID = action.payload.identifier;
      state.tableName = action.payload.name;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(getAllTables.pending, (state, action) => {
        state.status = "loading";
      })
      .addCase(getAllTables.rejected, (state, action) => {
        state.status = "rejected";
      })
      .addCase(getAllTables.fulfilled, (state, action) => {
        const { participants, families, genetic_findings, analytes, phenotypes, experiments } = action.payload;
        Object.assign(state, { participants, families, genetic_findings, analytes, phenotypes, experiments, status: "fulfilled" });
      })
      .addCase(updateTable.fulfilled, (state, action) => {
        state.status = "fulfilled";
        const { table, response, noChanges } = action.payload;
        // Return early if no changes
        if (noChanges) {
          return; 
        }
        // Extract the updated object from the response
        const updatedObject = response[0]?.data?.instance;

        if (updatedObject && table) {
          // Extract the identifier value dynamically using the table name
          const identifier = updatedObject[table];
          // Dynamically determine the collection to update based on the table name
          const collectionName = table === "participant_id" ? "participants" : 
                                 table === "family_id" ? "families" : 
                                 table === "genetic_findings_id" ? "genetic_findings" :
                                 table === "analyte_id" ? "analytes" :
                                 table === "phenotype_id" ? "phenotypes" :
                                 table === "experiment_id" ? "experiments" : null 
      
          if (collectionName && state[collectionName]) {
            // Find the object to update in the relevant collection
            const objectToUpdate = state[collectionName].find(item => item[table] === identifier);
      
            if (objectToUpdate) {
              // Update the object in the state
              Object.assign(objectToUpdate, updatedObject);
            }
          }
        }
      })
      .addCase(updateTable.pending, (state, action) => {
        state.status = "loading";
      })
      .addCase(updateTable.rejected, (state, action) => {
        state.status = "rejected";
      })
  }
});


export const getAllTables = createAsyncThunk(
  "getAllTables",
  async ({token}, thunkAPI) => {
    try {
      const response = await dataService.getAllTables(token);
      return response.data
    } catch(error) {
      console.log("ERROR! ",error)
    }
  }
)

export const updateTable = createAsyncThunk(
  "updateTable",
  async ({table, data, token}, thunkAPI) => {
    const apiCall = (table, data, token) => {
      if (table === "participant_id") {
        return dataService.updateParticipant(data, token);
      }
      if (table === "family_id") {
        return dataService.updateFamily(data, token);
      }
      if (table === "genetic_findings_id") {
        return dataService.updateGeneticFindings(data, token);
      }
      if (table === "analyte_id") {
        return dataService.updateAnalyte(data, token);
      }
      if (table === "analyte_id") {
        return dataService.updateExperiment(data, token);
      }
      if (table === "phenotype_id") {
        return dataService.updatePhenotype(data, token);
      }
      throw new Error("Invalid table type");
    }
    try {
      const response = await apiCall(table, data, token);
      const payload = {response: response.data, table}
      console.log('herwe')
      if (response.data[0].message.includes("had no changes.")) {
        thunkAPI.dispatch(setMessage(`${payload.table} ${response.data[0].identifier} had no changes`));
        // Return a payload with a flag indicating no change
        return { response: [], table, noChanges: true };
      }
      thunkAPI.dispatch(setMessage(`${payload.table} ${response.data[0].identifier} updated successfuly`));
      return payload

    } catch (error) {
      let message = "";
      
      // Check if there's a top-level message.
      if (error.response && error.response.message) {
        message = error.response.message;
        console.log("Top-level message:", message);
      } 
      // Otherwise, if error.response.data is an array and has at least one element:
      else if (
        error.response &&
        error.response.data &&
        Array.isArray(error.response.data) &&
        error.response.data.length > 0
      ) {
        const firstError = error.response.data[0];
        // If the first element has a 'data' key that is an array, use that:
        if (firstError.data && Array.isArray(firstError.data) && firstError.data.length > 0) {
          message = firstError.data
            .map(err => `${err.field}: ${err.error}`)
            .join(", ");
        } 
        // Otherwise, if the first element itself has 'field' and 'error', use those.
        else if (firstError.field && firstError.error) {
          message = `${firstError.field}: ${firstError.error}`;
        } 
        // Otherwise, fall back to stringifying the first element.
        else {
          message = JSON.stringify(firstError);
        }
        console.log("Constructed message from response data:", message);
      } 
      // Fallback generic message.
      else {
        message = "An unknown error occurred.";
        console.log("Fallback message:", message);
      }
      
      console.log("ERROR! ", error.response.data);
      thunkAPI.dispatch(setMessage(message));
      return thunkAPI.rejectWithValue();
    }
    
  }
)

export const {
  setJsonData,
  setTableView
} = dataSlice.actions;
export const dataReducer = dataSlice.reducer;