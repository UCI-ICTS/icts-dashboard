import { configureStore } from "@reduxjs/toolkit";
import { accountReducer, login, logout, handleExpiredJWT } from "./accountSlice";
import AccountService from "../services/account.service";

// Mock AccountService
jest.mock("../services/account.service");

describe("accountSlice", () => {
  let store;

  beforeEach(() => {
    store = configureStore({ reducer: { account: accountReducer } });
  });

  test("should return initial state", () => {
    expect(store.getState().account).toMatchObject({
      isLoggedIn: false,
      user: null,
      loading: false,
    });
  });

  test("should set isLoggedIn on login success", async () => {
    const mockUser = { 
        access: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJ0ZXN0VXNlciJ9.sQvJG1nDbQxsmfXGp1OSuPOrP8B-BbURh5q_B3Wmc1M", 
        refresh: "mockRefreshToken" 
      };      
    AccountService.login.mockResolvedValue(mockUser);

    await store.dispatch(login({ username: "test", password: "pass", rememberMe: true }));

    expect(store.getState().account.isLoggedIn).toBe(true);
    expect(store.getState().account.user.access_token).toBe(mockUser.access);
    expect(store.getState().account.user.refresh_token).toBe(mockUser.refresh);
  });

  test("should reset state on logout", async () => {
    AccountService.logout.mockResolvedValue("Logged out");
    
    await store.dispatch(logout({ token: "mockToken" }));

    expect(store.getState().account.isLoggedIn).toBe(false);
    expect(store.getState().account.user).toBeNull();
  });

  test("should handle expired JWT", async () => {
    await store.dispatch(handleExpiredJWT());

    expect(store.getState().account.isLoggedIn).toBe(false);
    expect(store.getState().account.user).toBeNull();
  });
});
