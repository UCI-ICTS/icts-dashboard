// src/store.js

import { configureStore } from "@reduxjs/toolkit"
import { accountReducer } from "./slices/accountSlice"
import { dataReducer } from "./slices/dataSlice"
import { uiReducer } from "./slices/uiSlice"

export const store = configureStore({
  reducer: {
    account: accountReducer,
    data: dataReducer,
    ui: uiReducer
  }
})