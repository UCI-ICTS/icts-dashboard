// src/pages/AnvilUploads.js

import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import {
  Alert,
  Button,
  Card,
  Col,
  Descriptions,
  Form,
  Input,
  Layout,
  Modal,
  Row,
  Space,
  Spin,
  Table,
  Tag,
  Typography,
  message,
} from "antd";

import {
  CheckCircleOutlined,
  CloudUploadOutlined,
  FileDoneOutlined,
  FileTextOutlined,
  PlayCircleOutlined,
  ReloadOutlined,
} from "@ant-design/icons";

import {
    fetchAnvilUploads,
    fetchAnvilUploadDetail,
    createAnvilUpload,
    initializeAnvilUpload,
    validateAnvilSource,
    generateAnvilTsvs,
    generateAnvilManifest,
    validateAnvilPackage,
} from "../slices/anvilSlice";

const { Header, Content } = Layout;
const { Title, Text } = Typography;

const getStatusColor = (status) => {
  if (!status) return "default";

  const normalized = String(status).toLowerCase();

  if (normalized.includes("failed")) return "red";
  if (normalized.includes("ready")) return "green";
  if (normalized.includes("generated")) return "blue";
  if (normalized.includes("draft")) return "default";
  if (normalized.includes("pending")) return "gold";
  if (normalized.includes("passed")) return "green";

  return "blue";
};

const AnvilUploads = () => {
  const [form] = Form.useForm();
  const {
    uploads,
    selectedUpload,
    status,
    actionStatus,
    activeAction,
    error,
    lastActionResult,
  } = useSelector((state) => state.anvil);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(null);
  const [createOpen, setCreateOpen] = useState(false);
  const dispatch = useDispatch();

  const fetchUploads = () => {
    console.log("fetchUploads")
    dispatch(fetchAnvilUploads());
  }; 
  
  const fetchUploadDetail = (uploadId) => {
    console.log("fetchUploadDetail");
    dispatch(fetchAnvilUploadDetail(uploadId));
  }; 
  
  const handleCreateUpload = (values) => {
    console.log("handleCreateUpload", values)
    dispatch(createAnvilUpload(values))
  }; 

  const runUploadAction = async ({ actionThunk, label }) => {
    const uploadId = selectedUpload?.upload_id;

    if (!uploadId) {
        message.warning("Select an upload first.");
        return;
    }

    console.log("runUploadAction", label);

    try {
        await dispatch(actionThunk).unwrap();
        await dispatch(fetchAnvilUploadDetail(uploadId)).unwrap();
        await dispatch(fetchAnvilUploads()).unwrap();
    } catch (error) {
        console.error(`${label} failed`, error);
    }
  };

  const uploadColumns = [
    {
      title: "Upload ID",
      dataIndex: "upload_id",
      key: "upload_id",
      render: (uploadId) => (
        <Button type="link" onClick={() => fetchUploadDetail(uploadId)}>
          {uploadId}
        </Button>
      ),
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status) => <Tag color={getStatusColor(status)}>{status || "-"}</Tag>,
    },
    {
      title: "GREGoR Version",
      dataIndex: "gregor_model_version",
      key: "gregor_model_version",
    },
    {
      title: "Created",
      dataIndex: "created_at",
      key: "created_at",
      render: (value) => value ? new Date(value).toLocaleString() : "-",
    },
    {
      title: "Updated",
      dataIndex: "updated_at",
      key: "updated_at",
      render: (value) => value ? new Date(value).toLocaleString() : "-",
    },
  ];

  const uploadTableColumns = [
    {
      title: "Table",
      dataIndex: "table_name",
      key: "table_name",
    },
    {
      title: "Status",
      dataIndex: "generation_status",
      key: "generation_status",
      render: (status) => <Tag color={getStatusColor(status)}>{status || "-"}</Tag>,
    },
    {
      title: "Rows",
      dataIndex: "row_count",
      key: "row_count",
    },
    {
      title: "Columns",
      dataIndex: "column_names",
      key: "column_names",
      render: (columns) => Array.isArray(columns) ? columns.length : 0,
    },
    {
      title: "Error",
      dataIndex: "generation_error",
      key: "generation_error",
      render: (value) => value || "-",
    },
  ];

  const artifactColumns = [
    {
      title: "Path",
      dataIndex: "relative_path",
      key: "relative_path",
    },
    {
      title: "Type",
      dataIndex: "artifact_type",
      key: "artifact_type",
    },
    {
      title: "Status",
      dataIndex: "generation_status",
      key: "generation_status",
      render: (status) => <Tag color={getStatusColor(status)}>{status || "-"}</Tag>,
    },
    {
      title: "Bytes",
      dataIndex: "byte_size",
      key: "byte_size",
      render: (value) => value ?? "-",
    },
    {
      title: "SHA-256",
      dataIndex: "sha256",
      key: "sha256",
      render: (value) => value ? `${value.slice(0, 12)}...` : "-",
    },
  ];

  const validationRunColumns = [
    {
      title: "Validator",
      dataIndex: "validator_version",
      key: "validator_version",
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status) => <Tag color={getStatusColor(status)}>{status || "-"}</Tag>,
    },
    {
      title: "Errors",
      dataIndex: "error_count",
      key: "error_count",
    },
    {
      title: "Warnings",
      dataIndex: "warning_count",
      key: "warning_count",
    },
    {
      title: "Started",
      dataIndex: "started_at",
      key: "started_at",
      render: (value) => value ? new Date(value).toLocaleString() : "-",
    },
    {
      title: "Message",
      dataIndex: "message",
      key: "message",
      render: (value) => value || "-",
    },
  ];

  const latestValidationErrors = selectedUpload?.validation_runs
    ?.slice()
    ?.reverse()
    ?.find((run) => run?.summary?.errors?.length > 0)
    ?.summary?.errors || [];

  return (
    <Layout className="layout-container">
      <Header className="primary-header">
        <Title className="primary-title">AnVIL Uploads</Title>
      </Header>

      <Content style={{ padding: 24 }}>
        <Spin spinning={loading || Boolean(actionLoading)}>
          <Row gutter={[16, 16]}>
            <Col span={24}>
              <Space style={{ marginBottom: 16 }}>
                <Button
                  type="primary"
                  icon={<CloudUploadOutlined />}
                  onClick={() => setCreateOpen(true)}
                >
                  Create Upload
                </Button>

                <Button
                  icon={<ReloadOutlined />}
                  onClick={fetchUploads}
                >
                  Refresh
                </Button>
              </Space>

              <Table
                rowKey="upload_id"
                className="table"
                dataSource={uploads}
                columns={uploadColumns}
                pagination={{ pageSize: 10 }}
              />
            </Col>

            {selectedUpload && (
              <Col span={24}>
                <Card
                  title={`Upload: ${selectedUpload.upload_id}`}
                  extra={
                    <Tag color={getStatusColor(selectedUpload.status)}>
                      {selectedUpload.status}
                    </Tag>
                  }
                >
                  <Descriptions bordered size="small" column={2}>
                    <Descriptions.Item label="Upload ID">
                      {selectedUpload.upload_id}
                    </Descriptions.Item>
                    <Descriptions.Item label="Status">
                      <Tag color={getStatusColor(selectedUpload.status)}>
                        {selectedUpload.status}
                      </Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="GREGoR Model Version">
                      {selectedUpload.gregor_model_version}
                    </Descriptions.Item>
                    <Descriptions.Item label="Created">
                      {selectedUpload.created_at
                        ? new Date(selectedUpload.created_at).toLocaleString()
                        : "-"}
                    </Descriptions.Item>
                    <Descriptions.Item label="Updated">
                      {selectedUpload.updated_at
                        ? new Date(selectedUpload.updated_at).toLocaleString()
                        : "-"}
                    </Descriptions.Item>
                    <Descriptions.Item label="Notes" span={2}>
                      {selectedUpload.notes || "-"}
                    </Descriptions.Item>
                  </Descriptions>

                  <Card
                    size="small"
                    title="Workflow"
                    style={{ marginTop: 16 }}
                  >
                    <Space wrap>
                    <Button
                        icon={<PlayCircleOutlined />}
                        disabled={!selectedUpload?.upload_id || actionStatus === "loading"}
                        loading={activeAction === "initializeAnvilUpload"}
                        onClick={() =>
                        runUploadAction({
                            actionThunk: initializeAnvilUpload(selectedUpload.upload_id),
                            label: "Initialize package",
                        })
                        }
                    >
                        Initialize
                    </Button>

                    <Button
                        icon={<CheckCircleOutlined />}
                        disabled={!selectedUpload?.upload_id || actionStatus === "loading"}
                        loading={activeAction === "validateAnvilSource"}
                        onClick={() =>
                        runUploadAction({
                            actionThunk: validateAnvilSource(selectedUpload.upload_id),
                            label: "Source validation",
                        })
                        }
                    >
                        Validate Source
                    </Button>

                    <Button
                        icon={<FileTextOutlined />}
                        disabled={
                        !selectedUpload?.upload_id ||
                        actionStatus === "loading"
                        }
                        loading={activeAction === "generateAnvilTsvs"}
                        onClick={() =>
                        runUploadAction({
                            actionThunk: generateAnvilTsvs({
                            uploadId: selectedUpload.upload_id,
                            }),
                            label: "Generate TSVs",
                        })
                        }
                    >
                        Generate TSVs
                    </Button>

                    <Button
                        icon={<FileDoneOutlined />}
                        disabled={
                        !selectedUpload?.upload_id ||
                        actionStatus === "loading"
                        }
                        loading={activeAction === "generateAnvilManifest"}
                        onClick={() =>
                        runUploadAction({
                            actionThunk: generateAnvilManifest({
                            uploadId: selectedUpload.upload_id,
                            }),
                            label: "Generate manifest",
                        })
                        }
                    >
                        Generate Manifest
                    </Button>

                    <Button
                        type="primary"
                        icon={<CheckCircleOutlined />}
                        disabled={!selectedUpload?.upload_id || actionStatus === "loading"}
                        loading={activeAction === "validateAnvilPackage"}
                        onClick={() =>
                        runUploadAction({
                            actionThunk: validateAnvilPackage(selectedUpload.upload_id),
                            label: "Package validation",
                        })
                        }
                    >
                        Validate Package
                    </Button>
                    </Space>
                  </Card>

                  {latestValidationErrors.length > 0 && (
                    <Alert
                      style={{ marginTop: 16 }}
                      type="error"
                      showIcon
                      message="Latest validation errors"
                      description={
                        <pre style={{ whiteSpace: "pre-wrap", marginBottom: 0 }}>
                          {JSON.stringify(latestValidationErrors.slice(0, 10), null, 2)}
                        </pre>
                      }
                    />
                  )}

                  <Card size="small" title="Validation Runs" style={{ marginTop: 16 }}>
                    <Table
                      rowKey="id"
                      dataSource={selectedUpload.validation_runs || []}
                      columns={validationRunColumns}
                      pagination={false}
                      size="small"
                    />
                  </Card>

                  <Card size="small" title="Upload Tables" style={{ marginTop: 16 }}>
                    <Table
                      rowKey="id"
                      dataSource={selectedUpload.upload_tables || []}
                      columns={uploadTableColumns}
                      pagination={{ pageSize: 10 }}
                      size="small"
                    />
                  </Card>

                  <Card size="small" title="Artifacts" style={{ marginTop: 16 }}>
                    <Table
                      rowKey="id"
                      dataSource={selectedUpload.artifacts || []}
                      columns={artifactColumns}
                      pagination={{ pageSize: 10 }}
                      size="small"
                    />
                  </Card>
                </Card>
              </Col>
            )}
          </Row>
        </Spin>
      </Content>

      <Modal
        title="Create AnVIL Upload"
        open={createOpen}
        onCancel={() => setCreateOpen(false)}
        footer={null}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateUpload}
          initialValues={{
            gregor_model_version: "1.12",
          }}
        >
          <Form.Item
            label="Upload ID"
            name="upload_id"
            rules={[{ required: true, message: "Upload ID is required." }]}
          >
            <Input placeholder="UCI_GREGoR_2026_Q3" />
          </Form.Item>

          <Form.Item
            label="GREGoR Model Version"
            name="gregor_model_version"
          >
            <Input />
          </Form.Item>

          <Form.Item
            label="Notes"
            name="notes"
          >
            <Input.TextArea rows={3} />
          </Form.Item>

          <Space>
            <Button
              type="primary"
              htmlType="submit"
              loading={actionLoading === "create"}
            >
              Create
            </Button>
            <Button onClick={() => setCreateOpen(false)}>
              Cancel
            </Button>
          </Space>
        </Form>
      </Modal>
    </Layout>
  );
};

export default AnvilUploads;