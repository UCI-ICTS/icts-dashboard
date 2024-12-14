import { createSlice } from "@reduxjs/toolkit";

const initialState = {message: ""};

const messageSlice = createSlice({
  name: "message",
  initialState,
  reducers: {
    setMessage: (state, action) => {
      return { message: action.payload };
    },
    clearMessage: () => {
      return { message: "" };
    },
  },
});

export const messageReducer = messageSlice.reducer;
export const {
  setMessage,
  clearMessage
} = messageSlice.actions;
