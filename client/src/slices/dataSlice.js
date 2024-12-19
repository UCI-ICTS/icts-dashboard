// slices/dataSlice.js
import dataService from "../services/data.service";
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';

const initialState = {
  jsonData: null,
  participnats: null, 
};

export const dataSlice = createSlice({
  name: 'data',
  initialState,
  reducers: {
    setJsonData: (state, action) => {
      state.jsonData = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(submitParticipant.fulfilled, (state, action) => {
        console.log(action.payload)
        state.jsonData = action.payload;
      })
      .addCase(getAllParticipants.fulfilled, (state, action) => {
        console.log(action.payload)
        state.participnats = action.payload;
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

export const { setJsonData } = dataSlice.actions;
export const dataReducer = dataSlice.reducer;