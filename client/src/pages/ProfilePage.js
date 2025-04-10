// src/pages/profile.js

import React, { useState } from "react";
import { Button, Card, Form, Input, Typography, message } from "antd";
import { useDispatch, useSelector } from "react-redux";
import PasswordReset from "../components/PasswordReset";
import { updateUser } from "../slices/accountSlice";
import "../App.css";

const ProfilePage = () => {
  const dispatch = useDispatch();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const user = useSelector((state) => state.account.user);

  const [form] = Form.useForm();

  const handleSubmit = async (values) => {
    setLoading(true);
    const payload = {
      ...values,
      username: user?.username,
    };

    console.log(values);
    dispatch(updateUser(payload));
    setLoading(false);
  };

  return (
    <Card title="Profile Card" className="container-test">
      <PasswordReset open={open} setOpen={setOpen} />

      <Button type="default" onClick={() => setOpen(true)} style={{ marginBottom: 16 }}>
        Change Password
      </Button>

      <Form
        form={form}
        layout="vertical"
        initialValues={user}
        onFinish={handleSubmit}
      >
        <Form.Item label="Given Name" name="first_name">
          <Input />
        </Form.Item>

        <Form.Item label="Family Name" name="last_name">
          <Input />
        </Form.Item>

        <Form.Item
          label="Email"
          name="email"
          rules={[
            { required: true, message: "This field is required!" },
            { type: "email", message: "This is not a valid email." },
          ]}
        >
          <Input disabled />
        </Form.Item>

        <Form.Item label="Access Token" name="access_token">
          <Input.Password disabled />
        </Form.Item>

        <Button
          type="link"
          onClick={() => navigator.clipboard.writeText(user.access_token)}
          style={{ marginBottom: 16 }}
        >
          Copy Access Token
        </Button>

        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>
            Update Profile
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default ProfilePage;
