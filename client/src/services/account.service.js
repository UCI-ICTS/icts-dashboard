// src/services/account.service.js

import api from "../api";
import { message } from "antd";

// Get CSRF token by pinging health check
const getCSRFToken = async () => {
  try {
    await api.get("health/");
  } catch (error) {
    console.warn("⚠️ Failed to get CSRF token:", error.message);
    message.error(`⚠️ Failed to get CSRF token: ${error.message}`);
  }
};

// Utility to fetch the CSRF cookie manually
const getCookie = (name) => {
  const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  return match ? match[2] : null;
};

// Wrapper for CSRF-secured POST requests
const postWithCSRF = async (url, data) => {
  const csrftoken = getCookie("csrftoken");
  return api.post(url, data, {
    headers: {
      "X-CSRFToken": csrftoken,
      "Content-Type": "application/json",
    },
  });
};

// Auth services (return only res.data)
const login = (username, password) =>
  postWithCSRF("auth/token/login/", { username, password }).then(res => res.data);

const logout = (refresh_token) =>
  api.post("auth/token/logout/", { refresh: refresh_token }).then(res => res.data);

const changePassword = ({ old_password, new_password, confirm_password }) =>
  api.post("auth/password/change/", {
    old_password,
    new_password,
    confirm_new_password: confirm_password,
  }).then(res => res.data);

const resetPassword = (email) =>
  postWithCSRF("auth/password/reset/", { email }).then(res => res.data);

const confirmPasswordReset = ({ uid, token, new_password }) =>
  postWithCSRF("auth/password/confirm/", { uid, token, new_password }).then(res => res.data);

const createPassword = ({ uid, token, new_password }) =>
  api.post("auth/users/activate/", { uid, token, new_password }).then(res => res.data);

// User management
const getUsers = () =>
  api.get("auth/users/").then(res => res.data);

const createUser = (userData) =>
  api.post("auth/users/", userData).then(res => res.data);

const updateUser = (userData) =>
  api.put(`auth/users/${encodeURIComponent(userData.id)}/`, userData).then(res => res.data);

const deleteUser = (userId) =>
  api.delete(`auth/users/${encodeURIComponent(userId)}/`).then(res => res.data);

const accountService = {
  getCSRFToken,
  login,
  logout,
  changePassword,
  resetPassword,
  confirmPasswordReset,
  getUsers,
  createUser,
  createPassword,
  updateUser,
  deleteUser,
};

export default accountService;
