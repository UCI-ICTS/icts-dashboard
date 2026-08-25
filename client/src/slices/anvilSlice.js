// src/slices/anvilSlice.js

import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { message } from "antd";

import anvilService from "../services/anvil.services";
import errorService from "../services/error.service";


const getErrorMessage = (error) => {
  return errorService.printErrorMessages(error);
};


const getUploadFromActionPayload = (payload) => {
  if (!payload) return null;

  // Some workflow endpoints return the upload directly.
  if (payload.upload_id) return payload;

  // Some workflow endpoints return { upload, summary, ... }.
  if (payload.upload) return payload.upload;

  return null;
};


export const fetchAnvilUploads = createAsyncThunk(
  "anvil/fetchUploads",
  async (_, thunkAPI) => {
    try {
      const response = await anvilService.fetchAnvilUploadsService();

      return Array.isArray(response.data)
        ? response.data
        : response.data?.results || [];
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      message.error(errorMessage);
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);


export const fetchAnvilUploadDetail = createAsyncThunk(
  "anvil/fetchUploadDetail",
  async (uploadId, thunkAPI) => {
    try {
      const response = await anvilService.fetchAnvilUploadDetailService(uploadId);
      return response.data;
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      message.error(errorMessage);
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);


export const createAnvilUpload = createAsyncThunk(
  "anvil/createUpload",
  async (payload, thunkAPI) => {
    try {
      const response = await anvilService.createAnvilUploadService(payload);
      message.success("AnVIL upload created.");
      return response.data;
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      message.error(errorMessage);
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);


export const initializeAnvilUpload = createAsyncThunk(
  "anvil/initializeUpload",
  async (uploadId, thunkAPI) => {
    try {
      const response = await anvilService.initializeAnvilUploadService(uploadId);
      message.success("Upload package initialized.");
      return response.data;
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      message.error(errorMessage);
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);


export const validateAnvilSource = createAsyncThunk(
  "anvil/validateSource",
  async (uploadId, thunkAPI) => {
    try {
      const response = await anvilService.validateAnvilSourceService(uploadId);

      if (response.data?.passed === false) {
        message.warning("Source validation completed with errors.");
      } else {
        message.success("Source validation passed.");
      }

      return response.data;
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      message.error(errorMessage);
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);


export const generateAnvilTsvs = createAsyncThunk(
  "anvil/generateTsvs",
  async ({ uploadId }, thunkAPI) => {
    try {
      const response = await anvilService.generateAnvilTsvsService({uploadId});
      message.success("AnVIL TSVs generated.");
      return response.data;
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      message.error(errorMessage);
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);


export const generateAnvilManifest = createAsyncThunk(
  "anvil/generateManifest",
  async ({ uploadId }, thunkAPI) => {
    try {
      const response = await anvilService.generateAnvilManifestService({uploadId});
      message.success("AnVIL upload manifest generated.");
      return response.data;
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      message.error(errorMessage);
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);


export const validateAnvilPackage = createAsyncThunk(
  "anvil/validatePackage",
  async (uploadId, thunkAPI) => {
    try {
      const response = await anvilService.validateAnvilPackageService(uploadId);

      if (response.data?.passed === false) {
        message.warning("Package validation completed with errors.");
      } else {
        message.success("Package validation passed.");
      }

      return response.data;
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      message.error(errorMessage);
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);


const initialState = {
  uploads: [],
  selectedUpload: null,

  // List/detail loading.
  status: "idle",

  // Workflow action loading.
  actionStatus: "idle",
  activeAction: null,

  error: null,
  lastActionResult: null,
};


const setActionPending = (state, activeAction) => {
  state.actionStatus = "loading";
  state.activeAction = activeAction;
  state.error = null;
};


const setActionFulfilled = (state, action) => {
  state.actionStatus = "fulfilled";
  state.activeAction = null;
  state.lastActionResult = action.payload;

  const upload = getUploadFromActionPayload(action.payload);

  if (upload) {
    state.selectedUpload = upload;
  }
};


const setActionRejected = (state, action) => {
  state.actionStatus = "failed";
  state.activeAction = null;
  state.error = action.payload || action.error.message;
};


const anvilSlice = createSlice({
  name: "anvil",
  initialState,
  reducers: {
    clearSelectedAnvilUpload: (state) => {
      state.selectedUpload = null;
    },
    clearAnvilError: (state) => {
      state.error = null;
    },
    clearAnvilLastActionResult: (state) => {
      state.lastActionResult = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch uploads list.
      .addCase(fetchAnvilUploads.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(fetchAnvilUploads.fulfilled, (state, action) => {
        state.status = "fulfilled";
        state.uploads = action.payload;
      })
      .addCase(fetchAnvilUploads.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload || action.error.message;
      })

      // Fetch one upload detail.
      .addCase(fetchAnvilUploadDetail.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(fetchAnvilUploadDetail.fulfilled, (state, action) => {
        state.status = "fulfilled";
        state.selectedUpload = action.payload;
      })
      .addCase(fetchAnvilUploadDetail.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload || action.error.message;
      })

      // Create upload.
      .addCase(createAnvilUpload.pending, (state) => {
        setActionPending(state, "createAnvilUpload");
      })
      .addCase(createAnvilUpload.fulfilled, (state, action) => {
        setActionFulfilled(state, action);

        if (action.payload?.upload_id) {
          const exists = state.uploads.some(
            (upload) => upload.upload_id === action.payload.upload_id
          );

          if (!exists) {
            state.uploads = [action.payload, ...state.uploads];
          }
        }
      })
      .addCase(createAnvilUpload.rejected, setActionRejected)

      // Initialize package.
      .addCase(initializeAnvilUpload.pending, (state) => {
        setActionPending(state, "initializeAnvilUpload");
      })
      .addCase(initializeAnvilUpload.fulfilled, setActionFulfilled)
      .addCase(initializeAnvilUpload.rejected, setActionRejected)

      // Validate source.
      .addCase(validateAnvilSource.pending, (state) => {
        setActionPending(state, "validateAnvilSource");
      })
      .addCase(validateAnvilSource.fulfilled, setActionFulfilled)
      .addCase(validateAnvilSource.rejected, setActionRejected)

      // Generate TSVs.
      .addCase(generateAnvilTsvs.pending, (state) => {
        setActionPending(state, "generateAnvilTsvs");
      })
      .addCase(generateAnvilTsvs.fulfilled, setActionFulfilled)
      .addCase(generateAnvilTsvs.rejected, setActionRejected)

      // Generate manifest.
      .addCase(generateAnvilManifest.pending, (state) => {
        setActionPending(state, "generateAnvilManifest");
      })
      .addCase(generateAnvilManifest.fulfilled, setActionFulfilled)
      .addCase(generateAnvilManifest.rejected, setActionRejected)

      // Validate package.
      .addCase(validateAnvilPackage.pending, (state) => {
        setActionPending(state, "validateAnvilPackage");
      })
      .addCase(validateAnvilPackage.fulfilled, setActionFulfilled)
      .addCase(validateAnvilPackage.rejected, setActionRejected);
  },
});


export const {
  clearSelectedAnvilUpload,
  clearAnvilError,
  clearAnvilLastActionResult,
} = anvilSlice.actions;

export default anvilSlice.reducer;