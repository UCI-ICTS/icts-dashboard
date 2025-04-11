// src/routes.js 

import React, { useEffect } from 'react';
import { useRoutes, Navigate, useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { jwtDecode } from "jwt-decode";
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import { handleExpiredJWT } from './slices/accountSlice';
import { message } from 'antd';
import PrivateRout from "./components/PrivateRout";
import PasswordResetConfirm from './pages/PasswordResetConfirm';
import AccountService from "./services/account.service";


function setupTokenExpirationAlert(expirationTime, onExpireCallback) {
  const currentTime = Date.now() / 1000; // Convert to seconds
  const timeUntilExpiration = expirationTime - currentTime; 

  if (timeUntilExpiration > 0) {
    setTimeout(onExpireCallback, timeUntilExpiration * 1000);
  } else {
    onExpireCallback();
  }
}

const AppRoutes = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const isLoggedIn = useSelector((state) => state.account.isLoggedIn);
  const token = useSelector((state) => state.account.user?.access_token);
  console.log("isLoggedIn", isLoggedIn)
    
  useEffect(() => {
      if (token) {
        try {
          const decoded = jwtDecode(token);
          setupTokenExpirationAlert(decoded.exp, () => {
            navigate("/login");
            dispatch(handleExpiredJWT())
              .unwrap()
              .then(() => {
                message.error("JWT Expired. Please log in again.");
              });
          });
        } catch (error) {
          console.error("Invalid token:", error);
          navigate("/login");
          dispatch(handleExpiredJWT());
      }
    }
    if (isLoggedIn && !token) {
      console.log("Missing token",)
    }
  }, [token, isLoggedIn, dispatch, navigate]);

  useEffect(() => {
    AccountService.getCSRFToken();
  }, []);

  let element = useRoutes([
    {
      path: "/",
      element: (
        <PrivateRout>
          <Dashboard />
        </PrivateRout>
      )
    },
    {
      path: "/login",
      element: <Login />
    },
    {
      path: "/password-reset",
      element: <PasswordResetConfirm />
    },
    {
      path: "/password-create",
      element: <PasswordResetConfirm />
    }
  ])
  return element;
};

export default AppRoutes;

