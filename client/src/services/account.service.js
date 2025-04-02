// src/services/account.service.js

import axios from "axios";
import { store } from "../store";

const APIDB = process.env.REACT_APP_APIDB;

const getAuthHeaders = () => {
  const state = store.getState();
  const token = state.account.user.access_token;

  if (!token) {
    throw new Error("No authentication token found.");
  }

  return {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json",
  };
};

const login = async (username, password) => {
  const response = await axios.post(APIDB + "api/auth/login/", {
    username,
    password,
  });
  return response.data;
  };

const logout = async (refresh_token) => {
  const response = await axios.post(APIDB + "api/auth/logout/", {
    refresh: refresh_token
  });
  return response.data;
  };
  
const changePassword = (values) => {
  console.log("service values: ", values)
  return axios.post(APIDB + "/api/auth/change_password/", {
    old_password: values.old_password,
    new_password: values.new_password,
    confirm_new_password: values.confirm_password
  }, {
    headers: getAuthHeaders(),
  })
};

// ✅ Fetch all users
const getUsers = async () => {
  const response = await axios.get(APIDB + "api/auth/users/", { headers: getAuthHeaders() });
  return response.data;
};

// ✅ Create a new user
const createUser = async (userData) => {
  const response = await axios.post(APIDB + "api/auth/users/", userData, { headers: getAuthHeaders() });
  return response.data;
};

// ✅ Update an existing user
const updateUser = async (userData) => {
  const response = await axios.put(APIDB + `api/auth/users/${userData.username}/`, userData, { headers: getAuthHeaders() });
  return response.data;
};

// ✅ Delete a user
const deleteUser = async (userId) => {
  await axios.delete(APIDB + `api/auth/users/${userId}/`, { headers: getAuthHeaders() });
};

  const accountService = {
    login,
    logout,
    changePassword,
    getUsers,
    createUser,
    updateUser,
    deleteUser
  };
  
  export default accountService;