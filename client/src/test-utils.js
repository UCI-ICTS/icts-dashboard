// src/test-utils.js 

import React from "react";
import { configureStore } from "@reduxjs/toolkit";
import { Provider } from "react-redux";
import { render } from "@testing-library/react";
import { messageReducer } from "./slices/messageSlice";
import { accountReducer } from "./slices/accountSlice";

export function renderWithProviders(
  ui,
  {
    preloadedState = { 
      message: { message: "" },
      account: { isLoggedIn: false, user: null, loading: false }
    },
    store = configureStore({
      reducer: {
        message: messageReducer,
        account: accountReducer
      },
      preloadedState
    }),
    ...renderOptions
  } = {}
) {
  const Wrapper = ({ children }) => (
    <Provider store={store}>
      {children}
    </Provider>
  );

  return { store, ...render(ui, { wrapper: Wrapper, ...renderOptions }) };
}
