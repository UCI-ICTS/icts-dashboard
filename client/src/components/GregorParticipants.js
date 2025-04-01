// src/components/GregorParticipants.js

import React, { useState, useMemo, useEffect, useCallback } from "react";
import { Descriptions, Table, Form, Button, Input, Modal, Tooltip, Spin, Alert, Typography, Dropdown, Checkbox, Switch, Row, Col } from "antd";
import { SearchOutlined, FilterOutlined, PlusOutlined, SettingOutlined } from "@ant-design/icons";
import { useDispatch, useSelector } from "react-redux";
import { Resizable } from 'react-resizable';
import { getAllTables, updateTable, addTable } from "../slices/dataSlice";
import DownloadTSVButton from "./TableDownload";
import ErrorBoundary from "./ErrorBoundary";
import schemas from "../schemas/v1.7schemas.json";
import SchemaForm from "./SchemaForm";
import "../App.css";

const GregorParticipants = () => {
  const dispatch = useDispatch();
  const tableView = "participants"; 
  const tableData = useSelector(state => state.data[tableView]) || [];
  const dataStatus = useSelector(state => state.data.status);
  const rowID = useSelector(state => state.data['tableID']);
  const schema = schemas[tableView] || { properties: {} };
  const [filterModalVisible, setFilterModalVisible] = useState(false);
  const [advancedFilters, setAdvancedFilters] = useState({});
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [searchQuery, setSearchQuery] = useState("");
  const [form] = Form.useForm();
  const [editRecord, setEditRecord] = useState(null);
  const [useRegex, setUseRegex] = useState(false);
  const [regexError, setRegexError] = useState(null);
  const [addModalVisible, setAddModalVisible] = useState(false);
  const [selectedRow, setSelectedRow] = useState(null);
  const [visibleColumns, setVisibleColumns] = useState(() => {
    return Object.keys(schema.properties).reduce((acc, key) => {
      acc[key] = true; // All columns are visible by default
      return acc;
    }, {});
  });

  useEffect(() => {
    setVisibleColumns(() => {
      return Object.keys(schema.properties).reduce((acc, key) => {
        acc[key] = true;
        return acc;
      }, {});
    });
    setFilterModalVisible(false);
    setAdvancedFilters({});
  }, [tableView]);  

  // Toggle column visibility
  const toggleColumnVisibility = (key) => {
    setVisibleColumns((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };
  
  // Generate table columns dynamically
    const columns = useMemo(() => {
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

    // Data filtering for search, advanced search, regex search, and download. 
    const filteredData = useMemo(() => {
      let data = [...tableData];
    
      if (searchQuery.trim()) {
        data = data.filter((row) => {
          return Object.values(row).some((value) => {
            const strVal = String(value || "");
            if (useRegex) {
              try {
                const regex = new RegExp(searchQuery.trim(), "i"); // ← safe and case-insensitive
                setRegexError(null); // Clear previous errors
                return regex.test(strVal);
              } catch (err) {
                setRegexError("Invalid regular expression");
                return false; // Invalid regex
              }
            }
            setRegexError(null);
            return strVal.toLowerCase().includes(searchQuery.toLowerCase());
          });
        });
      }
      if (advancedFilters && Object.keys(advancedFilters).length > 0) {
        data = data.filter((row) =>
          Object.entries(advancedFilters).every(([key, value]) =>
            value ? String(row[key] || "").toLowerCase().includes(value.toLowerCase()) : true
          )
        );
      }
      return data;
    }, [tableData, searchQuery, advancedFilters, useRegex]);     

  // Dropdown menu for toggling column visibility
  const columnToggleMenuItems = Object.keys(schema.properties).map((key) => ({
    key,
    label: (
      <Checkbox
        checked={visibleColumns[key]}
        onChange={() => toggleColumnVisibility(key)}
      >
        {schema.properties[key]?.label || key}
      </Checkbox>
    ),
  }));
  
  const familyMembers = useMemo(() => {
    if (!selectedRow?.family_id) return [];
  
    return tableData.filter(
      member =>
        member.family_id === selectedRow.family_id &&
        member.participant_id !== selectedRow.participant_id
    );
  }, [selectedRow, tableData]);
  
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
      <Col xs={24} sm={12} md={6} lg={6} xl={3}>
      </Col>
      <Col xs={24} sm={12} md={6} lg={6} xl={3}>
      </Col>
      <Col xs={24} sm={12} md={6} lg={6} xl={3}>
        <Tooltip title="Download">
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
      </Col>
      <Col xs={24} sm={12} md={6} lg={4}>
        <Dropdown menu={{ items: columnToggleMenuItems }} trigger={["click"]}>
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
          columns={columns}
          dataSource={filteredData}
          onRow={(record) => ({
            onClick: () => setSelectedRow(record),
          })}
          // scroll={{ x: 1500, y: "calc(100vh - 250px)" }} // <-- Ensures layout even with no rows
          scroll={{ x: "max-content", y: "50vh" }}
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
      {selectedRow && (
        <div style={{ marginTop: 24 }}>
          <Typography.Title level={4}>
            Family Group for: {selectedRow[rowID] || selectedRow.participant_id}
          </Typography.Title>
          <Descriptions bordered size="small" column={1}>
            {Object.entries(schema.properties).map(([key, value]) => (
              <Descriptions.Item label={value.label || key} key={key}>
                {Array.isArray(selectedRow[key])
                  ? selectedRow[key].join(", ")
                  : selectedRow[key] || "-"}
              </Descriptions.Item>
            ))}
          </Descriptions>
          <br/>
          <Table
            dataSource={[
              selectedRow,
              ...familyMembers, // this will not duplicate if you filter correctly
            ]}
            rowKey="participant_id"
            size="small"
            columns={[
              { title: "Participant ID", dataIndex: "participant_id", key: "participant_id" },
              { title: "Relation", dataIndex: "proband_relationship", key: "proband_relationship" },
              { title: "Age at last observation", dataIndex: "age_at_last_observation", key: "age_at_last_observation" },
              // add more if needed
            ]}
            pagination={false}
            rowClassName={(record) =>
              record.participant_id === selectedRow.participant_id ? "selected-row-highlight" : ""
            }
          />

          <Button
            onClick={() => setSelectedRow(null)}
            type="link"
            style={{ marginTop: 8 }}
          >
            Clear Details
          </Button>
        </div>
      )}


      <Modal
        title="Advanced Filters"
        open={filterModalVisible}
        onCancel={() => setFilterModalVisible(false)}
        footer={[
          <Button key="clear" onClick={() => setAdvancedFilters({})}>
            Clear
          </Button>,
          <Button key="apply" type="primary" onClick={() => setFilterModalVisible(false)}>
            Apply
          </Button>,
        ]}
      >
        <Form layout="vertical">
          {columns.map((col) => (
            <Form.Item label={`Filter by ${col.title}`} key={col.key}>
              <Input
                value={advancedFilters[col.dataIndex] || ""}
                onChange={(e) =>
                  setAdvancedFilters((prev) => ({
                    ...prev,
                    [col.dataIndex]: e.target.value,
                  }))
                }
              />
            </Form.Item>
          ))}
        </Form>
      </Modal>
    </>
  );
};

export default GregorParticipants;
