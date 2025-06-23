// src/api.js

import axios from "axios";
import { message } from "antd";
import {store} from "./store";
import { logout } from "./slices/accountSlice";

const api = axios.create({
  baseURL: `${process.env.REACT_APP_API_URL || ""}/api/`,
  withCredentials: true,
});

// Attach token if available
api.interceptors.request.use((config) => {
  const token = store.getState()?.account?.user?.access_token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle errors globally
api.interceptors.response.use(
  response => response,
  error => {
    if (!error.response) {
      message.error("Cannot connect to server. Please check your network.");
    } else if (error.response.status === 401) {
      store.dispatch(logout());
      message.error("Session expired. Please log in again.");
    } else if (error.response.status >= 500) {
      message.error("Server error. Please try again later.");
    }
    return Promise.reject(error);
  }
);

export default api;
