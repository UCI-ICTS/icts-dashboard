// slices/dataSlice.js
import dataService from "../services/data.service";
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';

const initialState = {
  tableView: null,
  jsonData: null,
  participants: null,
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
        console.log(action.payload)
        state.participants = action.payload;
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
      console.log("slice get participants")
      const response = await dataService.getAllParticipants(token);
      return response.data
    } catch(error) {
      console.log("hadley",error)
    }
  }
)

export const {
  setJsonData,
  setTableView
} = dataSlice.actions;
export const dataReducer = dataSlice.reducer;