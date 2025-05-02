// src/pages/Dashboard.js

import React, { useState } from 'react';
import { Layout, Menu, Button, Spin, Alert, Tooltip, Space } from 'antd';
import { ProfileOutlined, TeamOutlined, LogoutOutlined, SettingOutlined, ApiOutlined, GithubOutlined } from '@ant-design/icons';
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

const HomePage = () => {
  const dispatch = useDispatch();
  const [collapsed, setCollapsed] = useState(false);
  const [selectedMenuItem, setSelectedMenuItem] = useState('patients');
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const auth = useSelector((state) => state.account);
  const isAdmin = auth?.user?.is_superuser
  console.log(isAdmin)

  const handleLogout = () => {
    const refresh_token = auth?.user?.refresh_token;
    localStorage.removeItem('authToken');
    dispatch(logout(refresh_token));
    navigate('/login');
  };

  const handleMenuSelect = ({ key }) => {
    setSelectedMenuItem(key);
    setSelectedPatient(null);
  };

  const renderContent = () => {
    if (error) return <Alert message={error} type="error" showIcon />;
    switch (selectedMenuItem) {
      case 'admin':
        return <AdminPage />;
      case 'gregor_data':
        return <GregorTables />;
      case 'gregor':
        return <GregorParticipants />;
      case 'profile':
        return <ProfilePage/> ;
      default:
        return <ProfilePage/>;
    }
  };

  return (
    <Layout className="layout-container">
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed} className="sider-container">
        <h2 className="sider-header">UCI ICTS Dashboard</h2>
        {/* Menu Items */}
        <div className="sider-menu-wrapper">
          <Menu
            theme="dark"
            selectedKeys={[selectedMenuItem]}
            mode="inline"
            onClick={handleMenuSelect}
            items={[
              { key: 'gregor_data', icon: <TeamOutlined />, label: 'GREGoR Tables' },
              { key: 'gregor', icon: <TeamOutlined />, label: 'Participant Detail' },
              { key: 'profile', icon: <ProfileOutlined />, label: 'Profile'},
              ...(isAdmin ? [{ key: 'admin', icon: <SettingOutlined />, label: 'Admin' }] : []),
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
        <Content className="site-content">{renderContent()}</Content>
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

export default HomePage;
