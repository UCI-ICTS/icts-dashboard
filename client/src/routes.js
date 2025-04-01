// src/routes.js 

import React, { useEffect } from 'react';
import { useRoutes, Navigate, useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { jwtDecode } from "jwt-decode";
import Login from './components/Login';
import HomePage from './pages/HomePage';
import { handleExpiredJWT } from './slices/accountSlice';
import { message } from 'antd';

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

  let element = useRoutes([
    {
      path: "/",
      element: <HomePage />
    },
    {
      path: "/login",
      element: <Login />
    }
  ])
  return element;
};

export default AppRoutes;

