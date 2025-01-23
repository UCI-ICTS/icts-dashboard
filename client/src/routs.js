
import React, { useEffect } from "react";
import { useRoutes, Navigate, useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { jwtDecode } from "jwt-decode";
import { setMessage } from "./slices/messageSlice.js";
import { handleExpiredJWT } from "./slices/accountSlice";
import MainLayout from "./layouts/MainLayout";
import HomePage from "./pages/Home";
import Login from "./pages/Login";
import GregorTables from "./pages/GregorTables";

function setupTokenExpirationAlert(expirationTime, onExpireCallback) {
    const currentTime = Date.now() / 1000; // Convert milliseconds to seconds
    const timeUntilExpiration = expirationTime - currentTime; // Time until expiration in seconds
  
    if (timeUntilExpiration > 0) {
      // Set a timeout to call the onExpireCallback after the calculated delay in milliseconds
      setTimeout(onExpireCallback, timeUntilExpiration * 1000);
    } else {
      // If the token is already expired or the time is negative, call the callback immediately
      onExpireCallback();
    }
  }

export default function Router() {
    const dispatch = useDispatch();
    const navigate = useNavigate()
    const isLoggedIn = useSelector((state) => state.account.isLoggedIn)
    const token = useSelector((state) => state.account.user?.access_token)
    
    useEffect(() => {
        if (token) {
          const decoded = jwtDecode(token);
          setupTokenExpirationAlert(decoded.exp, () => {
            navigate("/login")
            dispatch(handleExpiredJWT())
              .unwrap()
              .then((response) => {
                console.log(response)
                dispatch(setMessage("JW Token Expired. Please log in again"))
              })
          });
        }
        
        return () => clearTimeout(setupTokenExpirationAlert);
      }, [token, isLoggedIn]);

    let element = useRoutes([
        {
            path: "/",
            element: <MainLayout />,
            children: [
                { path: "/", element: <HomePage /> },
                { path: "login", element: <Login /> },
                { path: "/gregor/", element: <GregorTables />}
            ]
        },
        {
            path: "/",
            element: <MainLayout />,
            children: [
              { path: "404", element: <Navigate to="/" />},
              { path: "*", element: <Navigate to="/" />}
            ]
          }
    ])
    return element
}