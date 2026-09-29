// src/pages/AnvilUpload.js
//
// The upload view is a render of the upload's manifest document. Stage
// status comes from manifest.validation.{source,files,package} and
// manifest_state; failure detail comes from tables.by_name.<t>.excluded_rows
// (source) and .file_check_failures (files). Detail is failures-only by
// design (manifest v0.2).

import { useEffect, useState, useMemo } from "react";
import { useDispatch, useSelector } from "react-redux";

import {
  Badge,
  Button,
  Card,
  Col,
  Collapse,
  Descriptions,
  Form,
  Input,
  Layout,
  Modal,
  Row,
  Space,
  Spin,
  Steps,
  Table,
  Tag,
  Typography,
  message,
} from "antd";

import {
  CloudUploadOutlined,
  ReloadOutlined,
} from "@ant-design/icons";

import {
  fetchAnvilUploads,
  fetchAnvilUploadDetail,
  createAnvilUpload,
  initializeAnvilUpload,
  validateAnvilSource,
  generateAnvilTsvs,
  validateAnvilFiles,
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

// ---------------------------------------------------------------------------
// Stage model: derive each pipeline step's display state from the manifest.
// ---------------------------------------------------------------------------

const stageDescription = (entry) => {
  if (!entry) return null;

  const parts = [`${entry.error_count} errors`];

  if (entry.warning_count > 0) {
    parts.push(`${entry.warning_count} warnings`);
  }

  if (entry.provider) {
    parts.push(`via ${entry.provider}`);
  }

  return parts.join(", ");
};

const derivePipelineSteps = (manifest) => {
  const validation = manifest?.validation || {};
  const manifestState = manifest?.manifest_state;
  const initialized = Boolean(manifest);
  const tsvsGenerated =
    manifest?.artifacts?.table_tsvs?.length > 0;

  const validationStep = (entry, { supersededWhen = false, name }) => {
    if (entry) {
      return {
        status: entry.status === "passed" ? "finish" : "error",
        description: stageDescription(entry),
      };
    }

    if (supersededWhen) {
      return {
        status: "wait",
        description: "superseded — rerun",
      };
    }

    return { status: "wait", description: null };
  };

  return [
    {
      key: "initialize",
      title: "Initialize",
      status: initialized ? "finish" : "wait",
      description: initialized
        ? `${manifest?.tables?.included?.length || 0} tables selected`
        : null,
      runnable: true,
    },
    {
      key: "source",
      title: "Validate Source",
      ...validationStep(validation.source, { name: "source" }),
      runnable: initialized,
    },
    {
      key: "tsvs",
      title: "Generate TSVs",
      status: tsvsGenerated ? "finish" : "wait",
      description: tsvsGenerated
        ? `${manifest.artifacts.table_tsvs.length} files`
        : null,
      runnable: Boolean(validation.source),
    },
    {
      key: "files",
      title: "Validate Files",
      ...validationStep(validation.files, {
        supersededWhen: tsvsGenerated && validation.files === null
          && manifestState === "package_generated"
          && Boolean(validation.source),
      }),
      runnable: tsvsGenerated,
    },
    {
      key: "package",
      title: "Validate Package",
      ...validationStep(validation.package, {
        supersededWhen: tsvsGenerated && validation.package === null
          && manifestState === "package_generated"
          && Boolean(validation.source),
      }),
      runnable: tsvsGenerated,
    },
  ];
};

// ---------------------------------------------------------------------------
// Problems: flatten failures-only manifest detail into renderable rows.
// ---------------------------------------------------------------------------

const collectProblems = (manifest) => {
  const byName = manifest?.tables?.by_name || {};
  const excluded = [];
  const fileFailures = [];
  const unverified = [];

  Object.entries(byName).forEach(([tableName, entry]) => {
    (entry.excluded_rows || []).forEach((row) => {
      excluded.push({
        key: `${tableName}:${row.pk}`,
        table: tableName,
        pk: row.pk,
        reason: row.reason,
        errors: row.errors || [],
      });
    });

    (entry.file_check_failures || []).forEach((row) => {
      const target = row.status === "FAIL" ? fileFailures : unverified;

      target.push({
        key: `${tableName}:${row.pk}:${row.status}`,
        table: tableName,
        pk: row.pk,
        status: row.status,
        checks: row.checks || [],
      });
    });
  });

  return { excluded, fileFailures, unverified };
};

const excludedRowColumns = [
  { title: "Table", dataIndex: "table", key: "table" },
  { title: "Row", dataIndex: "pk", key: "pk" },
  { title: "Reason", dataIndex: "reason", key: "reason" },
  {
    title: "Errors",
    dataIndex: "errors",
    key: "errors",
    render: (errors) => (
      <>
        {errors.map((error, index) => (
          <div key={index}>
            <Text code>{error.field}</Text> {error.error}
          </div>
        ))}
      </>
    ),
  },
];

const fileFailureColumns = [
  { title: "Table", dataIndex: "table", key: "table" },
  { title: "Row", dataIndex: "pk", key: "pk" },
  {
    title: "Status",
    dataIndex: "status",
    key: "status",
    render: (status) => (
      <Tag color={status === "FAIL" ? "red" : "gold"}>{status}</Tag>
    ),
  },
  {
    title: "Failed checks",
    dataIndex: "checks",
    key: "checks",
    render: (checks) => (
      <>
        {checks.map((check, index) => (
          <div key={index}>
            <Text code>{check.check}</Text> {check.detail || check.status}
          </div>
        ))}
      </>
    ),
  },
];

// ---------------------------------------------------------------------------
// Package summary: one row per table merging source counts, file checks,
// and TSV artifact info.
// ---------------------------------------------------------------------------

const buildPackageSummary = (manifest) => {
  const byName = manifest?.tables?.by_name || {};
  const tsvsByTable = Object.fromEntries(
    (manifest?.artifacts?.table_tsvs || []).map((entry) => [
      entry.table_name,
      entry,
    ])
  );

  return (manifest?.tables?.included || []).map((tableName) => {
    const entry = byName[tableName] || {};
    const tsv = tsvsByTable[tableName];

    return {
      key: tableName,
      table: tableName,
      sourceStatus: entry.source_status,
      includedRows: entry.included_row_count,
      sourceRows: entry.source_row_count,
      excludedRows: entry.excluded_row_count || 0,
      files: entry.files || null,
      fileFailures: (entry.file_check_failures || []).filter(
        (row) => row.status ==="FAIL"
      ).length,
      tsvRows: tsv?.row_count,
      tsvBytes: tsv?.byte_size,
    };
  });
};

const packageSummaryColumns = [
  { title: "Table", dataIndex: "table", key: "table" },
  {
    title: "Source rows",
    key: "rows",
    render: (_, record) => {
      if (record.sourceRows === undefined) return "-";

      const text = `${record.includedRows}/${record.sourceRows}`;

      return record.excludedRows > 0 ? (
        <Badge count={`${record.excludedRows} excluded`} color="orange">
          <span style={{ paddingRight: 8 }}>{text}</span>
        </Badge>
      ) : (
        text
      );
    },
  },
  {
    title: "File checks",
    key: "files",
    render: (_, record) => {
      if (!record.files) return "—";

      const {
        checked_row_count,
        passed_row_count,
        failed_row_count,
        unverified_row_count
      } =  record.files;

      if (failed_row_count > 0) {
        return (
          <Tag color="red">
            {failed_row_count} failed / {checked_row_count}
          </Tag>
        );
      }

      if (unverified_row_count > 0) {
        return (
          <Tag color="gold">
            {passed_row_count} passed, {unverified_row_count} unverified
          </Tag>
        );
      }

      return (
        <Tag color="green">
          {passed_row_count}/{checked_row_count} passed
          </Tag>
      );
    },
  },
  {
    title: "TSV",
    key: "tsv",
    render: (_, record) =>
      record.tsvBytes !== undefined
        ? `${record.tsvRows} rows, ${record.tsvBytes} B`
        : "—",
  },
];

// ---------------------------------------------------------------------------

const validationRunColumns = [
  { title: "Validator", dataIndex: "validator_version", key: "validator_version" },
  {
    title: "Status",
    dataIndex: "status",
    key: "status",
    render: (status) => <Tag color={getStatusColor(status)}>{status || "-"}</Tag>,
  },
  { title: "Errors", dataIndex: "error_count", key: "error_count" },
  { title: "Warnings", dataIndex: "warning_count", key: "warning_count" },
  {
    title: "Started",
    dataIndex: "started_at",
    key: "started_at",
    render: (value) => (value ? new Date(value).toLocaleString() : "-"),
  },
  {
    title: "Message",
    dataIndex: "message",
    key: "message",
    render: (value) => value || "-",
  },
];

const AnvilUploads = () => {
  const [form] = Form.useForm();
  const {
    uploads,
    selectedUpload,
    actionStatus,
    activeAction,
  } = useSelector((state) => state.anvil);
  const [createOpen, setCreateOpen] = useState(false);
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(fetchAnvilUploads());
  }, [dispatch]);

  const fetchUploadDetail = (uploadId) => {
    dispatch(fetchAnvilUploadDetail(uploadId));
  };

  const handleCreateUpload = async (values) => {
    try {
      await dispatch(createAnvilUpload(values)).unwrap();
      setCreateOpen(false);
      form.resetFields();
      dispatch(fetchAnvilUploads());
    } catch (error) {
      // Error message already shown by the thunk; keep the modal open so
      // the user can correct the form.
    }
  };

  const runUploadAction = async ({ actionThunk, label }) => {
    const uploadId = selectedUpload?.upload_id;

    if (!uploadId) {
      message.warning("Select an upload first.");
      return;
    }

    try {
      await dispatch(actionThunk).unwrap();
    } catch (error) {
      console.error(`${label} failed`, error);
    } finally {
      // Always refetch: stage results, manifest, and derived status all
      // change server-side regardless of pass/fail.
      dispatch(fetchAnvilUploadDetail(uploadId));
      dispatch(fetchAnvilUploads());
    }
  };

  const stageActions = {
    initialize: () =>
      runUploadAction({
        actionThunk: initializeAnvilUpload(selectedUpload.upload_id),
        label: "Initialize package",
      }),
    source: () =>
      runUploadAction({
        actionThunk: validateAnvilSource(selectedUpload.upload_id),
        label: "Source validation",
      }),
    tsvs: () =>
      runUploadAction({
        actionThunk: generateAnvilTsvs({ uploadId: selectedUpload.upload_id }),
        label: "Generate TSVs",
      }),
    files: () =>
      runUploadAction({
        actionThunk: validateAnvilFiles(selectedUpload.upload_id),
        label: "File validation",
      }),
    package: () =>
      runUploadAction({
        actionThunk: validateAnvilPackage(selectedUpload.upload_id),
        label: "Package validation",
      }),
  };

  const manifest = selectedUpload?.manifest;
  const steps = useMemo(
    () => derivePipelineSteps(manifest, selectedUpload),
    [manifest, selectedUpload]
  );
  const problems = useMemo(() => collectProblems(manifest), [manifest]);
  const packageSummary = useMemo(
    () => buildPackageSummary(manifest),
    [manifest]
  );
  
  const hasFailures =
    problems.excluded.length > 0 ||
    problems.fileFailures.length > 0;

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
      render: (status) => (
        <Tag color={getStatusColor(status)}>{status || "-"}</Tag>
      ),
    },
    {
      title: "GREGoR Version",
      dataIndex: "gregor_model_version",
      key: "gregor_model_version",
    },
    {
      title: "Updated",
      dataIndex: "updated_at",
      key: "updated_at",
      render: (value) => (value ? new Date(value).toLocaleString() : "-"),
    },
  ];

  return (
    <Layout className="layout-container">
      <Header className="primary-header">
        <Title className="primary-title">AnVIL Uploads</Title>
      </Header>

      <Content style={{ padding: 24 }}>
        <Spin spinning={actionStatus === "loading"}>
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
                  onClick={() => dispatch(fetchAnvilUploads())}
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
                    <Space>
                      {manifest?.manifest_state && (
                        <Tag>{manifest.manifest_state}</Tag>
                      )}
                      <Tag color={getStatusColor(selectedUpload.status)}>
                        {selectedUpload.status}
                      </Tag>
                    </Space>
                  }
                >
                  <Descriptions bordered size="small" column={3}>
                    <Descriptions.Item label="GREGoR Model">
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
                  </Descriptions>

                  <Card size="small" title="Pipeline" style={{ marginTop: 16 }}>
                    <Steps
                      size="small"
                      labelPlacement="vertical"
                      items={steps.map((step) => ({
                        title: step.title,
                        status: step.status,
                        description: step.description,
                      }))}
                    />
                    <Space wrap style={{ marginTop: 16 }}>
                      {steps.map((step) => (
                        <Button
                          key={step.key}
                          size="small"
                          type={
                            step.status === "error" ? "primary" : "default"
                          }
                          danger={step.status === "error"}
                          disabled={
                            !step.runnable || actionStatus === "loading"
                          }
                          loading={
                            activeAction &&
                            activeAction
                              .toLowerCase()
                              .includes(step.key === "tsvs" ? "tsvs" : step.key)
                          }
                          onClick={stageActions[step.key]}
                        >
                          Run {step.title}
                        </Button>
                      ))}
                    </Space>
                  </Card>

                  <Collapse
                    style={{ marginTop: 16 }}
                    defaultActiveKey={[
                      ...(hasFailures ? ["problems"] : []),
                      ...(packageSummary.length > 0 ? ["package"] : []),
                    ]}
                    items={[
                      ...(hasFailures || problems.unverified.length > 0
                        ? [
                            {
                              key: "problems",
                              label: (
                                <Space>
                                  Problems
                                  {problems.excluded.length > 0 && (
                                    <Tag color="orange">
                                      {problems.excluded.length} excluded rows
                                    </Tag>
                                  )}
                                  {problems.fileFailures.length > 0 && (
                                    <Tag color="red">
                                      {problems.fileFailures.length} file failures
                                    </Tag>
                                  )}
                                  {problems.unverified.length > 0 && (
                                    <Tag color="gold">
                                      {problems.unverified.length} unverified
                                    </Tag>
                                  )}
                                </Space>
                              ),
                              children: (
                                <>
                                  {problems.excluded.length > 0 && (
                                    <>
                                      <Text strong>
                                        Rows excluded by source validation
                                        (omitted from the package)
                                      </Text>
                                      <Table
                                        rowKey="key"
                                        dataSource={problems.excluded}
                                        columns={excludedRowColumns}
                                        pagination={{ pageSize: 5 }}
                                        size="small"
                                        style={{
                                          marginTop: 8,
                                          marginBottom: 16,
                                        }}
                                      />
                                    </>
                                  )}

                                  {problems.fileFailures.length > 0 && (
                                    <>
                                      <Text strong>File check failures</Text>
                                      <Table
                                        rowKey="key"
                                        dataSource={problems.fileFailures}
                                        columns={fileFailureColumns}
                                        pagination={{ pageSize: 5 }}
                                        size="small"
                                        style={{
                                          marginTop: 8,
                                          marginBottom: 16,
                                        }}
                                      />
                                    </>
                                  )}

                                  {problems.unverified.length > 0 && (
                                    <>
                                      <Text strong>
                                        Files not verifiable from this server
                                      </Text>
                                      <Text
                                        type="secondary"
                                        style={{
                                          display: "block",
                                          marginBottom: 8,
                                        }}
                                      >
                                        These files could not be retrieved for
                                        hashing or header checks. They are
                                        warnings, not failures; presence is
                                        enforced on the AnVIL side after
                                        transfer.
                                      </Text>
                                      <Table
                                        rowKey="key"
                                        dataSource={problems.unverified}
                                        columns={fileFailureColumns}
                                        pagination={{ pageSize: 5 }}
                                        size="small"
                                      />
                                    </>
                                  )}
                                </>
                              ),
                            },
                          ]
                        : []),
                      ...(packageSummary.length > 0
                        ? [
                            {
                              key: "package",
                              label: "Package Contents",
                              children: (
                                <Table
                                  rowKey="key"
                                  dataSource={packageSummary}
                                  columns={packageSummaryColumns}
                                  pagination={{ pageSize: 25 }}
                                  size="small"
                                />
                              ),
                            },
                          ]
                        : []),
                      {
                        key: "history",
                        label: `Validation history (${
                          selectedUpload.validation_runs?.length || 0
                        } runs)`,
                        children: (
                          <Table
                            rowKey="id"
                            dataSource={selectedUpload.validation_runs || []}
                            columns={validationRunColumns}
                            pagination={{ pageSize: 10 }}
                            size="small"
                          />
                        ),
                      },
                    ]}
                  />
                  
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

          <Form.Item label="GREGoR Model Version" name="gregor_model_version">
            <Input />
          </Form.Item>

          <Form.Item label="Notes" name="notes">
            <Input.TextArea rows={3} />
          </Form.Item>

          <Space>
            <Button
              type="primary"
              htmlType="submit"
              loading={activeAction === "createAnvilUpload"}
            >
              Create
            </Button>
            <Button onClick={() => setCreateOpen(false)}>Cancel</Button>
          </Space>
        </Form>
      </Modal>
    </Layout>
  );
};

export default AnvilUploads;
