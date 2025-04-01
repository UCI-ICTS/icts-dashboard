import React from 'react';
import { Form, Input, Button, Checkbox } from 'antd';

const AddUserForm = ({ onSubmit }) => {
  const [form] = Form.useForm();

  const handleSubmit = (values) => {
    onSubmit(values);
    form.resetFields();
  };

  return (
    <Form form={form} onFinish={handleSubmit} layout="vertical">
      <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}>
        <Input />
      </Form.Item>
      <Form.Item name="first_name" label="First Name" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <Form.Item name="last_name" label="Last Name" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <Form.Item name="specialization" label="Specialization">
        <Input />
      </Form.Item>
      <Form.Item name="phone_number" label="Phone Number">
        <Input />
      </Form.Item>
      <Form.Item name="institution" label="Institution">
        <Input />
      </Form.Item>
      <Form.Item name="is_staff" valuePropName="checked">
        <Checkbox>Is Staff</Checkbox>
      </Form.Item>
      <Form.Item>
        <Button type="primary" htmlType="submit">
          Add User
        </Button>
      </Form.Item>
    </Form>
  );
};

export default AddUserForm;