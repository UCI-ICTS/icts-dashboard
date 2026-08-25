// src/routs.js

import React, { useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { jwtDecode } from "jwt-decode";
import { message } from 'antd';

import AdminPage from './pages/AdminPage';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ProfilePage from './pages/ProfilePage';
import SummaryPage from './pages/SummaryPage';
import GregorDataSheets from './pages/GregorDataSheets';
import RAGHPO from './pages/RAGHPO';
import PasswordResetConfirm from './pages/PasswordResetConfirm';
import PrivateRout from "./components/PrivateRoute";
import AccountService from "./services/account.service";
import HomePage from './pages/Home';
import { handleExpiredJWT } from './slices/accountSlice';
import { Uploader } from "./pages/Uploader";
import PhenotypeCohort from './pages/PhenotypeCohort';
import AnvilUpload from './pages/AnvilUpload.js';

function setupTokenExpirationAlert(expirationTime, onExpireCallback) {
  const currentTime = Date.now() / 1000;
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
      console.warn("Logged in but missing token");
    }
  }, [token, isLoggedIn, dispatch, navigate]);

  useEffect(() => {
    AccountService.getCSRFToken();
  }, []);

  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<Login />} />
      <Route path="/password-reset" element={<PasswordResetConfirm />} />
      <Route path="/password-create" element={<PasswordResetConfirm />} />
      <Route path="/gregor-summary" element={<SummaryPage />} />

      <Route path="/dashboard" element={<PrivateRout><Dashboard /></PrivateRout>}>
        <Route index element={<ProfilePage />} />
        <Route path="table-data" element={<GregorDataSheets />} />
        <Route path="table-data/:table" element={<GregorDataSheets />} />
        <Route path="participant-detail/" element={<GregorDataSheets renderDetail={true} />} />
        <Route path="participant-detail/:pid" element={<GregorDataSheets renderDetail={true} />} />
        <Route path="case-queue/" element={<GregorDataSheets renderQueue={true} />} />
        <Route path="case-queue/:pid" element={<GregorDataSheets renderQueue={true} />} />
        <Route path="admin" element={<AdminPage />} />
        <Route path="uploader" element={<Uploader />} />
        <Route path="summary" element={<SummaryPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="cohort" element={<PhenotypeCohort />} />
        <Route path="rag-hpo" element={<RAGHPO />} />
        <Route path="anvil" element={<AnvilUpload />} />
      </Route>

      {/* CATCH-ALL: Place this LAST so it doesn't block valid routes */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );

};

export default AppRoutes;
