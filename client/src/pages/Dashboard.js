// src/pages/Dashboard.js
import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from "react-router-dom";
import { Layout, Menu, Button, Tooltip } from 'antd';
import {
  DatabaseOutlined,
  DotChartOutlined,
  HomeOutlined,
  LogoutOutlined,
  ProfileOutlined,
  ScheduleOutlined,
  SettingOutlined,
  UploadOutlined,
  UserOutlined
} from '@ant-design/icons';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../slices/accountSlice';
import SiteFooter from '../components/SiteFooter';
import '../App.css';

const { Content, Sider } = Layout;

const Dashboard = () => {
  const location = useLocation();
  const current = location.pathname.split("/").pop();
  const dispatch = useDispatch();
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const auth = useSelector((state) => state.account);
  const isAdmin = auth?.user?.is_superuser;

  const handleLogout = () => {
    const refresh_token = auth?.user?.refresh_token;
    localStorage.removeItem('authToken');
    dispatch(logout(refresh_token));
    navigate('/');
  };

  const menuItems = [
    { key: 'home', icon: <HomeOutlined />, label: <Link to="/">ICTS Home</Link> },
    { key: 'summary', icon: <DotChartOutlined />, label: <Link to="/gregor-summary">Summary Page</Link> },
    { key: 'table-data', icon: <DatabaseOutlined />, label: <Link to="table-data">GREGoR Tables</Link> },
    { key: 'participant-detail', icon: <UserOutlined />, label: <Link to="participant-detail">Participant Detail</Link> },
    { key: 'case-queue', icon: <ScheduleOutlined />, label: <Link to="case-queue">Case Queue</Link> },
    { key: 'uploader', icon: <UploadOutlined />, label: <Link to="uploader">Uploader</Link> },
    { key: 'profile', icon: <ProfileOutlined />, label: <Link to="profile">Profile</Link> },
    ...(isAdmin ? [{ key: 'admin', icon: <SettingOutlined />, label: <Link to="admin">Admin</Link> }] : []),
  ];

  return (
    <Layout className="layout-container">
      <Sider
        width={220}
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        className="sider-container"
      >
        <h2 className="sider-header">{collapsed ? "ICTS" : "UCI ICTS Dashboard"}</h2>
        <div className="sider-menu-wrapper">
          <Menu
            theme="dark"
            selectedKeys={[current]}
            mode="inline"
            items={menuItems}
          />
        </div>
        <div className="logout-button-container">
          <Tooltip title="Logout">
            <Button
              onClick={handleLogout}
              icon={<LogoutOutlined />}
              className="logout-button"
            >
              {!collapsed && "Logout"}
            </Button>
          </Tooltip>
        </div>
      </Sider>
      <Layout className="site-layout">
        <Content className="site-content">
          <Outlet />
        </Content>
        <SiteFooter />
      </Layout>
    </Layout>
  );
};

export default Dashboard;
