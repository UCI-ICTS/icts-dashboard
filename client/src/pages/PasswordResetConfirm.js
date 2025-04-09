import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Form, Input, Button, message } from 'antd';
import axios from 'axios';

const PasswordResetConfirm = () => {
  const [params] = useSearchParams();
  const uid = params.get("uid");
  const token = params.get("token");
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      await axios.post(`${process.env.REACT_APP_APIDB}api/auth/password/confirm/`, {
        uid,
        token,
        new_password: values.new_password,
      });
      message.success("Password has been reset!");
      navigate("/login");
    } catch (error) {
      console.error(error);
      message.error("Failed to reset password. Link may be expired.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-form-wrapper">
        <h2>Reset Your Password</h2>
        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item
            name="new_password"
            label="New Password"
            rules={[{ required: true, message: "Please enter your new password" }]}
          >
            <Input.Password />
          </Form.Item>
          <Form.Item
            label="Confirm New Password"
            name="confirm_password"
            dependencies={['new_password']}
            rules={[
                { required: true, message: "Please confirm your new password" },
                ({ getFieldValue }) => ({
                validator(_, value) {
                    if (!value || getFieldValue("new_password") === value) {
                    return Promise.resolve();
                    }
                    return Promise.reject(new Error("Passwords do not match"));
                },
                }),
            ]}
            >
              <Input.Password autoComplete="new-password" />
            </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>
              Reset Password
            </Button>
          </Form.Item>
        </Form>
      </div>
    </div>
  );
};

export default PasswordResetConfirm;
