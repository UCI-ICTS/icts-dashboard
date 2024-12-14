import axios from "axios";

const USERSDB = process.env.REACT_APP_USERDB;

const login = async (username, password) => {
  console.log("USERSDB",USERSDB)
  const response = await axios.post(USERSDB + "/api/auth/login/", {
    username,
    password,
  });
  if (response.data.token) {
    localStorage.setItem("user", JSON.stringify(response.data.user));
    localStorage.setItem("token", JSON.stringify(response.data.token));
    return response.data;
    } else {
      console.log("service error")
    }
  };

  const accountService = {
    login,
  };
  
  export default accountService;