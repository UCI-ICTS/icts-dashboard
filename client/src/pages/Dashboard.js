// src/pages/Dashboard.js

import React, { useState } from 'react';

import { Outlet, Link, useLocation } from "react-router-dom";

import { Layout, Menu, Button, Spin, Alert, Tooltip, Space } from 'antd';
import { ProfileOutlined, TeamOutlined, HomeOutlined, LogoutOutlined, SettingOutlined, ApiOutlined, GithubOutlined, UploadOutlined } from '@ant-design/icons';
import AdminPage from './AdminPage';
import GregorParticipants from "../components/GregorParticipants";
import '../App.css'; // ✅ Importing CSS
import { logout } from '../slices/accountSlice';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import GregorTables from "../components/GregorTables";
import ProfilePage from './ProfilePage';

const { Header, Content, Footer, Sider } = Layout;
const APIDB = process.env.REACT_APP_APIDB;

const Dashboard = () => {
  const location = useLocation();
  const current = location.pathname.split("/").pop();

  const dispatch = useDispatch();
  const [collapsed, setCollapsed] = useState(false);
  
  const navigate = useNavigate();
  const auth = useSelector((state) => state.account);
  const isAdmin = auth?.user?.is_superuser

  const handleLogout = () => {
    const refresh_token = auth?.user?.refresh_token;
    localStorage.removeItem('authToken');
    dispatch(logout(refresh_token));
    navigate('/');
  };


  return (
    <Layout className="layout-container">
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed} className="sider-container">
        <h2 className="sider-header">UCI ICTS Dashboard</h2>
        {/* Menu Items */}
        <div className="sider-menu-wrapper">
          <Menu
            theme="dark"
            selectedKeys={[current]}
            mode="inline"
            items={[
              { key: 'home', icon: <HomeOutlined />, label: <Link to="/">ICTS Home</Link> },
              { key: 'summary', icon: <TeamOutlined />, label: <Link to="summary">Summary Page</Link> },
              { key: 'table-data', icon: <TeamOutlined />, label: <Link to="table-data">GREGoR Tables</Link> },
              { key: 'participant-detail', icon: <TeamOutlined />, label: <Link to="participant-detail">Participant Detail</Link> },
              { key: 'uploader', icon: <UploadOutlined />, label: <Link to="uploader">Uploader</Link> },
              { key: 'profile', icon: <ProfileOutlined />, label: <Link to="profile">Profile</Link> },
              ...(isAdmin ? [{ key: 'admin', icon: <SettingOutlined />, label: <Link to="admin">Admin</Link> }] : []),
            ]}
          />
        </div>
        <div className="logout-button-container">
          <Tooltip title="Logout">
            <Button
              onClick={handleLogout}
              icon={<LogoutOutlined />}
              className="logout-button"
              >
              {!collapsed && "Logout"} {/* Hide text when sidebar is collapsed */}
            </Button>
          </Tooltip>
        </div>
      </Sider>
      <Layout className="site-layout">
        <Header className="site-header" />
        <Content className="site-content">
          <Outlet />
        </Content>
        <Footer className="site-footer">
          <Space >
            <Tooltip title="UCI ICTS Dashboard"> ©2024 UCI</Tooltip>
            <br/>
            <Tooltip title="Swagger API site">
              <ApiOutlined />
              <a
                href={`${APIDB}api/swagger/`} //"https://genomics.icts.uci.edu/"
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()} // prevent triggering `onClick` from Menu
                >
                Swagger API
              </a>
            </Tooltip>
            <br/>
            <Tooltip title="UCI ICTS Dashboard GitHub">
              <GithubOutlined />
              <a
                href="https://github.com/UCI-GREGoR/GREGor_dashboard"
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()} // prevent triggering `onClick` from Menu
              >GitHub</a>
            </Tooltip>
          </Space>
        </Footer>
      </Layout>
    </Layout>
  );
};

export default Dashboard;
