// slices/dataSlice.js
import dataService from "../services/data.service";
import errorService from "../services/error.service";
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';  // combineSlices
import { message } from "antd";
import { getCollectionName, getTableName } from "../utils/schemaAndTables";

const initialState = {
  tableView: "participants",
  tableID: "participant_id",
  tableName: "Participants",
  jsonData: null,
  familyDetail: null,
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
    clearJsonData: (state, action) => {
      state.jsonData = null;
    },
    clearFamilyDetail: (state, action) => {
      state.familyDetail = null;
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
      .addCase(fetchTable.pending, (state, action) => {
        state.status = "loading"
      })
      .addCase(fetchTable.rejected, (state, action) => {
        state.status = "rejected"
      })
      .addCase(fetchTable.fulfilled, (state, action) => {
        state.status = "fulfilled"
        const { table, response } = action.payload;
        const stateTable = getTableName(table)
        if (state[stateTable]) {
          state[stateTable] = response
        }
      })
      .addCase(updateEntry.fulfilled, (state, action) => {
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
          const collectionName = table

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
      .addCase(updateEntry.pending, (state, action) => {
        state.status = "loading";
      })
      .addCase(updateEntry.rejected, (state, action) => {
        state.status = "rejected";
      })
      .addCase(createEntry.fulfilled, (state, action) => {
        state.status = "fulfilled";
        const { table, response, noChanges } = action.payload;
        console.log(table, response)

        // Extract the added object from the response
        const addedObject = response[0]?.data?.instance;
        console.log(addedObject[table])
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
      .addCase(createEntry.pending, (state, action) => {
        state.status = "loading";
      })
      .addCase(createEntry.rejected, (state, action) => {
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
      .addCase(familyDetail.pending, (state, action) => {
        state.status = "loading";
      })
      .addCase(familyDetail.rejected, (state, action) => {
        state.status = "rejected";
      })
      .addCase(familyDetail.fulfilled, (state, action) => {
        state.familyDetail = action.payload
        state.status = "fulfilled";
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

export const familyDetail = createAsyncThunk(
  "familyDetail",
  async (participant_id, thunkAPI) => {
    try {
      const response = await dataService.familyDetail(participant_id);
      return response.data
    } catch(error) {
      message.error(errorService.printErrorMessages(error));
      return thunkAPI.rejectWithValue()
    }
  }
)

export const fetchTable = createAsyncThunk(
  "fetchTable",
  async (table, thunkAPI) => {
    try {
      const response = await dataService.fetchTable(table);
      const payload = {response: response.data, table}
      return payload
    } catch(error) {
      message.error(errorService.printErrorMessages(error));
      return thunkAPI.rejectWithValue()
    }
  }
)

export const createEntry = createAsyncThunk(
  "createEntry",
  async ({table, data}, thunkAPI) => {
    try {
      const response = await dataService.createEntry(table, data);
      const payload = {response: response.data, table}
      message.success(`${payload.table} ${response.data[0].identifier} updated successfuly`);
      return payload
    } catch (error) {
      message.error(errorService.printErrorMessages(error));
      return thunkAPI.rejectWithValue();
    }
  }
)

export const updateEntry = createAsyncThunk(
  "updateEntry",
  async ({table, data}, thunkAPI) => {
    try {
      const response = await dataService.updateEntry(table, data);
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

export const deleteEntry = createAsyncThunk(
  "deleteEntry",
  async ({table, idList}, thunkAPI) => {
    try {
      const response = await dataService.deleteEntry(table, idList)
      const payload = {response: response.data, table}
      console.log("slice", response)
      message.success(`${payload.table} ${response.data[0].identifier} deleted successfuly`);
    } catch(error) {
      message.error(errorService.printErrorMessages(error));
      return thunkAPI.rejectWithValue()
    }
  }
)

export const {
  setJsonData,
  clearJsonData,
  setTableView
} = dataSlice.actions;
export const dataReducer = dataSlice.reducer;