import React, { useEffect, useState } from 'react';
import { Form, Input, Button, Checkbox, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { login } from '../slices/accountSlice';

const Login = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [rememberMe, setRememberMe] = useState(false);
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

  // Redirect after login
  useEffect(() => {
    if (isLoggedIn) {
      navigate('/'); // Redirect to Dashboard after login
    }
  }, [isLoggedIn, navigate]);

  return (
    <div className="login-container">
      <div className="login-form-wrapper">
        <h2>Welcome to C3PO</h2>
        <Form name="login_form" className="login-form" onFinish={onFinish}>
          <Form.Item
            name="username"
            rules={[{ required: true, message: 'Please input your Email!' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="Email" />
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
        </Form>
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </div>
    </div>
  );
};

export default Login;
