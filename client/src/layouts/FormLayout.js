// src/layouts/MainLayout/index.js

import React from "react";
import { Outlet } from "react-router-dom";
import NavBar from "./NavBar";
import "../App.css";

const FormLayout = () => {

  return (
    <div className="outlet-root">
      {/* <NavBar /> */}
      <div className="outlet-container">
        <div className="outlet-main-content">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default FormLayout;