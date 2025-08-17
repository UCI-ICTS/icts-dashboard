// src/pages/profile.js

import React, { useState } from "react";
import { Button, Card, Form, Input, Typography, message } from "antd";
import { EyeTwoTone, EyeInvisibleOutlined } from "@ant-design/icons";
import { useDispatch, useSelector } from "react-redux";
import PasswordReset from "../components/PasswordReset";
import { updateProfile } from "../slices/accountSlice";
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
    dispatch(updateProfile(payload));
    setLoading(false);
  };

  return (
    <Card title={<span className="card-title">User Profile</span>} className="secondary-card">
      <PasswordReset open={open} setOpen={setOpen} />

      <Button onClick={() => setOpen(true)} className="action-btn">
        Change Password
      </Button>

      <Form
        className="profile-form"
        form={form}
        layout="horizontal"
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

        <Form.Item label={
          <Button
          type="secondary"
          size=""
          onClick={() => {
            navigator.clipboard.writeText(user.access_token)
            message.success("Token copied to clipboard")
          }}
          className="action-btn"
        >
          Copy Access Token
        </Button>
        } name="access_token">
          <Input.Password 
            disabled 
            iconRender={visible => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
          />
        </Form.Item>

        <Form.Item>
          <Button className="logout-button" htmlType="submit" loading={loading}>
            Update Profile
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default ProfilePage;
