// slices/dataSlice.js
import dataService from "../services/data.service";
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';

const initialState = {
  tableView: "participants",
  jsonData: [],
  participants: [],
  families: [],
  genetic_findings: [],
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
      state.tableView = action.payload.identifier;
      console.log(action.payload)
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(submitParticipant.fulfilled, (state, action) => {
        console.log(action.payload)
        state.jsonData = action.payload;
      })
      .addCase(getAllParticipants.fulfilled, (state, action) => {
        console.log("thing", action.payload)
        state.participants = action.payload.participants;
        state.families = action.payload.families;
        state.genetic_findings = action.payload.genetic_findings;
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

export const getAllParticipants = createAsyncThunk(
  "getAllParticipants",
  async ({token}, thunkAPI) => {
    try {
      const response = await dataService.getAllParticipants(token);
      return response.data
    } catch(error) {
      console.log("ERROR! ",error)
    }
  }
)

export const {
  setJsonData,
  setTableView
} = dataSlice.actions;
export const dataReducer = dataSlice.reducer;