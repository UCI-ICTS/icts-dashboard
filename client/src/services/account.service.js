// src/services/account.service.js

import axios from "axios";

const APIDB = process.env.REACT_APP_APIDB;

const login = async (username, password) => {
  const response = await axios.post(APIDB + "/api/auth/login/", {
    username,
    password,
  });
  return response.data;
  };

const logout = async (token) => {
  const response = await axios.post(APIDB + "/api/auth/logout/", {
    refresh: token
  });
  return response.data;
  };
  
const changePassword = (values) => {
  const token = values.token
  return axios.post(APIDB + "/api/auth/change_password/", {
    old_password: values.old_password,
    new_password: values.new_password,
    confirm_new_password: values.confirm_password
  }, {
    headers: {
      "Authorization": "Bearer " + token,
      "Content-Type": "application/json"
    }
  })
};

  const accountService = {
    login,
    logout,
    changePassword
  };
  
  export default accountService;