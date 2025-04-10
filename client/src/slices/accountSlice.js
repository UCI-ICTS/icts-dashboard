// accountSlice

import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { message } from "antd";
import AccountService from "../services/account.service";
import { jwtDecode } from "jwt-decode";

const user = JSON.parse(localStorage.getItem("user"));

const initialState = user
  ? { isLoggedIn: true, user, staff: [], loading: false, error: null }
  : { isLoggedIn: false, user: null, staff: [], loading: false, error: null };

  export const accountSlice = createSlice({
    name: "account",
    initialState,
    extraReducers: (builder) => {
      builder
// --- Authentication and Passwords ---
        .addCase(login.pending, (state) => {
          state.loading = true; // Set loading to true when login is pending
        })
        .addCase(login.fulfilled, (state, action) => {
          state.loading = false; // Set loading to false when login is fulfilled
          state.isLoggedIn = true;
          const payload = action.payload.data
          const user = jwtDecode(action.payload.data.access)
          user["refresh_token"] = payload.refresh
          user["access_token"] = payload.access
          delete user.token_type
          state.user = user;
          if (action.payload.rememberMe === true) {
            localStorage.setItem("user", JSON.stringify(user));
          }
        })
        .addCase(login.rejected, (state) => {
          state.loading = false; // Set loading to false when login is rejected
          state.isLoggedIn = false;
          state.user = null;
        })

        .addCase(handleExpiredJWT.fulfilled, (state, action) => {
          state.loading = false; // Set loading to false when login is rejected
          state.isLoggedIn = false;
          state.user = null;
        })
        .addCase(handleExpiredJWT.pending, (state, action) => {
          console.log("pending")
          state.loading = true; // Set loading to true when logout is pending
        })
        .addCase(handleExpiredJWT.rejected, (state, action) => {
          console.log("rejected")
        })

        .addCase(logout.pending, (state) => {
          console.log("logout pending")
          state.loading = true;
        })
        .addCase(logout.rejected, (state) => {
          state.loading = false;
          localStorage.removeItem("user")
          state.loading = false; // Set loading to false when logout is processed
          state.isLoggedIn = false;
          state.user = null;
          console.log("Token blacklist rejected")
        })
        .addCase(logout.fulfilled, (state) => {
          localStorage.removeItem("user")
          console.log("logout fulfilled")
          state.loading = false; // Set loading to false when logout is processed
          state.isLoggedIn = false;
          state.user = null;

        })
        
        .addCase(resetPassword.pending, (state) => {
          state.loading = true;
          state.error = null;
        })
        .addCase(resetPassword.fulfilled, (state, action) => {
          state.loading = false;
        })
        .addCase(resetPassword.rejected, (state, action) => {
          state.loading = false;
          state.error = action.payload;
        })

        .addCase(confirmPasswordReset.pending, (state) => {
          state.loading = true;
          state.error = null;
        })
        .addCase(confirmPasswordReset.fulfilled, (state, action) => {
          state.loading = false;
        })
        .addCase(confirmPasswordReset.rejected, (state, action) => {
          state.loading = false;
          state.error = action.payload;
        })

// --- Users ---
        .addCase(fetchUsers.pending, (state) => {
          state.loading = true;
          state.error = null;
        })
        .addCase(fetchUsers.fulfilled, (state, action) => {
          state.loading = false;
          state.staff = action.payload;
        })
        .addCase(fetchUsers.rejected, (state, action) => {
          state.loading = false;
          state.error = action.payload;
        })
  
        .addCase(addUser.fulfilled, (state, action) => {
          state.loading = true;
          state.error = null;
        })
        .addCase(addUser.pending, (state, action) => {
          const user = action.payload;
          state.staff.push(user);
        })
        .addCase(addUser.rejected, (state, action) => {
          state.loading = false;
          state.error = action.payload;
        })
  
        .addCase(updateUser.fulfilled, (state, action) => {
          const updated = action.payload;
          state.staff.push(updated);
        })
        .addCase(updateUser.pending, (state, action) => {
          const user = action.payload;
          state.staff.push(user);
        })
        .addCase(updateUser.rejected, (state, action) => {
          state.loading = false;
          state.error = action.payload;
        })

        .addCase(deleteUser.fulfilled, (state, action) => {
          const id = action.payload;
          state.staff = state.staff.filter((u) => u.id !== id);
        })
        .addCase(deleteUser.pending, (state, action) => {
          const user = action.payload;
          state.staff.push(user);
        })
        .addCase(deleteUser.rejected, (state, action) => {
          state.loading = false;
          state.error = action.payload;
        })
    }
})

// --- Authentication and Passwords ---
export const login = createAsyncThunk(
  "auth/login",
  async ({ username, password, rememberMe }, thunkAPI) => {
    try {
      const data = await AccountService.login(username, password);
      return { data, rememberMe };
    } catch (error) {
      console.error("Login Error:", error);

      // Extract error message safely
      let errorMessage = "Login failed. Please try again."; // Default message
      if (error.response?.data) {
        // Handle Django DRF-style errors (e.g., { detail: "Invalid credentials" })
        if (typeof error.response.data === "object") {
          errorMessage = error.response.data.detail || JSON.stringify(error.response.data);
        } else {
          errorMessage = error.response.data;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);

export const logout = createAsyncThunk(
  "auth/logout",
  async (refresh_token, thunkAPI) => {
    try {
      const data = await AccountService.logout(refresh_token);
      message.success("User logged out successfully");
      return { data };
    } catch (error) {
      const errorMessage =
        (error &&
          error.errorMessage) ||
          error.non_field_errors[0] ||
        error.toString();
      message.error(errorMessage|| "Logout failed. Please try again.");
      return thunkAPI.rejectWithValue();
    }
  }
);

export const handleExpiredJWT = createAsyncThunk(
  "account/handleExpiredJWT",
  async () => {
    try {
      localStorage.removeItem("user");
      // global.window.location.reload()
      return "Logged out due to expired session"
    } catch (error) {
      return error;
    }
  }
);

export const changePassword = createAsyncThunk(
  "auth/change_password",
  async (values, thunkAPI) => {
    try {
      console.log("Slice values: ", values)
      const response = await AccountService.changePassword(values);
      message.success("Password changed successfully");
      return response.data;
    } catch (error) {
      console.log("Slice response: ", error)
      let errorMessage = "An error occurred";

      if (error.response) {
        const errorData = error.response.data;

        // Handle "detail" errors (e.g., token issues)
        if (errorData?.detail) {
          errorMessage = errorData.detail;
        } 
        // Handle field validation errors (e.g., incorrect password)
        else if (typeof errorData === "object") {
          errorMessage = Object.entries(errorData)
            .map(([field, errors]) => `${field}: ${errors.join(", ")}`)
            .join(" | "); // Join multiple field errors with " | "
        } 
        // Generic error errorMessage
        else {
          errorMessage = "Something went wrong";
        }
      } else if (error.errorMessage) {
        errorMessage = error.errorMessage;
      }

      // Dispatch errorMessage to Redux state
      message.error(errorMessage);

      // Reject the request and pass the errorMessage
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);

export const resetPassword = createAsyncThunk(
  "auth/reset_password",
  async (email, thunkAPI) => {
    try {
      console.log("Slice password reset: ", email);
      const response = await AccountService.resetPassword(email);
      console.log(response.message)
      message.success(response.message)
      return response.data;
    } catch (error) {
      console.log("Slice password reset error: ", error);

      let errorMessage = "An error occurred";

      if (error.response) {
        const errorData = error.response.data;

        if (typeof errorData === "string") {
          // If backend just returns a plain error message
          errorMessage = errorData;
        } else if (errorData?.detail) {
          errorMessage = errorData.detail;
        } else if (typeof errorData === "object") {
          errorMessage = Object.entries(errorData)
            .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(", ") : errors}`)
            .join(" | ");
        } else {
          errorMessage = `Request failed with status ${error.response.status}`;
        }

      } else if (error.message) {
        errorMessage = error.message;
      }

      message.error(errorMessage);
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);

export const confirmPasswordReset = createAsyncThunk(
  "auth/confirm_password_reset",
  async ({ uid, token, new_password }, thunkAPI) => {
    try {
      const response = await AccountService.confirmPasswordReset({ uid, token, new_password });
      return response.data;
    } catch (error) {
      console.log("Slice confirm reset error:", error);

      let errorMessage = "An error occurred";

      if (error.response) {
        const errorData = error.response.data;

        if (typeof errorData === "string") {
          errorMessage = errorData;
        } else if (errorData?.detail) {
          errorMessage = errorData.detail;
        } else if (typeof errorData === "object") {
          errorMessage = Object.entries(errorData)
            .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(", ") : errors}`)
            .join(" | ");
        } else {
          errorMessage = `Request failed with status ${error.response.status}`;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }

      message.error(errorMessage);
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);

// --- Users ---

export const fetchUsers = createAsyncThunk(
  "data/fetchUsers", 
  async (_, thunkAPI) => {
  try {
    return await AccountService.getUsers();
  } catch (error) {
    message.error("Failed to fetch users.");
    return thunkAPI.rejectWithValue(error.message);
  }
});

export const addUser = createAsyncThunk(
  "data/addUser", 
  async (userData, thunkAPI) => {
  try {
    console.log("Slice ",userData)
    const res = await AccountService.createUser(userData);
    message.success("User added successfully!");
    return res;
  } catch (error) {
    console.log(error)
    let errorMessage = "Login failed. Please try again."; // Default message
    message.error("Failed to add participant. A participant with that email probably exists");
    return thunkAPI.rejectWithValue(error.message);
  }
});

export const activateUserAccount = createAsyncThunk(
  "auth/activate_account",
  async ({ uid, token, new_password }, thunkAPI) => {
    try {
      const response = await AccountService.createPassword({ uid, token, new_password });
      return response.data;
    } catch (error) {
      console.log("Slice activation error:", error);

      let errorMessage = "An error occurred";

      if (error.response) {
        const errorData = error.response.data;

        if (typeof errorData === "string") {
          errorMessage = errorData;
        } else if (errorData?.detail) {
          errorMessage = errorData.detail;
        } else if (typeof errorData === "object") {
          errorMessage = Object.entries(errorData)
            .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(", ") : errors}`)
            .join(" | ");
        } else {
          errorMessage = `Request failed with status ${error.response.status}`;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }

      message.error(errorMessage);
      return thunkAPI.rejectWithValue(errorMessage);
    }
  }
);

export const updateUser = createAsyncThunk(
  "data/updateUser",
  async (userData, thunkAPI) => {
  try {
    const response = await AccountService.updateUser(userData);
    message.success("User updated successfully!");
    return response;
  } catch (error) {
    message.error("Failed to update user.");
    return thunkAPI.rejectWithValue(error.message);
  }
});

export const deleteUser = createAsyncThunk(
  "data/deleteUser",
  async (userId, thunkAPI) => {
  try {
    console.log(userId)
    await AccountService.deleteUser(userId);
    message.success("User deleted successfully!");
    return userId;
  } catch (error) {
    message.error("Failed to delete user.");
    return thunkAPI.rejectWithValue(error.message);
  }
});

export const accountReducer = accountSlice.reducer