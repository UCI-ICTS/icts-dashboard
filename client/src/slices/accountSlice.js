// accountSlice

import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { setMessage } from "./messageSlice";
import AuthService from "../services/auth.service";

const user = JSON.parse(localStorage.getItem("user"));

const initialState = user
  ? { isLoggedIn: true, user }
  : { isLoggedIn: false, user: null };

  export const accountSlice = createSlice({
    name: "account",
    initialState,
    extraReducers: (builder) => {

    }
})

export const login = createAsyncThunk(
  "auth/login",
  async ({ username, password }, thunkAPI) => {
    try {
      const data = await AuthService.login(username, password);
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