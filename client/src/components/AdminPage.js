import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, message, Input } from 'antd';
import axios from 'axios';
import AddUserForm from './AddUserForm';

const AdminPage = () => {
  const [users, setUsers] = useState([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [tempPassword, setTempPassword] = useState('');
  const [isPasswordModalVisible, setIsPasswordModalVisible] = useState(false);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/private/v1/users/');
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
      message.error('Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { title: 'Email', dataIndex: 'email', key: 'email' },
    { title: 'First Name', dataIndex: 'first_name', key: 'first_name' },
    { title: 'Last Name', dataIndex: 'last_name', key: 'last_name' },
    { title: 'Specialization', dataIndex: 'specialization', key: 'specialization' },
    { title: 'Phone Number', dataIndex: 'phone_number', key: 'phone_number' },
    { title: 'Institution', dataIndex: 'institution', key: 'institution' },
    { title: 'Is Staff', dataIndex: 'is_staff', key: 'is_staff' },
    { title: 'Is Active', dataIndex: 'is_active', key: 'is_active' },
  ];

  const showModal = () => {
    setIsModalVisible(true);
  };

  const handleCancel = () => {
    setIsModalVisible(false);
  };

  const handleAddUser = async (userData) => {
    try {
      const dataToSend = {
        ...userData,
        is_staff: userData.is_staff === true
      };
      const response = await axios.post('/api/private/v1/users/', dataToSend);
      message.success('User added successfully');
      fetchUsers();
      setIsModalVisible(false);
      if (response.data.temp_password) {
        setTempPassword(response.data.temp_password);
        setIsPasswordModalVisible(true);
      }
    } catch (error) {
      console.error('Error adding user:', error);
      if (error.response) {
        console.error('Error response:', error.response.data);
      }
      message.error('Failed to add user');
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(tempPassword).then(() => {
      message.success('Password copied to clipboard');
    }, (err) => {
      console.error('Could not copy text: ', err);
      message.error('Failed to copy password');
    });
  };

  return (
    <div>
      <h1>User Management</h1>
      <Button onClick={showModal} type="primary" style={{ marginBottom: 16 }}>
        Add New User
      </Button>
      <Table 
        columns={columns} 
        dataSource={users} 
        rowKey="id" 
        loading={loading}
      />
      <Modal
        title="Add New User"
        open={isModalVisible}
        onCancel={handleCancel}
        footer={null}
      >
        <AddUserForm onSubmit={handleAddUser} />
      </Modal>
      <Modal
        title="Temporary Password"
        open={isPasswordModalVisible}
        onOk={() => setIsPasswordModalVisible(false)}
        onCancel={() => setIsPasswordModalVisible(false)}
        footer={[
          <Button key="copy" type="primary" onClick={copyToClipboard}>
            Copy Password
          </Button>,
          <Button key="ok" onClick={() => setIsPasswordModalVisible(false)}>
            OK
          </Button>,
        ]}
      >
        <p>The temporary password for the new user is:</p>
        <Input.Password
          value={tempPassword}
          readOnly
          style={{ marginBottom: '10px' }}
        />
        <p>Please securely communicate this password to the user.</p>
      </Modal>
    </div>
  );
};

export default AdminPage;;