// accountSlice

import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { setMessage } from "./messageSlice";
import AccountService from "../services/account.service";
import { jwtDecode } from "jwt-decode";

const user = JSON.parse(localStorage.getItem("user"));

const initialState = user
  ? { isLoggedIn: true, user, loading: false }
  : { isLoggedIn: false, user: null, loading: false };

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
          console.log(action.payload)
          const payload = action.payload.data
          const user = jwtDecode(action.payload.data.access)
          user["refresh_token"] = payload.refresh
          user["access_token"] = payload.access
          delete user.token_type
          console.log(user)
          state.user = user;
          if (action.payload.rememberMe === true) {
            localStorage.setItem("user", JSON.stringify(user));
          }
        })
        .addCase(login.rejected, (state) => {
          state.loading = false; // Set loading to false when login is rejected
          state.isLoggedIn = false;
          state.user = null;
        })
        .addCase(handleExpiredJWT.fulfilled, (state, action) => {
          state.loading = false; // Set loading to false when login is rejected
          state.isLoggedIn = false;
          state.user = null;
        })
        .addCase(handleExpiredJWT.pending, (state, action) => {
          console.log("pending")
          state.loading = true; // Set loading to true when logout is pending
        })
        .addCase(handleExpiredJWT.rejected, (state, action) => {
          console.log("rejected")
        })
        .addCase(logout.pending, (state) => {
          console.log("logout pending")
          state.loading = true;
        })
        .addCase(logout.rejected, (state) => {
          state.loading = false;
          localStorage.removeItem("user")
          state.loading = false; // Set loading to false when logout is processed
          state.isLoggedIn = false;
          state.user = null;
          console.log("Token blacklist rejected")
        })
        .addCase(logout.fulfilled, (state) => {
          localStorage.removeItem("user")
          console.log("logout fulfilled")
          state.loading = false; // Set loading to false when logout is processed
          state.isLoggedIn = false;
          state.user = null;

        })
    }
})

export const login = createAsyncThunk(
  "auth/login",
  async ({ username, password, rememberMe }, thunkAPI) => {
    try {
      const data = await AccountService.login(username, password);
      return { data, rememberMe };
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

export const logout = createAsyncThunk(
  "auth/logout",
  async ({ token }, thunkAPI) => {
    console.log("slice",token)
    try {
      const data = await AccountService.logout(token);
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

export const handleExpiredJWT = createAsyncThunk(
  "account/handleExpiredJWT",
  async () => {
    try {
      localStorage.removeItem("user");
      // global.window.location.reload()
      return "Logged out due to expired session"
    } catch (error) {
      return error;
    }
  }
);

export const accountReducer = accountSlice.reducer