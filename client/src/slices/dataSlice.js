// slices/dataSlice.js
import dataService from "../services/data.service";
import errorService from "../services/error.service";
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';  // combineSlices
import { message } from "antd";
import { getCollectionName, getTableName } from "../utils/tableNameMap";

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
          participants,
          families,
          genetic_findings,
          analytes,
          biobank_entries,
          phenotypes,
          experiments,
          experiment_dna_short_read,
          experiment_rna_short_read,
          experiment_pac_bio,
          experiment_nanopore,
          aligned,
          aligned_dna_short_read,
          aligned_nanopore,
          aligned_pac_bio,
          aligned_rna_short_read
        } = action.payload;

        Object.assign(state, {
          participants,
          families,
          genetic_findings,
          analytes,
          biobank_entries,
          phenotypes,
          experiments,
          experiment_dna_short_read,
          experiment_rna_short_read,
          experiment_pac_bio,
          experiment_nanopore,
          aligned,
          aligned_dna_short_read,
          aligned_nanopore,
          aligned_pac_bio,
          aligned_rna_short_read,
          status: "fulfilled"
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
          const collectionName = table === "participants" ? "participant" :
                                 table === "families" ? "families" :
                                 table === "genetic_findings" ? "genetic_findings" :
                                 table === "analyte" ? "analytes" :
                                 table === "biobank_entries" ? "biobank_entries" :
                                 table === "phenotypes" ? "phenotypes" :
                                 table === "experiments" ? "experiments" :
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
        // Extract the added object from the response
        const addedObject = response[0]?.data?.instance;

        if (addedObject && table) {
          // Extract the identifier value dynamically using the table name
          const identifier = addedObject[table];
          // Dynamically determine the collection to add based on the table name
          const collectionName = table === "participants" ? "participants" :
                                 table === "families" ? "families" :
                                 table === "genetic_findings" ? "genetic_findings" :
                                 table === "analytes" ? "analytes" :
                                 table === "biobank_entries" ? "biobank_entries" :
                                 table === "phenotypes" ? "phenotypes" :
                                 table === "experiments" ? "experiments" :
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
              Object.assign(objectToUpdate, addedObject);
            }
          }
        }
      })
      .addCase(addTable.pending, (state, action) => {
        state.status = "loading";
      })
      .addCase(addTable.rejected, (state, action) => {
        state.status = "rejected";
      })
      .addCase(deleteEntry.fulfilled, (state, action) => {
        state.status = "fulfilled";

        const { table, idList } = action.meta.arg;

        // Normalize idList in case it's a single ID or an array of IDs
        const idsToRemove = Array.isArray(idList) ? idList : [idList];
        const stateTable = getTableName(table)
        console.log("Before delete:", table, stateTable, idList, );
        if (state[stateTable]) {
          state[stateTable] = state[stateTable].filter(
            (entry) => !idsToRemove.includes(entry[`${table}_id`])
          );
        }
        console.log(action.meta.arg)
      })
      .addCase(deleteEntry.pending, (state, action) => {
        state.status = "loading";
      })
      .addCase(deleteEntry.rejected, (state, action) => {
        state.status = "rejected";
      })
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
      if (table === "families") {
        return dataService.createFamily(data);
      }
      if (table === "participants") {
        return dataService.createParticipant(data);
      }
      if (table === "phenotypes") {
        return dataService.createPhenotype(data);
      }
      if (table === "analytes") {
        return dataService.createAnalyte(data);
      }
      if (table === "genetic_findings") {
        return dataService.createGeneticFindings(data);
      }
      if (table === "biobank_entries") {
        return dataService.createBiobankEntries(data);
      }
      if (table === "experiment_id") {
        return dataService.createExperiment(data);
      }
      if (table === "experiment_dna_short_read_id") {
        return dataService.createExpDnaShortRead(data);
      }
      if (table === "experiment_rna_short_read_id") {
        return dataService.createExpRnaShortRead(data);
      }
      if (table === "experiment_pac_bio_id") {
        return dataService.createExpPacBio(data);
      }
      if (table === "experiment_nanopore_id") {
        return dataService.createExpNanopore(data);
      }
      if (table === "aligned_id") {
        return dataService.createAligned(data);
      }
      if (table === "aligned_dna_short_read_id") {
        return dataService.createAlnDnaShortRead(data);
      }
      if (table === "aligned_rna_short_read_id") {
        return dataService.createAlnRnaShortRead(data);
      }
      if (table === "aligned_pac_bio_id") {
        return dataService.createAlnPacBio(data);
      }
      if (table === "aligned_nanopore_id") {
        return dataService.createAlnNanopore(data);
      }
      throw new Error("Invalid table type");
    }
    try {
      const response = await apiCall(table, data);
      const payload = {response: response.data, table}
      if (response.data[0].message.includes("had no changes.")) {
        message.info(`${payload.table} ${response.data[0].identifier} had no changes`);

        // Return a payload with a flag indicating no change
        return { response: [], table, noChanges: true };
      }
      message.success(`${payload.table} ${response.data[0].identifier} added successfuly`);
      return payload

    } catch (error) {
      message.error(`${errorService.printErrorMessages(error)}`);
      return thunkAPI.rejectWithValue();
    }
  }
)

export const getTable = createAsyncThunk(
  "getTable",
  async ({table}, thunkAPI) => {
    const apiCall = (table) => {
      if (table === "family_id") {
        return dataService.getFamilyTable();
      }
      if (table === "participant_id") {
        return dataService.getParticipantTable();
      }
      if (table === "phenotype_id") {
        return dataService.getPhenotypeTable();
      }
      if (table === "analyte_id") {
        return dataService.getAnalyteTable();
      }
      if (table === "genetic_findings_id") {
        return dataService.getGeneticFindingsTable();
      }
      if (table === "biobank_id") {
        return dataService.getBiobankEntriesTable();
      }
      if (table === "experiment_id") {
        return dataService.getExperimentTable();
      }
      if (table === "experiment_dna_short_read_id") {
        return dataService.getExpDnaShortReadTable();
      }
      if (table === "experiment_rna_short_read_id") {
        return dataService.getExpRnaShortReadTable();
      }
      if (table === "experiment_pac_bio_id") {
        return dataService.getExpPacBioTable();
      }
      if (table === "experiment_nanopore_id") {
        return dataService.getExpNanoporeTable();
      }
      if (table === "aligned_id") {
        return dataService.getAlignedTable();
      }
      if (table === "aligned_dna_short_read_id") {
        return dataService.getAlnDnaShortReadTable();
      }
      if (table === "aligned_rna_short_read_id") {
        return dataService.getAlnRnaShortReadTable();
      }
      if (table === "aligned_pac_bio_id") {
        return dataService.getAlnPacBioTable();
      }
      if (table === "aligned_nanopore_id") {
        return dataService.getAlnNanoporeTable();
      }
      throw new Error("Invalid table type");
    }
    try {
      console.log('Get', table)
      const response = await apiCall(table);
      console.log('response', response)
      const payload = {response: response.data, table}
      message.success(`${payload.table} ${response.data[0].identifier} retrieved successfuly`);
      return payload

    } catch (error) {
      message.error(errorService.printErrorMessages(error));
      return thunkAPI.rejectWithValue();
    }
  }
)

export const updateTable = createAsyncThunk(
  "updateTable",
  async ({table, data}, thunkAPI) => {
    try {
      console.log('herwe', table, data)
      const response = await dataService.updateEntry(table, data);
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
      message.error(errorService.printErrorMessages(error));
      return thunkAPI.rejectWithValue();
    }
  }
)

export const deleteTable = createAsyncThunk(
  "deleteTable",
  async ({table, data}, thunkAPI) => {
    const apiCall = (table, data) => {
      if (table === "families") {
        return dataService.deleteFamily(data);
      }
      if (table === "participants") {
        return dataService.deleteParticipant(data);
      }
      if (table === "phenotypes") {
        return dataService.deletePhenotype(data);
      }
      if (table === "analytes") {
        return dataService.deleteAnalyte(data);
      }
      if (table === "genetic_findings") {
        return dataService.deleteGeneticFindings(data);
      }
      if (table === "biobank_entries") {
        return dataService.deleteBiobankEntries(data);
      }
      if (table === "experiment_id") {
        return dataService.deleteExperiment(data);
      }
      if (table === "experiment_dna_short_read_id") {
        return dataService.deleteExpDnaShortRead(data);
      }
      if (table === "experiment_rna_short_read_id") {
        return dataService.deleteExpRnaShortRead(data);
      }
      if (table === "experiment_pac_bio_id") {
        return dataService.deleteExpPacBio(data);
      }
      if (table === "experiment_nanopore_id") {
        return dataService.deleteExpNanopore(data);
      }
      if (table === "aligned_id") {
        return dataService.deleteAligned(data);
      }
      if (table === "aligned_dna_short_read_id") {
        return dataService.deleteAlnDnaShortRead(data);
      }
      if (table === "aligned_rna_short_read_id") {
        return dataService.deleteAlnRnaShortRead(data);
      }
      if (table === "aligned_pac_bio_id") {
        return dataService.deleteAlnPacBio(data);
      }
      if (table === "aligned_nanopore_id") {
        return dataService.deleteAlnNanopore(data);
      }
      throw new Error("Invalid table type");
    }
    try {
      console.log('Delete', table, data)
      const response = await apiCall(table, data);
      console.log('response', response)
      const payload = {response: response.data, table}
      message.success(`${payload.table} ${response.data[0].identifier} deleted successfuly`);
      return payload

    } catch (error) {
      message.error(errorService.printErrorMessages(error));
      return thunkAPI.rejectWithValue();
    }
  }
)

export const deleteEntry = createAsyncThunk(
  "deleteEntry",
  async ({table, idList}, thunkAPI) => {
    const response = await dataService.deleteEntry(table, idList)
    console.log("slice", response)
  });

export const {
  setJsonData,
  setTableView
} = dataSlice.actions;
export const dataReducer = dataSlice.reducer;