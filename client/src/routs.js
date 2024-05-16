
import React from "react";
import { useRoutes, Navigate } from "react-router-dom";
import { useSelector } from "react-redux";
import MainLayout from "./layouts/MainLayout";
import HomePage from "./pages/Home";
import Login from "./pages/Login";
import Refferal from "./pages/Refferal";
import FormLayout from "./layouts/FormLayout";


export default function Router() {
    // const isLoggedIn = useSelector((state) => state.account.isLoggedIn)
    
    let element = useRoutes([
        {
            path: "/",
            element: <MainLayout />,
            children: [
                { path: "/", element: <HomePage /> },
                { path: "login", element: <Login /> },
                { path: "/contact", element: <Login /> },
                // { path: "/howto", element: <Login /> },
            ]
        },
        {
            path: "/forms",
            element: <FormLayout/>,
            children: [
                { path: "/forms/refferal", element: <Refferal />}
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