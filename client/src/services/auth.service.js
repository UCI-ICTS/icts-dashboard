import axios from "axios";

const USERS_URL = process.env.REACT_APP_USERDB_URL;

const login = async (username, password) => {
    const response = await axios.post(USERS_URL + "auth/login/", {
      username,
      password,
    });
    if (response.data.token) {
      localStorage.setItem("user", JSON.stringify(response.data.user));
      localStorage.setItem("token", JSON.stringify(response.data.token));
    }
    return response.data;
  };

  const authService = {
    login,
  };
  
  export default authService;