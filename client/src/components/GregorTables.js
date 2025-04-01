// src/GregorTables.js

import React, { useState, useMemo, useEffect, useCallback } from "react";
import { Table, Form, Button, Input, Space, Modal, Tooltip, Spin, Alert, Typography, Dropdown, Checkbox, Row } from "antd";
import { SearchOutlined, FilterOutlined, PlusOutlined, SettingOutlined } from "@ant-design/icons";
import { useDispatch, useSelector } from "react-redux";
import { Resizable } from 'react-resizable';
import { getAllTables, updateTable, addTable } from "../slices/dataSlice";
import DownloadTSVButton from "./TableDownload";
import ErrorBoundary from "./ErrorBoundary";
import TableSelector from "./TableSelector";
import schemas from "../schemas/v1.7schemas.json";
import { setTableView } from "../slices/dataSlice";
import SchemaForm from "./SchemaForm";
import "../App.css";

const GregorTables = () => {
  const dispatch = useDispatch();
  const tableView = useSelector(state => state.data['tableView']);
  const tableData = useSelector(state => state.data[tableView]) || [];
  const dataStatus = useSelector(state => state.data.status);
  const rowID = useSelector(state => state.data['tableID']);
  const schema = schemas[tableView] || { properties: {} };
  
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [searchQuery, setSearchQuery] = useState("");
  const [form] = Form.useForm();
  const [editRecord, setEditRecord] = useState(null);
  const [addModalVisible, setAddModalVisible] = useState(false);
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
      {
        title: "Actions",
        key: "actions",
        render: (text, record) => (
          <Button
            type="link"
            onClick={() => {
              setEditRecord(record);
              setAddModalVisible(true);
            }}
          >
            Edit
          </Button>
        ),
      },
    ], [baseColumns]);

    // Data filtering for search and download. 
    const filteredData = useMemo(() => {
      if (!searchQuery.trim()) return tableData;
    
      const lowerQuery = searchQuery.toLowerCase();
    
      return tableData.filter(row =>
        Object.values(row).some(
          value => value && String(value).toLowerCase().includes(lowerQuery)
        )
      );
    }, [tableData, searchQuery]);
    

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
  
  
  return (
    <>
    <Space justify="space-between" align="middle" style={{ marginBottom: 16 }}>
      <Tooltip title="Fetch or refresh the table data">
        <Button
          onClick={() => dispatch(getAllTables())}
          type="primary"
          style={{ marginBottom: 16 }}
        >
          Fetch/Refresh data
        </Button>
      </Tooltip>
      <Tooltip title={`Add a new ${tableView} entry`}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setEditRecord(null);               // Clear any old record
            form.resetFields();               // Reset the form manually
            setAddModalVisible(true);         // Then open the modal
          }}        
        >
          Add Row
        </Button>
      </Tooltip>
      <Tooltip title={`downlaod`}>
      <DownloadTSVButton
        rows={filteredData}
        rowID={rowID}
        headCells={columns.map(col => ({
          headerName: typeof col.title === "string" ? col.title : col.title?.props?.children || col.dataIndex,
          field: col.dataIndex
        }))}
      />
      </Tooltip>
      </Space>
      <Space className="table-header">
        <Input
          prefix={<SearchOutlined />}
          placeholder="Search all fields"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{ width: "300px" }}
        />
        <Typography.Text strong>{filteredData.length} Records</Typography.Text>

        <Tooltip title="Advanced Filters">
          <Button icon={<FilterOutlined />}>Filters</Button>
        </Tooltip>
        <TableSelector />

        <Dropdown menu={{ items: columnToggleMenuItems }} trigger={["click"]}>
          <Button icon={<SettingOutlined />}>Columns</Button>
        </Dropdown>
      </Space>

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
          scroll={{ x: "max-content", y: "calc(100vh - 250px)" }}
        />
      )}
      <Modal
        title={editRecord ? `Edit ${tableView}` : `Add New ${tableView}`}
        open={addModalVisible}
        onCancel={() => {
          form.resetFields();
          setAddModalVisible(false);
        }}      
        footer={null}
        width={800}
      >
        <SchemaForm
          form={form}
          schema={schemas[tableView]}
          initialValues={editRecord || {}}
          onSubmit={(values) => {
            console.log(schemas[tableView]);
          
            if (editRecord) {
              // Update existing record
              dispatch(updateTable({ table: tableView, data: values }));
              console.log("Editing row:", tableView, values);
            } else {
              // Add new record
              dispatch(addTable({ table: tableView, data: values }));
              console.log("Creating new row:", tableView, values);
            }
          
            setAddModalVisible(false);
            setEditRecord(null);
          }}
          onCancel={() => {
            form.resetFields();
            setAddModalVisible(false);
            setEditRecord(null);
          }}
        />
      </Modal>
    </>
  );
};

export default GregorTables;
