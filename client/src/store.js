// src/store.js

import { configureStore } from "@reduxjs/toolkit"
import { accountReducer } from "./slices/accountSlice"
import { dataReducer } from "./slices/dataSlice"
import { geneyxReducer } from "./slices/geneyxSlice"

export const store = configureStore({
  reducer: {
    account: accountReducer,
    data: dataReducer,
    geneyx: geneyxReducer
  }
})