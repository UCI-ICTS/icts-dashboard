import React from 'react';
import { Form, Input, Button, message, Card } from 'antd';
import { LockOutlined } from '@ant-design/icons';
import axios from 'axios';

const ChangePasswordForm = ({ onPasswordChanged}) => {
  const [form] = Form.useForm();

  const handleSubmit = async (values) => {
    try {
      await axios.post('/api/change-password/', { new_password: values.newPassword });
      message.success('Password changed successfully');
      form.resetFields();
      // delay time for user to read message before calling callback function
      setTimeout(() => {
        onPasswordChanged();
      }, 1300);
    } catch (error) {
      console.error('Error changing password:', error);
      message.error('Failed to change password. Please try again.');
    }
  };

  return (
    <Card title="Change Password" style={{ maxWidth: 400, margin: '0 auto' }}>
      <Form
        form={form}
        name="change_password"
        onFinish={handleSubmit}
        layout="vertical"
      >
        <Form.Item
          name="newPassword"
          rules={[
            { required: true, message: 'Please input your new password!' },
            { min: 8, message: 'Password must be at least 8 characters long' },
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="New Password"
          />
        </Form.Item>

        <Form.Item
          name="confirmPassword"
          dependencies={['newPassword']}
          rules={[
            { required: true, message: 'Please confirm your new password!' },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('newPassword') === value) {
                  return Promise.resolve();
                }
                return Promise.reject(new Error('The two passwords do not match!'));
              },
            }),
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="Confirm New Password"
          />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" block>
            Change Password
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default ChangePasswordForm;