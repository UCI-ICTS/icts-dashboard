// slices/dataSlice.js
import dataService from "../services/data.service";
import { combineSlices, createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { message } from "antd";
import { useSelector } from "react-redux";

const initialState = {
  tableView: "participants",
  tableID: "participant_id",
  tableName: "Participants",
  jsonData: [],
  participants: [],
  families: [],
  genetic_findings: [],
  analytes: [],
  biobank_entries: [],
  phenotypes: [],
  experiments: [],
  experiment_stages: [],
  experiment_dna_short_read: [],
  experiment_rna_short_read: [],
  experiment_pac_bio: [],
  experiment_nanopore: [],
  aligned: [],
  aligned_dna_short_read: [],
  aligned_nanopore: [],
  aligned_pac_bio: [],
  aligned_rna_short_read: [],
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
        const {
          participants, families, genetic_findings, analytes, biobank_entries, phenotypes, experiments, experiment_stages, experiment_dna_short_read, experiment_rna_short_read, experiment_pac_bio, experiment_nanopore,  aligned, aligned_dna_short_read, aligned_nanopore, aligned_pac_bio, aligned_rna_short_read
        } = action.payload;

        Object.assign(state, {
          participants, families, genetic_findings, analytes, biobank_entries, phenotypes, experiments, experiment_stages, experiment_dna_short_read, experiment_rna_short_read, experiment_pac_bio, experiment_nanopore, aligned, aligned_dna_short_read, aligned_nanopore, aligned_pac_bio, aligned_rna_short_read, status: "fulfilled"
        });
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
          const collectionName = table === "participants" ? "participants" :
                                 table === "families" ? "families" :
                                 table === "genetic_findings" ? "genetic_findings" :
                                 table === "analyte" ? "analytes" :
                                 table === "biobank_entries" ? "biobank_entries" :
                                 table === "phenotypes" ? "phenotypes" :
                                 table === "experiments" ? "experiments" :
                                 table === "experiment_stages" ? "experiment_stages" :
                                 table === "experiment_dna_short_read" ? "experiment_dna_short_read" :
                                 table === "experiment_rna_short_read" ? "experiment_rna_short_read" :
                                 table === "experiment_nanopore" ? "experiment_nanopore" :
                                 table === "aligned" ? "aligned" :
                                 table === "aligned_dna_short_read" ? "aligned_dna_short_read" :
                                 table === "aligned_nanopore" ? "aligned_nanopore" :
                                 table === "aligned_pac_bio_id" ? "aligned_pac_bio" :
                                 table === "aligned_rna_short_read" ? "aligned_rna_short_read" : null

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
      .addCase(addTable.fulfilled, (state, action) => {
        state.status = "fulfilled";
        const { table, response, noChanges } = action.payload;
        // Return early if no changes
        if (noChanges) {
          return;
        }
        // Extract the addd object from the response
        const adddObject = response[0]?.data?.instance;

        if (adddObject && table) {
          // Extract the identifier value dynamically using the table name
          const identifier = adddObject[table];
          // Dynamically determine the collection to add based on the table name
          const collectionName = table === "participants" ? "participants" :
                                 table === "families" ? "families" :
                                 table === "genetic_findings" ? "genetic_findings" :
                                 table === "analytes" ? "analytes" :
                                 table === "biobank_entries" ? "biobank_entries" :
                                 table === "phenotypes" ? "phenotypes" :
                                 table === "experiments" ? "experiments" :
                                 table === "experiment_stages" ? "experiment_stages" :
                                 table === "experiment_dna_short_read" ? "experiment_dna_short_read" :
                                 table === "experiment_rna_short_read" ? "experiment_rna_short_read" :
                                 table === "experiment_nanopore" ? "experiment_nanopore" :
                                 table === "aligned" ? "aligned" :
                                 table === "aligned_dna_short_read" ? "aligned_dna_short_read" :
                                 table === "aligned_nanopore" ? "aligned_nanopore" :
                                 table === "aligned_pac_bio_id" ? "aligned_pac_bio" :
                                 table === "aligned_rna_short_read" ? "aligned_rna_short_read" : null

          if (collectionName && state[collectionName]) {
            // Find the object to add in the relevant collection
            const objectToUpdate = state[collectionName].find(item => item[table] === identifier);

            if (objectToUpdate) {
              // Update the object in the state
              Object.assign(objectToUpdate, adddObject);
            }
          }
        }
      })
      .addCase(addTable.pending, (state, action) => {
        state.status = "loading";
      })
      .addCase(addTable.rejected, (state, action) => {
        state.status = "rejected";
      });
  }
});


export const getAllTables = createAsyncThunk(
  "getAllTables",
  async (_, thunkAPI) => {
    try {

      const response = await dataService.getAllTables();
      return response.data
    } catch(error) {
      console.log("ERROR! ",error)
    }
  }
)

export const addTable = createAsyncThunk(
  "addTable",
  async ({table, data}, thunkAPI) => {
    const apiCall = (table, data) => {
      if (table === "participants") {
        return dataService.createParticipant(data);
      }
      if (table === "families") {
        return dataService.createFamily(data);
      }
      if (table === "genetic_findings") {
        return dataService.createGeneticFindings(data);
      }
      if (table === "analytes") {
        return dataService.createAnalyte(data);
      }
      if (table === "biobank_entries") {
        return dataService.createBiobankEntries(data);
      }
      if (table === "phenotypes") {
        return dataService.createPhenotype(data);
      }
      if (table === "experiment_stages") {
        return dataService.createExperimentStage(data);
      }
      if (table === "experiment_dna_short_read_id") {
        console.log("stuff")
        return dataService.createDnaShortRead(data);
      }
      if (table === "experiment_rna_short_read_id") {
        return dataService.createRnaShortRead(data);
      }
      if (table === "experiment_pac_bio_id") {
        return dataService.createPacBio(data);
      }
      if (table === "experiment_nanopore_id") {
        return dataService.createNanoPore(data);
      }
      throw new Error("Invalid table type");
    }
    try {
      console.log('herwe', table, data)
      const response = await apiCall(table, data);
      console.log('repsonse', response)
      const payload = {response: response.data, table}
      if (response.data[0].message.includes("had no changes.")) {
        message.info(`${payload.table} ${response.data[0].identifier} had no changes`);
        // Return a payload with a flag indicating no change
        return { response: [], table, noChanges: true };
      }
      message.success(`${payload.table} ${response.data[0].identifier} addd successfuly`);
      return payload

    } catch (error) {
      let errorMessage = "";

      // Check if there's a top-level errorMessage.
      if (error.response && error.response.message) {
        errorMessage = error.response.message;
        console.log("Top-level message:", errorMessage);
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
          errorMessage = firstError.data
            .map(err => `${err.field}: ${err.error}`)
            .join(", ");
        }
        // Otherwise, if the first element itself has 'field' and 'error', use those.
        else if (firstError.field && firstError.error) {
          errorMessage = `${firstError.field}: ${firstError.error}`;
        }
        // Otherwise, fall back to stringifying the first element.
        else {
          errorMessage = JSON.stringify(firstError);
        }
        console.log("Constructed message from response data:", errorMessage);
      }
      // Fallback generic message.
      else {
        errorMessage = "An unknown error occurred.";
        console.log("Fallback message:", errorMessage);
      }

      console.log("ERROR! ", error.response.data);
      message.error(errorMessage);
      return thunkAPI.rejectWithValue();
    }

  }
)

export const updateTable = createAsyncThunk(
  "updateTable",
  async ({table, data}, thunkAPI) => {
    const apiCall = (table, data) => {
      if (table === "participants") {
        return dataService.updateParticipant(data);
      }
      if (table === "families") {
        return dataService.updateFamily(data);
      }
      if (table === "genetic_findings") {
        return dataService.updateGeneticFindings(data);
      }
      if (table === "analytes") {
        return dataService.updateAnalyte(data);
      }
      if (table === "biobank_entries") {
        return dataService.updateBiobankEntries(data);
      }
      if (table === "phenotypes") {
        return dataService.updatePhenotype(data);
      }
      if (table === "experiment_stages") {
        return dataService.updateExperimentStage(data);
      }
      if (table === "experiment_dna_short_read_id") {
        console.log("stuff")
        return dataService.updateDnaShortRead(data);
      }
      if (table === "experiment_rna_short_read_id") {
        return dataService.updateRnaShortRead(data);
      }
      if (table === "experiment_pac_bio_id") {
        return dataService.updatePacBio(data);
      }
      if (table === "experiment_nanopore_id") {
        return dataService.updateNanoPore(data);
      }
      throw new Error("Invalid table type");
    }
    try {
      console.log('herwe', table, data)
      const response = await apiCall(table, data);
      console.log('repsonse', response)
      const payload = {response: response.data, table}
      if (response.data[0].message.includes("had no changes.")) {
        message.info(`${payload.table} ${response.data[0].identifier} had no changes`);
        // Return a payload with a flag indicating no change
        return { response: [], table, noChanges: true };
      }
      message.success(`${payload.table} ${response.data[0].identifier} updated successfuly`);
      return payload

    } catch (error) {
      let errorMessage = "";

      // Check if there's a top-level errorMessage.
      if (error.response && error.response.message) {
        errorMessage = error.response.message;
        console.log("Top-level message:", errorMessage);
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
          errorMessage = firstError.data
            .map(err => `${err.field}: ${err.error}`)
            .join(", ");
        }
        // Otherwise, if the first element itself has 'field' and 'error', use those.
        else if (firstError.field && firstError.error) {
          errorMessage = `${firstError.field}: ${firstError.error}`;
        }
        // Otherwise, fall back to stringifying the first element.
        else {
          errorMessage = JSON.stringify(firstError);
        }
        console.log("Constructed message from response data:", errorMessage);
      }
      // Fallback generic message.
      else {
        errorMessage = "An unknown error occurred.";
        console.log("Fallback message:", errorMessage);
      }

      console.log("ERROR! ", error.response.data);
      message.error(errorMessage);
      return thunkAPI.rejectWithValue();
    }

  }
)

export const {
  setJsonData,
  setTableView
} = dataSlice.actions;
export const dataReducer = dataSlice.reducer;