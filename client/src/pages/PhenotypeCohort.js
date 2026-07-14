// src/pages/PhenotypeCohort.js

import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  Alert,
  Button,
  Card,
  Checkbox,
  Col,
  Descriptions,
  Form,
  Input,
  Layout,
  Row,
  Space,
  Spin,
  Table,
  Tag,
  Typography,
} from "antd";
import {
  MinusCircleOutlined,
  PlusOutlined,
} from "@ant-design/icons";

import {
  createPhenotypeCohort,
  clearPhenotypeCohort,
} from "../slices/dataSlice";

const { Header, Content } = Layout;
const { Title, Text } = Typography;


const participantColumns = [
  {
    title: "Participant ID",
    dataIndex: "participant_id",
    key: "participant_id",
    fixed: "left",
  },
  {
    title: "Family ID",
    dataIndex: "family_id",
    key: "family_id",
  },
  {
    title: "Relationship",
    dataIndex: "proband_relationship",
    key: "proband_relationship",
  },
  {
    title: "Affected Status",
    dataIndex: "affected_status",
    key: "affected_status",
  },
  {
    title: "Solve Status",
    dataIndex: "solve_status",
    key: "solve_status",
  },
  {
    title: "Age at Enrollment",
    dataIndex: "age_at_enrollment",
    key: "age_at_enrollment",
    render: (value) => value ?? "Unknown",
  },
  {
    title: "Needs Review",
    dataIndex: "needs_review",
    key: "needs_review",
    render: (value) => (
      <Tag color={value ? "warning" : "default"}>
        {value ? "Yes" : "No"}
      </Tag>
    ),
  },
];


const TermTags = ({ values = [] }) => {
  if (!Array.isArray(values) || values.length === 0) {
    return <Text type="secondary">None</Text>;
  }

  return (
    <Space wrap>
      {values.map((value, index) => (
        <Tag key={`${value}-${index}`}>
          {value}
        </Tag>
      ))}
    </Space>
  );
};


const ResolvedTerms = ({ terms = [] }) => {
  if (!Array.isArray(terms) || terms.length === 0) {
    return <Text type="secondary">No terms resolved</Text>;
  }

  return (
    <Space direction="vertical" size={4}>
      {terms.map((term, index) => (
        <div key={`${term.input || term.hpo_id}-${index}`}>
          {term.resolved === false ? (
            <>
              <Tag color="error">Unresolved</Tag>
              <Text>{term.input}</Text>
            </>
          ) : (
            <>
              <Tag color="success">{term.hpo_id}</Tag>
              <Text>{term.label || term.input}</Text>

              {term.input && term.input !== term.label && (
                <Text type="secondary">
                  {" "}
                  — submitted as “{term.input}”
                </Text>
              )}
            </>
          )}
        </div>
      ))}
    </Space>
  );
};


const CohortSummary = ({ cohort }) => {
  if (!cohort) {
    return (
      <Card className="text-area-input">
        <Text type="secondary">
          Submit one or more HPO terms or identifiers to build a phenotype
          cohort.
        </Text>
      </Card>
    );
  }

  const summary = cohort.summary || {};

  return (
    <Card
      title="Phenotype Cohort Definition"
      className="text-area-input"
    >
      <Descriptions
        bordered
        column={{
          xs: 1,
          sm: 1,
          md: 2,
          lg: 2,
          xl: 2,
          xxl: 2,
        }}
        size="small"
      >
        <Descriptions.Item
          label="Submitted terms"
          span={2}
        >
          <TermTags values={cohort.submitted_terms} />
        </Descriptions.Item>

        <Descriptions.Item
          label="Resolved terms"
          span={2}
        >
          <ResolvedTerms terms={cohort.resolved_terms} />
        </Descriptions.Item>

        <Descriptions.Item
          label="Root HPO IDs"
          span={2}
        >
          <TermTags values={cohort.root_hpo_ids} />
        </Descriptions.Item>

        <Descriptions.Item label="Expanded HPO terms">
          {cohort.cohort_hpo_term_count ?? 0}
        </Descriptions.Item>

        <Descriptions.Item label="Include descendants">
          <Tag color={cohort.include_descendants ? "success" : "default"}>
            {cohort.include_descendants ? "Yes" : "No"}
          </Tag>
        </Descriptions.Item>

        <Descriptions.Item label="Present phenotypes only">
          <Tag color={cohort.present_only ? "success" : "default"}>
            {cohort.present_only ? "Yes" : "No"}
          </Tag>
        </Descriptions.Item>

        <Descriptions.Item label="Total enrolled">
          {summary.total_enrolled ?? 0}
        </Descriptions.Item>

        <Descriptions.Item label="Adults at enrollment">
          {summary.adult_at_enrollment ?? 0}
        </Descriptions.Item>

        <Descriptions.Item label="Solved">
          {summary.solved ?? 0}
        </Descriptions.Item>

        {"missing_age_at_enrollment" in summary && (
          <Descriptions.Item label="Missing enrollment age">
            {summary.missing_age_at_enrollment ?? 0}
          </Descriptions.Item>
        )}
      </Descriptions>
    </Card>
  );
};


const PhenotypeCohort = () => {
  const [form] = Form.useForm();
  const dispatch = useDispatch();

  /*
   * Adjust this selector if your fulfilled reducer stores the response under
   * a different state.data key.
   */
  const {
    phenotype_cohort,
    status,
    error,
  } = useSelector((state) => state.data);

  const cohort = phenotype_cohort || null;
  const participants = Array.isArray(cohort?.participants)
    ? cohort.participants
    : [];

  useEffect(() => {
    if (!form.getFieldValue("submitted_terms")) {
      form.setFieldsValue({
        submitted_terms: [""],
        include_descendants: true,
        present_only: true,
      });
    }
  }, [form]);

  const onFinish = (values) => {
    const submittedTerms = values.submitted_terms
      .map((term) => term?.trim())
      .filter(Boolean);

    dispatch(
      createPhenotypeCohort({
        ...values,
        terms: submittedTerms,
      })
    );
  };

  const handleClear = () => {
    form.resetFields();

    form.setFieldsValue({
      submitted_terms: [""],
      include_descendants: true,
      present_only: true,
    });

    dispatch(clearPhenotypeCohort());
  };

  return (
    <Layout className="layout-container">
      <Header className="primary-header">
        <Title className="primary-title">
          Phenotype Cohort Builder
        </Title>
      </Header>

      <Content>
        <Spin
          spinning={status === "loading"}
          tip="Building phenotype cohort..."
        >
          <Form
            form={form}
            name="phenotype_cohort"
            layout="vertical"
            onFinish={onFinish}
            initialValues={{
              submitted_terms: [""],
              include_descendants: true,
              present_only: true,
            }}
          >
            <CohortSummary cohort={cohort} />

            {error && (
              <Alert
                type="error"
                showIcon
                message="Unable to build phenotype cohort"
                description={
                  typeof error === "string"
                    ? error
                    : "The cohort request failed."
                }
                style={{ marginTop: 16 }}
              />
            )}

            <Card
              title="Cohort Search"
              style={{ marginTop: 16 }}
            >
              <Form.List
                name="submitted_terms"
                rules={[
                  {
                    validator: async (_, terms) => {
                      const validTerms = (terms || []).filter(
                        (term) => term?.trim()
                      );

                      if (validTerms.length === 0) {
                        throw new Error(
                          "Enter at least one HPO term or HPO identifier."
                        );
                      }
                    },
                  },
                ]}
              >
                {(fields, { add, remove }, { errors }) => (
                  <>
                    <Row gutter={[12, 12]} align="bottom">
                      <Col flex="auto">
                        <Space
                          direction="vertical"
                          style={{ width: "100%" }}
                        >
                          {fields.map(({ key, name, ...restField }) => (
                            <Space
                              key={key}
                              align="baseline"
                              style={{
                                display: "flex",
                                width: "100%",
                              }}
                            >
                              <Form.Item
                                {...restField}
                                name={name}
                                style={{
                                  flex: 1,
                                  marginBottom: 0,
                                }}
                                rules={[
                                  {
                                    required: true,
                                    whitespace: true,
                                    message:
                                      "Enter an HPO term or remove this row.",
                                  },
                                ]}
                              >
                                <Input
                                  placeholder={
                                    "HPO term, synonym, or ID — e.g. cerebellar ataxia or HP:0001251"
                                  }
                                />
                              </Form.Item>

                              <Button
                                danger
                                type="text"
                                icon={<MinusCircleOutlined />}
                                aria-label="Remove submitted term"
                                disabled={fields.length === 1}
                                onClick={() => remove(name)}
                              />
                            </Space>
                          ))}
                        </Space>

                        <Form.ErrorList errors={errors} />
                      </Col>

                      <Col>
                        <Button
                          type="dashed"
                          icon={<PlusOutlined />}
                          onClick={() => add("")}
                        >
                          Add term
                        </Button>
                      </Col>
                    </Row>
                  </>
                )}
              </Form.List>

              <Row
                gutter={[16, 12]}
                align="middle"
                style={{ marginTop: 16 }}
              >
                <Col>
                  <Form.Item
                    name="include_descendants"
                    valuePropName="checked"
                    noStyle
                  >
                    <Checkbox>
                      Include descendant HPO terms
                    </Checkbox>
                  </Form.Item>
                </Col>

                <Col>
                  <Form.Item
                    name="present_only"
                    valuePropName="checked"
                    noStyle
                  >
                    <Checkbox>
                      Present phenotypes only
                    </Checkbox>
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item style={{ marginTop: 16, marginBottom: 0 }}>
                <Space>
                  <Button
                    type="primary"
                    htmlType="submit"
                    className="logout-button"
                  >
                    Submit
                  </Button>

                  <Button
                    danger
                    type="default"
                    className="logout-button"
                    onClick={handleClear}
                  >
                    Clear
                  </Button>
                </Space>
              </Form.Item>
            </Card>
          </Form>

          <Card
            title={`Participants (${participants.length})`}
            style={{ marginTop: 16 }}
          >
            <Table
              rowKey="participant_id"
              className="table"
              dataSource={participants}
              columns={participantColumns}
              pagination={{
                defaultPageSize: 25,
                showSizeChanger: true,
                pageSizeOptions: ["25", "50", "100"],
                showTotal: (total) =>
                  `${total} participant${total === 1 ? "" : "s"}`,
              }}
              scroll={{
                x: "max-content",
              }}
              locale={{
                emptyText: cohort
                  ? "No participants matched this phenotype cohort."
                  : "Submit HPO terms to generate a participant cohort.",
              }}
            />
          </Card>
        </Spin>
      </Content>
    </Layout>
  );
};

export default PhenotypeCohort;
