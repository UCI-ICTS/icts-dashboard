// accountSlice

import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { setMessage } from "./messageSlice";
import AccountService from "../services/account.service";

const user = JSON.parse(localStorage.getItem("user"));

const initialState = user
  ? { isLoggedIn: true, user }
  : { isLoggedIn: false, user: null };

  export const accountSlice = createSlice({
    name: "account",
    initialState,
    extraReducers: (builder) => {
      builder
        .addCase(login.pending, (state) => {
          state.loading = true; // Set loading to true when login is pending
        })
        .addCase(login.fulfilled, (state, action) => {
          state.loading = false; // Set loading to false when login is fulfilled
          state.isLoggedIn = true;
          state.user = action.payload.user;
        })
        .addCase(login.rejected, (state) => {
          state.loading = false; // Set loading to false when login is rejected
          state.isLoggedIn = false;
          state.user = null;
        })
    }
})

export const login = createAsyncThunk(
  "auth/login",
  async ({ username, password }, thunkAPI) => {
    try {
      console.log("slice error")
      const data = await AccountService.login(username, password);
      return { data };
    } catch (error) {
      const message =
        (error &&
          error.message) ||
          error.non_field_errors[0] ||
        error.toString();
      thunkAPI.dispatch(setMessage(message));
      return thunkAPI.rejectWithValue();
    }
  }
);

export const accountReducer = accountSlice.reducer