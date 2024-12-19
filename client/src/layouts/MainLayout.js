// src/layouts/MainLayout/index.js

import React from "react";
import { Outlet } from "react-router-dom";
import NavBar from "../components/NavBar";
import NotificationBox from "../components/NotificationBox";
import "../App.css";

const MainLayout = () => {

  return (
    <div className="outlet-root">
      <NavBar />
      <NotificationBox />
      <div className="outlet-container">
        <div className="outlet-main-content">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default MainLayout;