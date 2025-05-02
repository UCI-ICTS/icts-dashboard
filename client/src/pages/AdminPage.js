// src/components/ManageAdministrators.js

import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import dayjs from "dayjs";
import {
  fetchUsers,
  addUser,
  updateUser,
  deleteUser,
} from "../slices/accountSlice";
import {
  Alert,
  Button,
  Form,
  Input,
  Modal,
  Popconfirm,
  Select,
  Spin,
  Table,
  Tooltip,
  message,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
} from "@ant-design/icons";
import ErrorBoundary from "../components/ErrorBoundary";

const { Option } = Select;

const ManageAdministrators = () => {
  const dispatch = useDispatch();
  const currentUsername = useSelector((state) => state.account.user?.username);
  const { staff = [], loading, error } = useSelector(
    (state) => state.account || {}
  );

  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingMember, setEditingMember] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    dispatch(fetchUsers()).catch(() =>
      message.error("Failed to load members")
    );
  }, [dispatch]);

  const handleOpenModal = (member = null) => {
    setEditingMember(member);
    form.setFieldsValue({
      first_name: member?.first_name || "",
      last_name: member?.last_name || "",
      email: member?.email || "",
      role: staff?.is_superuser ? "admin" : staff?.is_staff ? "staff" : "staff",
    });
    setIsModalVisible(true);
  };


  const handleSubmit = async () => {
    const values = await form.validateFields();
    console.log(values)
    const updatedValues = {
      ...values,
      is_superuser: values.role === "admin",
      is_staff: values.role === "admin" || values.role === "staff",
    };

    delete updatedValues.role;

    if (editingMember) {
      dispatch(updateUser({ id: editingMember.username, ...updatedValues }));
    } else {
      dispatch(addUser(updatedValues));
    }

    setIsModalVisible(false);
    dispatch(fetchUsers());
  };

  const handleDelete = async (id) => {
    dispatch(deleteUser(id));
    message.success("Staff deleted.");
    dispatch(fetchUsers());
  };

  const columns = [
    {
      title: "Given Name",
      key: "first_name",
      render: (text, record) => `${record.first_name}`,
    },
    {
      title: "Family Name",
      key: "last_name",
      render: (text, record) => `${record.last_name}`,
    },
    { title: "Email", dataIndex: "email" },
    {
      title: "Role",
      render: (_, record) => (record.is_superuser ? "Admin" : record.is_staff ? "Staff" : "User"),
      dataIndex: "role"
    },
    {
      title: "Date Joined",
      dataIndex: "date_joined",
      render: (date) => date ? dayjs(date).format("MMM D, YYYY h:mm A") : "N/A",
    },
    {
      title: "Actions",
      render: (_, record) => {
        const isSelf = record?.username && record.username === currentUsername;
        return (
          <>
            <Tooltip title="Edit administrator">
              <Button
                icon={<EditOutlined />}
                onClick={() => handleOpenModal(record)}
                style={{ marginRight: 8 }}
              />
            </Tooltip>
            <Tooltip title={isSelf ? "You cannot delete yourself" : "Delete Administrator"}>
              <Popconfirm
                title="Are you sure you want to delete this user?"
                onConfirm={() => handleDelete(record?.username)}
                okText="Yes"
                cancelText="No"
                disabled={isSelf}
              >
                <Button
                  icon={<DeleteOutlined />}
                  danger
                  disabled={isSelf}
                />
              </Popconfirm>
            </Tooltip>
          </>
        );
      },
    }
  ];

  return (
    <ErrorBoundary>
      <div style={{ padding: 20 }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => handleOpenModal()}
          style={{ marginBottom: 20 }}
        >
          Add New Staff
        </Button>

        {loading ? (
          <Spin />
        ) : error ? (
          <Alert
            message="Error fetching staff"
            description={error}
            type="error"
            showIcon
          />
        ) : ( null)}
          <Table
            columns={columns}
            dataSource={staff.filter(Boolean)}
            rowKey="username"
            bordered
          />
        <Modal
          title={editingMember ? "Edit Member" : "Add New Member"}
          open={isModalVisible}
          onCancel={() => setIsModalVisible(false)}
          onOk={handleSubmit}
        >
          <Form form={form} layout="vertical">
            <Form.Item
              name="first_name"
              label="Given Name"
              rules={[{ required: true, message: "Enter given(first) name" }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="last_name"
              label="Family Name"
              rules={[{ required: true, message: "Enter family(last) name" }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="email"
              label="Email"
              rules={[{ required: true, message: "Enter email" }]}
            >
              <Input type="email" />
            </Form.Item>
            <Form.Item
              name="role"
              label="Role"
              rules={[{ required: true, message: "Select a role" }]}
            >
              <Select placeholder="Select role">
                <Option value="admin">Admin</Option>
                <Option value="staff">Staff</Option>
              </Select>
            </Form.Item>
          </Form>
        </Modal>
      </div>
    </ErrorBoundary>
  );
};

export default ManageAdministrators;
