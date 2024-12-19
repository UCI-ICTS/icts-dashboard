// src/layouts/MainLayout/index.js

import React from "react";
import { Outlet } from "react-router-dom";
import FormNavBar from "../components/FormNavBar";
import "../App.css";
import NotificationBox from "../components/NotificationBox";

const FormLayout = () => {
  
  return (
    <div className="outlet-root">
      <FormNavBar />
      <NotificationBox />
      <div className="outlet-container">
        <div className="outlet-main-content">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default FormLayout;