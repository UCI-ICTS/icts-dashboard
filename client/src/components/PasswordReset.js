// src/components/PasswordReset.js

import React from "react";
import { Modal, Form, Input, Button, message } from "antd";
import { useDispatch, useSelector } from "react-redux";
import { changePassword } from "../slices/accountSlice";

export default function PasswordReset({ open, setOpen }) {
  const [form] = Form.useForm();
  const dispatch = useDispatch();
  const user = useSelector((state) => state.account.user);

  const handleOk = () => {
    form.submit();
  };

  const handleCancel = () => {
    setOpen(false);
    form.resetFields();
  };

  const onFinish = (values) => {
    console.log("Dispach values: ", values)
    dispatch(changePassword({ ...values }));
    setOpen(false);
    form.resetFields();
  };

  return (
    <Modal
      title="Reset Password"
      open={open}
      onOk={handleOk}
      onCancel={handleCancel}
      okText="Submit"
      cancelText="Cancel"
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
        initialValues={{ old_password: "", new_password: "", confirm_password: "" }}
      >
        {/*Hidden email field for accessibility  https://goo.gl/9p2vKq */}
        <Form.Item name="email">
        <Input
          type="email"
          autoComplete="username"
          style={{
            position: "absolute",
            width: 1,
            height: 1,
            padding: 0,
            margin: 0,
            overflow: "hidden",
            clip: "rect(0 0 0 0)",
            whiteSpace: "nowrap",
            border: 0,
          }}
        />
        </Form.Item>

        <Form.Item
          label="Old Password"
          name="old_password"
          rules={[
            { required: true, message: "Please enter your current password" }
          ]}
        >
          <Input.Password autoComplete="current-password" />
        </Form.Item>

        <Form.Item
          label="New Password"
          name="new_password"
          rules={[
            { required: true, message: "Please enter your new password" },
            { min: 6, max: 40, message: "Password must be 6–40 characters" },
          ]}
        >
          <Input.Password autoComplete="new-password" />
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
      </Form>
    </Modal>
  );
}
