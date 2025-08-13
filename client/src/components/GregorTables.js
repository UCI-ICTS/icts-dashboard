// src/GregorTables.js

import { useState, useMemo, useEffect } from "react";
import { Table, Form, Button, Input, Modal, Tooltip, Spin, Alert, Typography, Dropdown, Select, Checkbox, Switch, Row, Col } from "antd";
import { SearchOutlined, FilterOutlined, PlusOutlined, SettingOutlined } from "@ant-design/icons";
import { useDispatch, useSelector } from "react-redux";
import { getAllTables, fetchTable } from "../slices/dataSlice";
import { getCollectionName } from "../utils/tableNameMap";
import DownloadTSVButton from "./TableDownload";
import TableSelector from "./TableSelector";
import schemas from "../schemas/v1.9schemas.json";
import SchemaForm from "./SchemaForm";
import "../App.css";
import { defaultVisibleColumns } from "../utils/schemaAndTables";

const GregorTables = () => {
  const [form] = Form.useForm();
  const dispatch = useDispatch();
  const isAdmin = useSelector(state => state.account.user.is_superuser)
  const tableView = useSelector(state => state.data['tableView']);
  const tableData = useSelector(state => state.data[tableView]) || [];
  const dataStatus = useSelector(state => state.data.status);
  const rowID = useSelector(state => state.data['tableID']);
  const schema = schemas[tableView] || { properties: {} };
  const [draftFilters, setDraftFilters] = useState({});

  const [filterForm, setFilterForm] = useState({});
  const [filterModalVisible, setFilterModalVisible] = useState(false);
  const [advancedFilters, setAdvancedFilters] = useState({});
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [searchQuery, setSearchQuery] = useState("");
  const [entry, setEntry] = useState(null);
  const [useRegex, setUseRegex] = useState(false);
  const [regexError, setRegexError] = useState(null);
  const [addModalVisible, setAddModalVisible] = useState(false);

  const [visibleColumns, setVisibleColumns] = useState(() => {
    return Object.keys(schema.properties).reduce((acc, key) => {
      acc[key] = true; // All columns are visible by default
      return acc;
    }, {});
  });

  useEffect(() => {
    const tableName = getCollectionName(tableView)

    if ((!tableData || tableData.length === 0)) {
      dispatch(fetchTable(tableName))
    }
    const defaultColumns = defaultVisibleColumns[tableView] || [];
    setVisibleColumns(() => {
      return Object.keys(schema.properties).reduce((acc, key) => {
        acc[key] = defaultColumns.length > 0 ? defaultColumns.includes(key) : true;
        return acc;
      }, {});
    });
    setFilterModalVisible(false);
    setAdvancedFilters({});
    setFilterForm({});
  }, [tableView]);

  // Toggle column visibility
  const toggleColumnVisibility = (key) => {
    setVisibleColumns((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  // Generate table columns dynamically
  const baseColumns = useMemo(() => {
    return Object.entries(schema.properties)
      .filter(([key]) => visibleColumns[key])
      .map(([key, value]) => ({
        title: value.label || key,
        dataIndex: key,
        key,
        width: (key.length * 10),
        sorter: (a, b) => {
          const valA = a[key] !== undefined && a[key] !== null ? String(a[key]) : "";
          const valB = b[key] !== undefined && b[key] !== null ? String(b[key]) : "";
          return valA.localeCompare(valB, undefined, { numeric: true });
        },
        render: (text) => text || "-",
        onHeaderCell: () => ({}),
      }));
  }, [schema, visibleColumns]);

  // add actions to rows
  const columns = useMemo(() => [
    ...baseColumns,
  ], [baseColumns]);

  // Data filtering for search, advanced search, regex search, and download.
  const filteredData = useMemo(() => {
    let data = [...tableData];
    if (searchQuery.trim()) {
      const lowerQuery = searchQuery.trim().toLowerCase();
      data = data.filter((row) =>
        Object.entries(row).some(([key, value]) => {
          const strVal = String(value || "");
          const fieldSchema = schema.properties?.[key];

          if (useRegex) {
            try {
              const regex = new RegExp(lowerQuery, "i");
              setRegexError(null);
              return regex.test(strVal);
            } catch (err) {
              setRegexError("Invalid regular expression");
              return false;
            }
          }

          // 💡 If field is enum, require exact match
          if (fieldSchema?.enum) {
            return strVal.toLowerCase() === lowerQuery;
          }

          // Default partial match
          return strVal.toLowerCase().includes(lowerQuery);
        })
      );
    }

    if (advancedFilters && Object.keys(advancedFilters).length > 0) {
      data = data.filter((row) =>
        Object.entries(advancedFilters).every(([key, value]) => {
          if (!value) return true;

          const rowVal = String(row[key] || "");
          const fieldSchema = schema.properties?.[key];

          if (fieldSchema?.enum) {
            return rowVal === value; // exact match for enum
          }

          return rowVal.toLowerCase().includes(value.toLowerCase()); // partial for free text
        })
      );
    }
    return data;
  }, [tableData, searchQuery, advancedFilters, useRegex]);

  return (
    <>
      <Row gutter={[16, 16]} justify="start" style={{ marginBottom: 16 }}>
        <Col xs={24} sm={12} md={6} lg={6} xl={3}>
          <Tooltip title="Fetch or refresh the table data">
            <Button
              onClick={() => dispatch(getAllTables())}
              type="primary"
            >
              Fetch/Refresh data
            </Button>
          </Tooltip>
        </Col>
        <Col />
        <Col xs={24} sm={12} md={6} lg={6} xl={3}>
          <Tooltip title={`Add a new ${tableView} entry`}>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => {
                setEntry(null);
                form.resetFields();
                setAddModalVisible(true);
              }}
            >
              Add Row
            </Button>
          </Tooltip>
        </Col>
        <Col xs={24} sm={12} md={6} lg={6} xl={3}>
          <Tooltip title="Download results in TSV or CSV">
            <DownloadTSVButton
              rows={filteredData}
              rowID={rowID}
              headCells={columns.map(col => ({
                headerName: typeof col.title === "string" ? col.title : col.title?.props?.children || col.dataIndex,
                field: col.dataIndex
              }))}
            />
          </Tooltip>
        </Col>
        <Col xs={24} sm={12} md={6} lg={4}>
          <Tooltip title="Select GREGoR table">
            <Typography.Text strong>Select Table</Typography.Text>
            <TableSelector />
          </Tooltip>
        </Col>
      </Row>
      <Row gutter={[16, 16]} align="middle" style={{ flexWrap: "wrap" }}>
        <Col xs={24} sm={12} md={6} lg={4}>
          <Switch checked={useRegex} onChange={setUseRegex} /> Enable Regex
        </Col>
        <Col xs={24} sm={12} md={6} lg={4}>
          <Input
            prefix={<SearchOutlined />}
            placeholder="Search all fields"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: "100%",
              maxWidth: 300,
              borderColor: useRegex && regexError ? "red" : undefined,
            }}
            status={useRegex && regexError ? "error" : undefined}
          />
        </Col>
        {useRegex && regexError && (
          <Col xs={24}>
            <Typography.Text type="danger">{regexError}</Typography.Text>
          </Col>
        )}
        <Col xs={24} sm={12} md={6} lg={4}>
          <Typography.Text strong>{filteredData.length} Records</Typography.Text>
        </Col>
        <Col xs={24} sm={12} md={6} lg={4}>
          <Tooltip title="Advanced Filters">
            <Button icon={<FilterOutlined />} onClick={() => setFilterModalVisible(true)}>
            Advanced Filters
            </Button>
          </Tooltip>
        </Col>

<Col xs={24} sm={12} md={6} lg={4}>
  <Dropdown
    trigger={["click"]}
    dropdownRender={() => {
      const allSelected = Object.values(visibleColumns).every(Boolean);
      const someSelected = Object.values(visibleColumns).some(Boolean);

      return (
        <div className="column-toggle-menu">
          <div className="column-toggle-item">
            <Button
              size="small"
              onClick={() => {
                const allSelected = Object.keys(schema.properties).every((key) => visibleColumns[key]);
                const newState = !allSelected;
                const updated = {};
                Object.keys(schema.properties).forEach((key) => {
                  updated[key] = newState;
                });
                setVisibleColumns(updated);
              }}
            >
              {Object.keys(schema.properties).every((key) => visibleColumns[key])
                ? "Deselect All"
                : "Select All"}
            </Button>
          </div>
          {Object.keys(schema.properties).map((key) => (
            <div key={key}>
              <Checkbox
                checked={visibleColumns[key]}
                onChange={() => toggleColumnVisibility(key)}
                className="column-toggle-item"
              >
                {schema.properties[key]?.label || key}
              </Checkbox>
            </div>
          ))}
        </div>
      );
    }}
  >
    <Button icon={<SettingOutlined />}>Columns</Button>
  </Dropdown>
</Col>

      </Row>

      {dataStatus === "loading" ? (
        <Spin tip="Loading data..." style={{ display: "block", textAlign: "center", marginTop: "20px" }}>
          <div style={{ minHeight: "100px" }} />
        </Spin>
      ) : dataStatus === "error" ? (
        <Alert message="Error loading data" type="error" showIcon />
      ) : (
        <Table
          className="table"
          columns={columns}
          onRow={(record) => ({
            onClick: () => {
              setEntry({...record});
              setAddModalVisible(true);
            },
          })}
          dataSource={filteredData}
          scroll={{ x: 1500, y: "calc(100vh - 250px)" }} // <-- Ensures layout even with no rows
          locale={{ emptyText: "No records match your filters or search." }}
          rowKey={(row) => row[rowID] || row.participant_id || row.genetic_findings_id}
          pagination={{
            current: page,
            pageSize,
            onChange: (page, pageSize) => {
              setPage(page);
              setPageSize(pageSize === "All" ? tableData.length : pageSize); // Handle "All" option
            },
            showSizeChanger: true,
            pageSizeOptions: ["10", "25", "50", "100", "All"],
          }}
        />
      )}
      <Modal
        className="uci-modal"
        title={entry ? (
          `Edit ${tableView}`
        ) : (
          `Add New ${tableView}`
        )}
        open={addModalVisible}
        onCancel={() => {
          form.resetFields();
          setAddModalVisible(false);
        }}
        footer={null}
        width={800}
      >
        <SchemaForm
          isAdmin={isAdmin}
          form={form}
          schema={schemas[tableView]}
          open={addModalVisible}
          initialValues={entry || {}}
          setAddModalVisible={setAddModalVisible}
          setEntry={setEntry}
        />
      </Modal>

      <Modal
        className="uci-modal"
        title="Advanced Filters"
        open={filterModalVisible}
        onCancel={() => setFilterModalVisible(false)}
        footer={[
          <Button key="clear" onClick={() => {
            setDraftFilters({});
            setAdvancedFilters({});
          }}>
            Clear
          </Button>,
          <Button key="apply" type="primary" onClick={() => {
            setAdvancedFilters(draftFilters);
            setFilterModalVisible(false);
          }}>
            Apply
          </Button>
        ]}
      >        
        <Form layout="horizontal">
          {columns.map((col) => {
            const fieldSchema = schema.properties[col.dataIndex];
            const fieldKey = col.dataIndex;

            return (
              <Form.Item label={`Filter by ${col.title}`} key={col.key}>
                {fieldSchema?.enum ? (
                  <Select
                    allowClear
                    value={draftFilters[fieldKey]}
                    onChange={(value) =>
                      setDraftFilters((prev) => ({
                        ...prev,
                        [fieldKey]: value,
                      }))
                    }
                  >
                    {fieldSchema.enum.map((option) => (
                      <Select.Option key={option} value={option}>
                        {option}
                      </Select.Option>
                    ))}
                  </Select>
                ) : (
                  <Input
                    value={draftFilters[fieldKey] || ""}
                    onChange={(e) =>
                      setDraftFilters((prev) => ({
                        ...prev,
                        [fieldKey]: e.target.value,
                      }))
                    }
                  />
                )}
              </Form.Item>
            );
          })}
        </Form>
      </Modal>
    </>
  );
};

export default GregorTables;
