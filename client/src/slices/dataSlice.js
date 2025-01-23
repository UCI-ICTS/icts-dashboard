// slices/dataSlice.js
import dataService from "../services/data.service";
import { combineSlices, createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { setMessage } from "./messageSlice";
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
      console.log(action.payload)
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(submitParticipant.fulfilled, (state, action) => {
        console.log(action.payload)
        state.jsonData = action.payload;
      })
      .addCase(getAllTables.pending, (state, action) => {
        state.status = "loading";
      })
      .addCase(getAllTables.rejected, (state, action) => {
        state.status = "rejected";
      })
      .addCase(getAllTables.fulfilled, (state, action) => {
        state.participants = action.payload.participants;
        state.families = action.payload.families;
        state.genetic_findings = action.payload.genetic_findings;
        state.analytes = action.payload.analytes;
        state.phenotypes = action.payload.phenotypes;
        state.experiments = action.payload.experiments;
        state.status = "idle";
      })
      .addCase(updateTable.fulfilled, (state, action) => {
        if (action.payload.table === 'participant_id') {
          const participant = action.payload.response[0].data.updated_instance
          const identifier = participant[action.payload.table]
          const updatedParticipant = state.participants.find(p => p.participant_id === identifier);
          if (updatedParticipant) {
            Object.assign(updatedParticipant, participant)
          }
        }
        state.status = "idle";
      })
      .addCase(updateTable.pending, (state, action) => {
        state.status = "loading";
      })
      .addCase(updateTable.rejected, (state, action) => {
        state.status = "rejected";
      })
  }
});


export const submitParticipant = createAsyncThunk(
  "submitParticipant",
  async ({data_list}, thunkAPI) => {
    try {
      console.log("slice", data_list)
      const response = await dataService.submitParticipant(data_list);
      console.log(response)
      return response.data
    } catch(error) {
      console.log("hadley",error)
    }
  }
)

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
    if (table === "participant_id") {
      console.log("slice", table)
      try {
        const response = await dataService.updateParticipant(data, token);
        const payload = {response: response.data, table}
        if (response.data[0].message.includes("had no changes.")) {
          thunkAPI.dispatch(setMessage(`${payload.table} ${response.data[0].identifier} had no changes`));
          return 0
        }
        thunkAPI.dispatch(setMessage(`${payload.table} ${response.data[0].identifier} updated successfuly`));
        return payload
      } catch(error) {
        console.log("ERROR! ",error.response)
        return thunkAPI.rejectWithValue(error.response.data);
      }
    }
    if (table === "family_id") {
      console.log("slice", table, data, token)
      try {
        // const response = await dataService.updateTable(data, token);
        thunkAPI.dispatch(setMessage(`${data[table]} updated successfully`));
        // return response.data
      } catch(error) {
        console.log("ERROR! ",error)
        return thunkAPI.rejectWithValue(error.response.data);
      }
    }
    if (table === "genetic_findings_id") {
      console.log("slice", table, data, token)
      try {
        const response = await dataService.updateTable(data, token);
        thunkAPI.dispatch(setMessage(`${data[table]} updated successfully`));
        return response.data
      } catch(error) {
        console.log("ERROR! ",error)
        return thunkAPI.rejectWithValue(error.response.data);
      }
    }
    if (table === "analyte_id") {
      console.log("slice", table, data, token)
      try {
        // const response = await dataService.updateTable(data, token);
        thunkAPI.dispatch(setMessage(`${data[table]} updated successfully`));
        // return response.data
      } catch(error) {
        console.log("ERROR! ",error)
        return thunkAPI.rejectWithValue(error.response.data);
      }
    }
    if (table === "phenotype_id") {
      console.log("slice", table, data, token)
      try {
        // const response = await dataService.updateTable(data, token);
        thunkAPI.dispatch(setMessage(`${data[table]} updated successfully`));
        // return response.data
      } catch(error) {
        console.log("ERROR! ",error)
        return thunkAPI.rejectWithValue(error.response.data);
      }
    }
    if (table === "experiment_id") {
      console.log("slice", table, data, token)
      try {
        // const response = await dataService.updateTable(data, token);
        thunkAPI.dispatch(setMessage(`${data[table]} updated successfully`));
        // return response.data
      } catch(error) {
        console.log("ERROR! ",error)
        return thunkAPI.rejectWithValue(error.response.data);
      }
    }
  }
)

export const {
  setJsonData,
  setTableView
} = dataSlice.actions;
export const dataReducer = dataSlice.reducer;