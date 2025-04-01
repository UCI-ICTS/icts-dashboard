import React, { useState, useCallback } from 'react';
import { Layout, Menu, Button, Spin, Alert, Tooltip } from 'antd';
import { TeamOutlined, LogoutOutlined, SettingOutlined } from '@ant-design/icons';
import PatientList from '../components/PatientList';
import AdminPage from '../components/AdminPage';
import ChangePasswordForm from '../components/ChangePasswordForm';
import GregorParticipants from "../components/GregorParticipants";
import '../App.css'; // ✅ Importing CSS
import { logout } from '../slices/accountSlice';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import GregorTables from "../components/GregorTables";

const { Header, Content, Footer, Sider } = Layout;

const HomePage = () => {
  const dispatch = useDispatch();
  const [collapsed, setCollapsed] = useState(false);
  const [selectedMenuItem, setSelectedMenuItem] = useState('patients');
  const [isAdmin, setIsAdmin] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const auth = useSelector((state) => state.account);

  const handleLogout = () => {
    const token = auth?.user?.refresh_token;
    localStorage.removeItem('authToken');
    dispatch(logout(token));
    navigate('/login');
  };

  const handleMenuSelect = ({ key }) => {
    setSelectedMenuItem(key);
    setSelectedPatient(null);
  };

  const renderContent = () => {
    if (error) return <Alert message={error} type="error" showIcon />;
    switch (selectedMenuItem) {
      case 'patients':
        return <PatientList />;
      case 'admin':
        return <AdminPage />;
      case 'gregor_data':
        return <GregorTables />;
      case 'gregor':
        return <GregorParticipants />;
      default:
        return null;
    }
  };

  return (
    <Layout className="layout-container">
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed} className="sider-container">
        <h2 className="sider-header">C3PO</h2>  
        {/* Menu Items */}
        <div className="sider-menu-wrapper">
          <Menu
            theme="dark"
            selectedKeys={[selectedMenuItem]}
            mode="inline"
            onClick={handleMenuSelect}
            items={[
              { key: 'patients', icon: <TeamOutlined />, label: 'UDN Patients' },
              { key: 'gregor_data', icon: <TeamOutlined />, label: 'GREGoR Tables' },
              { key: 'gregor', icon: <TeamOutlined />, label: 'GREGoR Patients' },
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
        {/* <Header className="site-header">

        </Header> */}
        <Content className="site-content">{renderContent()}</Content>
        <Footer className="site-footer">C3PO ©2024 UCI</Footer>
      </Layout>
    </Layout>
  );
};

export default HomePage;
