// src/pages/PhenotypeCohort.js

import { useEffect, useMemo, useState } from "react";
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
  message,
  Modal,
  Row,
  Select,
  Space,
  Spin,
  Tag,
  Typography,
} from "antd";
import {
  MinusCircleOutlined,
  PlusOutlined,
} from "@ant-design/icons";

import {
  clearPhenotypeCohort,
  createPhenotypeCohort,
} from "../slices/dataSlice";
import { useTableSettings, buildColumns } from "../utils/tableSettings";
import { defaultVisibleColumns } from "../utils/schemaAndTables";
import GregorTable from "../components/GregorTable";
import TableToolBar from "../components/TableToolBar";
import schemas from "../schemas/v1.12schemas.json";

const { Header } = Layout;
const { Title, Text } = Typography;
const { Option } = Select;


const TermTags = ({ values = [] }) => {
  if (!Array.isArray(values) || values.length === 0) {
    return <Text type="secondary">None</Text>;
  }

  return (
    <Space wrap>
      {values.map((value, index) => (
        <Tag key={`${value}-${index}`}>{value}</Tag>
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
      {terms.map((term, index) => {
        const key = `${term.input || term.hpo_id || "term"}-${index}`;

        if (term.resolved === false) {
          return (
            <div key={key}>
              <Tag color="error">Unresolved</Tag>
              <Text>{term.input}</Text>
            </div>
          );
        }

        return (
          <div key={key}>
            <Tag color="success">{term.hpo_id}</Tag>
            <Text>{term.label || term.input}</Text>

            {term.input && term.input !== term.label ? (
              <Text type="secondary">
                {" "}
                — submitted as “{term.input}”
              </Text>
            ) : null}
          </div>
        );
      })}
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
        column={2}
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

        {Object.prototype.hasOwnProperty.call(
          summary,
          "missing_age_at_enrollment"
        ) ? (
          <Descriptions.Item label="Missing enrollment age">
            {summary.missing_age_at_enrollment ?? 0}
          </Descriptions.Item>
        ) : null}
      </Descriptions>
    </Card>
  );
};


export default function PhenotypeCohort() {
  const [form] = Form.useForm();
  const dispatch = useDispatch();

  const phenotypeCohort = useSelector(
    (state) => state.data.phenotype_cohort
  );

  const status = useSelector(
    (state) => state.data.status
  );

  const cohortError = useSelector(
    (state) =>
      state.data.phenotype_cohort_error ||
      state.data.error
  );

  const schema = schemas.participants || { properties: {} };
  const tableView = "participants";
  const rowKey = "participant_id";
  const rememberUI = Boolean(localStorage.getItem("user"));

  const participants = Array.isArray(phenotypeCohort?.participants)
    ? phenotypeCohort.participants
    : [];

  // ---- Global search and regex toggle ----
  const [useRegex, setUseRegex] = useState(false);
  const [search, setSearch] = useState("");
  const [regexErr, setRegexErr] = useState(null);

  // ---- Advanced filters modal ----
  const [advOpen, setAdvOpen] = useState(false);
  const [draft, setDraft] = useState({});

  // ---- Export modal ----
  const [exportOpen, setExportOpen] = useState(false);
  const [exportFormat, setExportFormat] = useState("TSV");

  // ---- Schema-driven table settings ----
  const dataTable = useTableSettings({
    schema,
    tableView,
    defaults: defaultVisibleColumns[tableView] || [],
    persist: rememberUI,
    storagePrefix: "uci:phenotypeCohortTableSettings",
  });

  const {
    sorter,
    filters,
    setSorter,
    setFilters,
  } = dataTable;

  const columns = buildColumns({
    schema,
    visible: dataTable.visible,
    widths: dataTable.widths,
  });

  const onChangeSort = (value) => {
    setSorter(value);
  };

  const onChangeFilter = (key, value) => {
    setFilters((previous) => ({
      ...previous,
      [key]: value,
    }));
  };

  const onClearFilter = (key) => {
    setFilters((previous) => {
      const next = { ...previous };
      delete next[key];
      return next;
    });
  };

  const visibleKeys = useMemo(
    () =>
      Object.keys(schema?.properties || {}).filter(
        (key) => dataTable.visible[key]
      ),
    [schema, dataTable.visible]
  );

  const compiledRegex = useMemo(() => {
    if (!useRegex || !search.trim()) {
      return null;
    }

    try {
      return new RegExp(search.trim(), "i");
    } catch {
      return null;
    }
  }, [search, useRegex]);

  useEffect(() => {
    if (!useRegex || !search.trim() || compiledRegex) {
      setRegexErr(null);
    } else {
      setRegexErr("Invalid regular expression");
    }
  }, [compiledRegex, search, useRegex]);

  const displayData = useMemo(() => {
    let rows = [...participants];

    // Global search across all returned participant fields.
    if (search.trim()) {
      const query = search.trim();

      rows = rows.filter((row) =>
        Object.entries(row).some(([key, value]) => {
          const stringValue = String(value ?? "");
          const field = schema.properties?.[key];

          if (useRegex) {
            return compiledRegex
              ? compiledRegex.test(stringValue)
              : false;
          }

          if (field?.enum) {
            return (
              stringValue.toLowerCase() ===
              query.toLowerCase()
            );
          }

          return stringValue
            .toLowerCase()
            .includes(query.toLowerCase());
        })
      );
    }

    // Header and advanced filters share the same filter map.
    rows = rows.filter((row) =>
      Object.entries(filters).every(([key, value]) => {
        if (!value) {
          return true;
        }

        const field = schema.properties?.[key];
        const stringValue = String(row[key] ?? "");

        if (field?.enum) {
          return stringValue === value;
        }

        return stringValue
          .toLowerCase()
          .includes(String(value).toLowerCase());
      })
    );

    // Sorting.
    if (sorter?.key && sorter.order) {
      const { key, order } = sorter;

      rows.sort((leftRow, rightRow) => {
        const left = String(leftRow[key] ?? "");
        const right = String(rightRow[key] ?? "");

        const comparison = left.localeCompare(
          right,
          undefined,
          {
            numeric: true,
          }
        );

        return order === "ascend"
          ? comparison
          : -comparison;
      });
    }

    return rows;
  }, [
    compiledRegex,
    filters,
    participants,
    schema,
    search,
    sorter,
    useRegex,
  ]);

  const submitCohort = (formValues) => {
    const values = {
      terms: (formValues.submitted_terms || [])
        .map((term) => term?.trim())
        .filter(Boolean),
      include_descendants: formValues.include_descendants,
      present_only: formValues.present_only,
    };

    dispatch(createPhenotypeCohort(values));
  };

  const handleClear = () => {
    form.resetFields();
    setSearch("");
    setRegexErr(null);
    setFilters({});
    dispatch(clearPhenotypeCohort());
  };

  const handleRefresh = () => {
    form.submit();
  };

  const handleReadOnlyAction = () => {
    message.info(
      "Phenotype cohort results are read only on this page."
    );
  };

  const handleDownload = () => {
    const filename = "phenotype_cohort_participants";

    if (!displayData.length || !visibleKeys.length) {
      message.warning("No data to export.");
      return;
    }

    let fileContent = "";
    let fileExtension = "";
    let mimeType = "";

    if (
      exportFormat === "TSV" ||
      exportFormat === "CSV"
    ) {
      const isTSV = exportFormat === "TSV";
      const delimiter = isTSV ? "\t" : ",";

      fileExtension = isTSV ? "tsv" : "csv";

      mimeType = isTSV
        ? "text/tab-separated-values;charset=utf-8"
        : "text/csv;charset=utf-8";

      const escapeValue = (value) => {
        if (Array.isArray(value)) {
          return `"${value
            .map((item) => String(item).trim())
            .join("|")}"`;
        }

        if (typeof value === "string") {
          let trimmedValue = value.trim();

          if (
            trimmedValue.includes(delimiter) ||
            trimmedValue.includes('"') ||
            trimmedValue.includes("\n")
          ) {
            trimmedValue =
              `"${trimmedValue.replace(/"/g, '""')}"`;
          }

          return trimmedValue;
        }

        return value !== undefined && value !== null
          ? value
          : "";
      };

      const getHeaderTitle = (key) =>
        schema?.properties?.[key]?.title || key;

      const headers = visibleKeys
        .map((key) => escapeValue(getHeaderTitle(key)))
        .join(delimiter);

      const fileRows = displayData.map((row) =>
        visibleKeys
          .map((key) => escapeValue(row?.[key]))
          .join(delimiter)
      );

      fileContent = [headers, ...fileRows].join("\n");
    } else if (exportFormat === "JSON") {
      fileExtension = "json";
      mimeType = "application/json;charset=utf-8";
      fileContent = JSON.stringify(displayData, null, 2);
    }

    const blob = new Blob(
      [fileContent],
      { type: mimeType }
    );

    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");

    anchor.href = url;
    anchor.download = `${filename}.${fileExtension}`;

    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);

    URL.revokeObjectURL(url);

    message.success(
      `Current data exported as ${exportFormat}`
    );

    setExportOpen(false);
  };

  return (
    <Layout className="layout-container">
      <Header className="primary-header">
        <Title className="primary-title">
          Phenotype Cohort Builder
        </Title>
      </Header>

      <Spin
        spinning={status === "loading"}
        tip="Building phenotype cohort..."
      >
        <Form
          form={form}
          name="phenotype_cohort"
          layout="vertical"
          onFinish={submitCohort}
          initialValues={{
            submitted_terms: [""],
            include_descendants: true,
            present_only: true,
          }}
        >
          <CohortSummary cohort={phenotypeCohort} />

          {cohortError ? (
            <Alert
              type="error"
              showIcon
              message="Unable to build phenotype cohort"
              description={
                typeof cohortError === "string"
                  ? cohortError
                  : "The cohort request failed."
              }
              style={{ marginTop: 16 }}
            />
          ) : null}

          <Card
            title="Cohort Search"
            style={{ marginTop: 16 }}
          >
            <Row
              gutter={[16, 12]}
              align="top"
            >
              <Col flex="none">
                <Form.Item style={{ marginBottom: 0 }}>
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
              </Col>

              <Col flex="auto">
                <Form.List
                  name="submitted_terms"
                  rules={[
                    {
                      validator: async (_, terms) => {
                        const validTerms = (
                          terms || []
                        ).filter((term) => term?.trim());

                        if (validTerms.length === 0) {
                          throw new Error(
                            "Enter at least one HPO term or HPO identifier."
                          );
                        }
                      },
                    },
                  ]}
                >
                  {(
                    fields,
                    { add, remove },
                    { errors }
                  ) => (
                    <>
                      <Space
                        direction="vertical"
                        style={{ width: "100%" }}
                      >
                        {fields.map(
                          ({
                            key,
                            name,
                            ...restField
                          }) => (
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
                                icon={
                                  <MinusCircleOutlined />
                                }
                                aria-label={
                                  "Remove submitted term"
                                }
                                disabled={
                                  fields.length === 1
                                }
                                onClick={() =>
                                  remove(name)
                                }
                              />
                            </Space>
                          )
                        )}
                      </Space>

                      <Form.ErrorList
                        errors={errors}
                      />

                      <Button
                        type="dashed"
                        icon={<PlusOutlined />}
                        onClick={() => add("")}
                        style={{ marginTop: 8 }}
                      >
                        Add term
                      </Button>
                    </>
                  )}
                </Form.List>
              </Col>
            </Row>

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
          </Card>
        </Form>

        <Card
          title={`Participants (${displayData.length})`}
          style={{ marginTop: 16 }}
          bodyStyle={{ padding: 0 }}
        >
          <TableToolBar
            schema={schema}
            visibleColumns={dataTable.visible}
            onToggleColumn={dataTable.toggleColumn}
            onToggleAll={dataTable.toggleAll}
            onReset={dataTable.reset}
            onOpenModal={handleReadOnlyAction}
            useRegex={useRegex}
            onToggleRegex={setUseRegex}
            search={search}
            onSearch={setSearch}
            regexError={regexErr}
            onOpenAdvanced={() => {
              setDraft(filters);
              setAdvOpen(true);
            }}
            onExportOpen={() =>
              setExportOpen(true)
            }
            recordCount={displayData.length}
            onRefresh={handleRefresh}
            renderDetail={true}
            renderQueue={false}
          />

          <GregorTable
            rowKey={rowKey}
            data={displayData}
            columns={columns}
            onResizeColumn={dataTable.setWidth}
            onRow={() => ({})}
            sorter={sorter}
            filters={filters}
            onChangeSort={onChangeSort}
            onChangeFilter={onChangeFilter}
            onClearFilter={onClearFilter}
          />
        </Card>
      </Spin>

      <Modal
        className="uci-modal"
        title="Advanced Filters"
        open={advOpen}
        onCancel={() => setAdvOpen(false)}
        footer={[
          <Button
            key="clear"
            onClick={() => setDraft({})}
          >
            Clear
          </Button>,

          <Button
            key="apply"
            type="primary"
            onClick={() => {
              setFilters(draft);
              setAdvOpen(false);
            }}
          >
            Apply
          </Button>,
        ]}
      >
        <Form layout="horizontal">
          {visibleKeys.map((key) => {
            const definition =
              schema.properties[key];

            return (
              <Form.Item
                key={key}
                label={
                  `Filter by ${
                    definition?.title || key
                  }`
                }
              >
                {definition?.enum ? (
                  <Select
                    allowClear
                    value={draft[key]}
                    onChange={(value) =>
                      setDraft((previous) => ({
                        ...previous,
                        [key]: value,
                      }))
                    }
                  >
                    {definition.enum.map(
                      (option) => (
                        <Option
                          key={option}
                          value={option}
                        >
                          {option}
                        </Option>
                      )
                    )}
                  </Select>
                ) : (
                  <Input
                    value={draft[key] ?? ""}
                    onChange={(event) =>
                      setDraft((previous) => ({
                        ...previous,
                        [key]:
                          event.target.value,
                      }))
                    }
                  />
                )}
              </Form.Item>
            );
          })}
        </Form>
      </Modal>

      <Modal
        className="uci-modal"
        title="Select Export Format"
        open={exportOpen}
        onCancel={() =>
          setExportOpen(false)
        }
        onOk={handleDownload}
        okText="Download"
        cancelText="Cancel"
      >
        <Select
          value={exportFormat}
          onChange={setExportFormat}
          style={{ width: "100%" }}
        >
          <Option value="TSV">TSV</Option>
          <Option value="CSV">CSV</Option>
          <Option value="JSON">JSON</Option>
        </Select>
      </Modal>
    </Layout>
  );
}