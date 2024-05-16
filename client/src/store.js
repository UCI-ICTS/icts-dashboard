import { configureStore } from "@reduxjs/toolkit"
import { accountReducer } from "./slices/accountSlice"
import { messageReducer } from "./slices/messageSlice"

export const store = configureStore({
  reducer: {
    account: accountReducer,
    message: messageReducer,
  }
})