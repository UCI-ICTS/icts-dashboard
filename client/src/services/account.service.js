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
  
  const accountService = {
    login,
    logout,
  };
  
  export default accountService;