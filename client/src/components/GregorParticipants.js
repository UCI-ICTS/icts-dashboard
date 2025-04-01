import React, { useState, useEffect, useMemo } from 'react';
import { Table, Button, Input, Space, Modal, Tooltip, Spin, Alert, Typography, Dropdown, Checkbox } from "antd";
import { SearchOutlined, FilterOutlined, PlusOutlined, SettingOutlined } from "@ant-design/icons";
import { useSelector, useDispatch } from 'react-redux';
import { getAllTables } from "../slices/dataSlice";
import AddPatient from './AddPatient';
import schemas from "../schemas/v1.7schemas.json";

const GregorParticipants = () => {
  const dispatch = useDispatch();
  const participants = useSelector(state => state.data.participants)
  
  const schema = schemas["participants"] || { properties: {} };
  const [loading, setLoading] = useState(false);
  const [addModalVisible, setAddModalVisible] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [visibleColumns, setVisibleColumns] = useState(() => {
      return Object.keys(schema.properties).reduce((acc, key) => {
        acc[key] = true; // All columns are visible by default
        return acc;
      }, {});
    });
  // Dropdown menu for toggling column visibility
  const columnToggleMenu = (
    <div className="column-toggle-menu" size="middle">
      {Object.keys(schema.properties).map((key) => (
        <Checkbox 
          key={key}
          checked={visibleColumns[key]} 
          onChange={() => toggleColumnVisibility(key)}
          className="column-toggle-item"
        >
          {schema.properties[key]?.label || key}
        </Checkbox>
      ))}
    </div>
  );

  // Generate table columns dynamically
  const columns = useMemo(() => {
    return Object.entries(schema.properties)
      .filter(([key]) => visibleColumns[key]) // Only include visible columns
      .map(([key, value]) => ({
        title: value.label || key,
        dataIndex: key,
        key,
        width:  (key.length * 10),
        sorter: (a, b) => {
          const valA = a[key] !== undefined && a[key] !== null ? String(a[key]) : "";
          const valB = b[key] !== undefined && b[key] !== null ? String(b[key]) : "";
          return valA.localeCompare(valB, undefined, { numeric: true });
        },
        
        render: (text) => text || "-",
        onHeaderCell: () => ({}),
      }));
  }, [schema, visibleColumns]);

  // Toggle column visibility
  const toggleColumnVisibility = (key) => {
    setVisibleColumns((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };
  console.log("things", schema)
  return (
    <>
      <Button
        onClick={() => dispatch(getAllTables())}
        type="primary"
        style={{ marginBottom: 16 }}
      >
        Fetch/Refresh data
      </Button>
      
      <Space className="table-header">
        <Input
          prefix={<SearchOutlined />}
          placeholder="Search all fields"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{ width: "300px" }}
        />
        <Typography.Text strong>{participants.length} Records</Typography.Text>

        <Tooltip title="Advanced Filters">
          <Button icon={<FilterOutlined />}>Filters</Button>
        </Tooltip>

        <Button type="primary" icon={<PlusOutlined />}>Add Row</Button>

        <Dropdown overlay={columnToggleMenu} trigger={["click"]}>
          <Button icon={<SettingOutlined />}>Columns</Button>
        </Dropdown>
      </Space>
      <Table
        columns={columns}
        dataSource={participants}
        loading={loading}
        rowKey="participant_id"
      />
      <Modal
        title="Add New Patient"
        open={addModalVisible}
        onCancel={() => setAddModalVisible(false)}
        footer={null}
      >
        <AddPatient onSubmit={console.log("click")} />
      </Modal>
    </>
  );
};

export default GregorParticipants;