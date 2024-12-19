import axios from "axios";

const USERSDB = process.env.REACT_APP_USERDB;

const login = async (username, password) => {
  const response = await axios.post(USERSDB + "/api/auth/login/", {
    username,
    password,
  });
  return response.data;
  };

  const logout = async (token) => {
    const response = await axios.post(USERSDB + "/api/auth/logout/", {
      refresh: token
    });
    return response.data;
    };
  
  const accountService = {
    login,
    logout,
  };
  
  export default accountService;