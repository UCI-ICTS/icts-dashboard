import React, { useEffect, useState } from 'react';
import { Form, Input, Button, Checkbox, message, Modal } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { login, resetPassword } from '../slices/accountSlice';


const Login = () => {
  const [form] = Form.useForm();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [rememberMe, setRememberMe] = useState(false);
  const [passwordResetModal, setPasswordResetModal] = useState(false);
  const { isLoggedIn, loading, error } = useSelector((state) => state.account);

  const onFinish = async (values) => {
    dispatch(login({...values, rememberMe}))
      .unwrap()
      .then(() => {
        message.success("Login successful");
      })
      .catch((err) => {
        message.error(err || "Login failed. Please check your credentials.");
      });
  };
  
  const showModal = () => {
    setPasswordResetModal(true);
  };

  const submitReset = (values) => {
    console.log(values);
    dispatch(resetPassword(values.email))
    form.resetFields();
    setPasswordResetModal(false);
  };
  
  const handleCancel = () => {
    form.resetFields();
    setPasswordResetModal(false);
  };

  // Redirect after login
  useEffect(() => {
    if (isLoggedIn) {
      navigate('/'); // Redirect to Dashboard after login
    }
  }, [isLoggedIn, navigate]);

  return (
    <div className="login-container">
      <div className="login-form-wrapper">
        <h2>Welcome to the UCI ICTS Dashboard</h2>
        <Form name="login_form" className="login-form" onFinish={onFinish}>
          <Form.Item
            name="username"
            rules={[{ required: true, message: 'Please input your username!' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="Username" />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Please input your Password!' }]}
          >
            <Input prefix={<LockOutlined />} type="password" placeholder="Password" />
          </Form.Item>
          <Form.Item>
            <Checkbox checked={rememberMe} onChange={(e) => setRememberMe(e.target.checked)}>
              Remember Me
            </Checkbox>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" className="login-form-button" loading={loading}>
              Log in
            </Button>
          </Form.Item>
          <Form.Item>
            <Button
              onClick={showModal}
            >Forgot Password</Button>
          </Form.Item>
        </Form>
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </div>
      <Modal
        title="Password reset"
        open={passwordResetModal}
        onCancel={handleCancel}
        footer={null}
        width={500}
      >
        <Form layout="vertical" onFinish={submitReset}>
          <Form.Item
            name="email"
            label="Email"
            rules={[{ required: true, message: "Please enter a valid email" }]}
          >
            <Input type="email" autoComplete="email" />
          </Form.Item>
          <Form.Item>
            <Button onClick={handleCancel} style={{ marginRight: 8 }}>
              Cancel
            </Button>
            <Button type="primary" htmlType="submit">
              Submit
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Login;
