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


const getCSRFToken = async () => {
  await axios.get("/api/health/"); // sets cookie
};

function getCookie(name) {
  const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  if (match) return match[2];
  return null;
}

// utility to fetch the cookie and inject it into headers
const postWithCSRF = async (url, data) => {
  const csrftoken = getCookie("csrftoken");
  return axios.post(url, data, {
    headers: {
      "X-CSRFToken": csrftoken,
      "Content-Type": "application/json"
    },
    withCredentials: true, // ensures browser includes cookies
  });
};


// ✅ user log in
const login = async (username, password) => {
  const response = await postWithCSRF(APIDB + "api/auth/token/login/", {
    username,
    password,
  });
  return response.data;
};

// ✅ user log out (blacklist token)
const logout = async (refresh_token) => {
  const response = await axios.post(APIDB + "api/auth/token/logout/", {
    refresh: refresh_token
  });
  return response.data;
};
  
// ✅ user change password
const changePassword = (values) => {
  console.log("service values: ", values)
  return axios.post(APIDB + "api/auth/password/change/", {
    old_password: values.old_password,
    new_password: values.new_password,
    confirm_new_password: values.confirm_password
  }, {
    headers: getAuthHeaders(),
  })
};

// ✅ password reset received via email
const resetPassword = async (email) => {
  console.log("Service password reset: ", email);
  const response = await postWithCSRF(APIDB + "api/auth/password/reset/", {
    email,
  });
  return response.data;
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

// ✅ activate user/create password received via email
const createPassword = async ({ uid, token, new_password }) => {
  console.log("Service password create: ", uid, token, new_password);
  const response = await axios.post(`${APIDB}api/auth/users/activate/`, {
    uid,
    token,
    new_password,
  })
  return response.data;
};

// ✅ Update an existing user
const updateUser = async (userData) => {
  const response = await axios.put(APIDB + `api/auth/users/${userData.username}/`, userData, { headers: getAuthHeaders() });
  return response.data;
};

// ✅ Delete a user
const deleteUser = async (userId) => {
  // handle special characters
  const encodedUsername = encodeURIComponent(userId);
  await axios.delete(APIDB + `api/auth/users/${encodedUsername}/`, { headers: getAuthHeaders() });
};

  const accountService = {
    getCSRFToken,
    login,
    logout,
    changePassword,
    resetPassword,
    getUsers,
    createUser,
    createPassword,
    updateUser,
    deleteUser
  };
  
  export default accountService;