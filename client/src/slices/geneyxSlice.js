// slices/geneyxSlice.js
import geneyxService from "../services/geneyx.service";
import errorService from "../services/error.service";
import { message } from "antd";
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';  // combineSlices

const initialState = {
  jsonData: null,
  gsamples: [],
  gsample: null,
  gcases: [],
  gcase: null,
  gcaseNotes: null,
  status: "idle"
};

export const geneyxSlice = createSlice({
  name: 'geneyx',
  initialState,
  reducers: {
    setJsonData: (state, action) => {
      state.jsonData = action.payload;
    },
    clearJsonData: (state, action) => {
      state.jsonData = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(getSamples.pending, (state, action) => {
        state.status = "loading";
      })
      .addCase(getSamples.rejected, (state, action) => {
        state.status = "rejected";
      })
      .addCase(getSamples.fulfilled, (state, action) => {
        //const { gsamples } = action.payload;

        console.log(action.payload)
        state.status = "fullfiled";
      })
      .addCase(getSample.pending, (state, action) => {
        state.status = "loading"
      })
      .addCase(getSample.rejected, (state, action) => {
        state.status = "rejected"
      })
      .addCase(getSample.fulfilled, (state, action) => {
        state.status = "fulfilled"
        const { gsample } = action.payload;
        const { response } = action.response;
      })
      .addCase(getCases.pending, (state, action) => {
        state.status = "loading";
      })
      .addCase(getCases.rejected, (state, action) => {
        state.status = "rejected";
      })
      .addCase(getCases.fulfilled, (state, action) => {
        const {
          gcases
        } = action.payload;

        Object.assign(state, {
          gcases
        });
      })
      .addCase(getCase.pending, (state, action) => {
        state.status = "loading"
      })
      .addCase(getCase.rejected, (state, action) => {
        state.status = "rejected"
      })
      .addCase(getCase.fulfilled, (state, action) => {
        state.status = "fulfilled"
        const { gcase, response } = action.payload;
        if (state[gcase]) {
          state[gcase] = response
        }
      })
      .addCase(getCaseNotes.pending, (state, action) => {
        state.status = "loading"
      })
      .addCase(getCaseNotes.rejected, (state, action) => {
        state.status = "rejected"
      })
      .addCase(getCaseNotes.fulfilled, (state, action) => {
        state.status = "fulfilled"
        const { gcaseNotes, response } = action.payload;
        if (state[gcaseNotes]) {
          state[gcaseNotes] = response
        }
      })
  }
});

export const getSamples = createAsyncThunk(
  "getSamples",
  async (thunkAPI) => {
    try {
      const response = await geneyxService.getSamples();
      return response
    } catch(error) {
      message.error(errorService.printErrorMessages(error));
      return thunkAPI.rejectWithValue()
    }
  }
);

export const getSample = createAsyncThunk(
  "getSample",
  async (objectKey, thunkAPI) => {
    try {
      const response = await geneyxService.getSample(objectKey);
      return response.data
    } catch(error) {
      message.error(errorService.printErrorMessages(error));
      return thunkAPI.rejectWithValue()
    }
  }
);

export const getCases = createAsyncThunk(
  "getCases",
  async (thunkAPI) => {
    try {
      const response = await geneyxService.getCases();
      return response.data
    } catch(error) {
      message.error(errorService.printErrorMessages(error));
      return thunkAPI.rejectWithValue()
    }
  }
);

export const getCase = createAsyncThunk(
  "getCase",
  async (objectKey, thunkAPI) => {
    try {
      const response = await geneyxService.getCase(objectKey);
      return response.data
    } catch(error) {
      message.error(errorService.printErrorMessages(error));
      return thunkAPI.rejectWithValue()
    }
  }
);

export const getCaseNotes = createAsyncThunk(
  "getCaseNotes",
  async (objectKey, thunkAPI) => {
    try {
      const response = await geneyxService.getCaseNotes(objectKey);
      return response.data
    } catch(error) {
      message.error(errorService.printErrorMessages(error));
      return thunkAPI.rejectWithValue()
    }
  }
);

export const {
  setJsonData,
  clearJsonData
} = geneyxSlice.actions;
export const geneyxReducer = geneyxSlice.reducer;