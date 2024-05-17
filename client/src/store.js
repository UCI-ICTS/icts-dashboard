import { configureStore } from "@reduxjs/toolkit"
import { accountReducer } from "./slices/accountSlice"
import { messageReducer } from "./slices/messageSlice"
import { dataReducer, dataSlice } from "./slices/dataSlice"

export const store = configureStore({
  reducer: {
    account: accountReducer,
    message: messageReducer,
    data: dataReducer,
  }
})