// src/pages/Uploader.js

import Papa from "papaparse";
import React, { useEffect, useRef, useState, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Alert, Table, Input, Select, Form, Spin, Typography, Layout, Row, Col, Button, Tooltip } from "antd";
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import { setJsonData, clearJsonData, fetchTable, createEntry, setTableView } from '../slices/dataSlice';
import schemas from '../schemas/v1.12schemas.json';
import { getValidationRules, getCollectionName, TABLE_MAPPING } from "../utils/schemaAndTables";

const { Option } = Select;
const { Header } = Layout;
const { Title } = Typography;

export const Uploader = () => {
  const fileInputRef = useRef(null);
  const dispatch = useDispatch();
  const jsonData = useSelector(state => state.data['jsonData']);
  const { tableView, tableID } = useSelector(state => state.data);
  const tableName = getCollectionName(tableView)
  const tableData = useSelector(state => state.data[tableView])
  const initialRows = jsonData || [];
  const schema = schemas[tableView] || { properties: {} };
  const defaultHeaders = Object.keys(schema.properties || {});
  const [form] = Form.useForm();
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (value) => {
    const selectedTable = TABLE_MAPPING.find((table) => table.schema === value);
    if (selectedTable) {
      dispatch(setTableView(selectedTable));
    }
  };

  // Type coercion of cells based on schema
  const coerceValue = (rawValue, schemapProp) => {
    // Empty string as null
    if (rawValue == "" || rawValue == undefined) return null;

    // If PapaParse already geave number/boolean, keep it
    const val = rawValue;
    if (!schemapProp) return val;

  // Arrays: assuming CSV stores as "a|b|c"
    if (schemapProp.type === "array") {
      if (Array.isArray(val)) return val;
      return String(val)
        .split("|")
        .map(str => str.trim())
        .filter(Boolean);
    }

    if (schemapProp.type === "integer") {
      const num = Number(val);
      return Number.isFinite(num) ? parseInt(num, 10) : null;
    }

    if (schemapProp.type === "number") {
      const num = Number(val);
      return Number.isFinite(num) ? num : null;
    }

    if (schemapProp.type === "boolean") {
      if (typeof val === "boolean") return val;
      const str = String(val).toLowerCase().trim();
      if (["true", "t", "yes", "y", "1"].includes(str)) return true;
      if (["false", "f", "no", "n", "0"].includes(str)) return false;
      return null;
    }

    // default: string
    return String(val);
  };

  const coerceRowToSchema = (row, schema) => {
    const schemapProps = schema?.properties || {}
    const coercedRow = {}
    for (const key of Object.keys(schemapProps)) {
      coercedRow[key] = coerceValue(row[key], schemapProps[key]);
    }
    return coercedRow;
  };

  const handleCsvUpload = (sheet, fileInfo) => {
    const expectedHeaders = Object.keys(schema.properties || {});
    const actualHeaders = Object.keys(sheet[0] || {});
    const headersValid = actualHeaders.every(h => expectedHeaders.includes(h));

    // Block if CSV Headers do not match Schema
    if (!headersValid) {
      alert("CSV headers do not match the expected schema. Please check your file.");
      handleClear();
      setIsLoading(false);
      return;
    }

    // Coerce sheet before dispatch and add key for AntD
    const coercedSheet = sheet.map((row, index) => {
      const coerced = coerceRowToSchema(row, schema)
      return {
        // Edge case: phenotype_id. fallback to index if missing
        key: coerced?.[tableID] ?? coerced?.phenotype_id ?? index,
        ...coerced,
      };
    });

    dispatch(setJsonData(coercedSheet));
  };

  // Clear Form
  const handleClear = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    dispatch(clearJsonData());
    setError(null);
    setIsLoading(false);
  }

  // Submit to DB
  const handleSubmit = (values) => {
    const { rows } = values
    dispatch(createEntry({ table: tableName, data: rows }));
  };

  // Precompute rules
  const validationRulesMap = useMemo(() => {
    const rules = {};
    const existingPKs = new Set((tableData || []).map(item => item?.[tableID]));

    for (const key of Object.keys(schema.properties || {})) {
      const baseRules = getValidationRules(key, schema.properties[key], schema.required);

      const pkRules = [];

      if (key === tableID) {
        pkRules.push({
          validator: async (_, value) => {
            if (value && existingPKs.has(value)) {
              return Promise.reject(`${key} value "${value}" already exists`);
            }
            return Promise.resolve();
          }
        });
      }

      rules[key] = [...baseRules, ...pkRules];
    }
    return rules;
  }, [schema, tableData, tableID]);


  // Update validation count on change
  const updateErrorState = () => {
    const currentErrors = form.getFieldsError();
    const hasErrors = currentErrors.some(f => f.errors.length > 0);

    if (hasErrors) {
      const errorCount = currentErrors.reduce(
        (count, field) => count + field.errors.length,
        0
      );
      setError(`Validation errors: ${errorCount}`);
    } else {
      setError(null);
    }
  };

  useEffect(() => {
    const tableName = getCollectionName(tableView);
    dispatch(fetchTable(tableName));

    handleClear();

    // Wait until after clear
    setTimeout(() => {
      if (form) {
        form.resetFields();
      }
    }, 0);
  }, [tableView]);

  useEffect(() => {
    if (jsonData) {
      form.setFieldsValue({ rows: jsonData });

      const timeout = setTimeout(() => {
        form.validateFields()
          .then(() => {
            setError(null);
            setIsLoading(false);
          })
          .catch((err) => {
            console.warn("Initial validation errors:", err);
            setError(`Initial validation errors: ${err.errorFields.length}`);
            setIsLoading(false);
          });
      }, 0);

      return () => clearTimeout(timeout);
    }
  }, [jsonData, form]);

  return (
    <Layout className="layout-container">
      <Header className="primary-header">
        <Title className="primary-title">Data Sheet Uploader: GREGoR</Title>
      </Header>
      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <Tooltip title="Select table" className="table-selector-container">
            Select Table:&nbsp;
            <Select
              className="table-selector"
              value={tableView}
              onChange={handleChange}
              placeholder="Select Table"
              style={{ minWidth: 200 }}
            >
              {TABLE_MAPPING.map((table) => (
                <Option key={table.schema} value={table.schema}>
                  {table.name}
                </Option>
              ))}
            </Select>
          </Tooltip>
        </Col>
        <Col xs={24} md={8}>

          <input
            ref={fileInputRef}
            type="file"
            className=""
            accept=".csv"
            onChange={(e) => {
              setIsLoading(true);
              const file = e.target.files?.[0];
              if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                  const text = event.target.result;
                  Papa.parse(text, {
                    header: true,
                    skipEmptyLines: true,
                    complete: (results) => {
                      handleCsvUpload(results.data, file);
                    },
                  });
                };
                reader.readAsText(file);
              } else {
                setIsLoading(false);
              }
            }}
          />
        </Col>
        <Col xs={24} md={8}>
          <Button
            className="header-button"
            onClick={handleClear}
          >Clear Data</Button>
        </Col>
      </Row>
      <Spin spinning={isLoading}>
        <Row>
          {
            (jsonData !== null) ? (
              <Form form={form} onFinish={handleSubmit} onFieldsChange={updateErrorState} initialValues={{ rows: initialRows }} layout="vertical">
                <Form.List name="rows">
                  {(fields, { add, remove }) => (
                    <>
                      <Table
                        dataSource={fields}
                        pagination={false}
                        rowKey={(field) => field.key}
                        columns={[
                            {
                              title: "Actions",
                              key: "actions",
                              fixed: "left",
                              render: (_, __, index) => (
                                <Button
                                  danger
                                  onClick={() => {
                                    remove(index);
                                    setTimeout(() => {
                                      form.validateFields();
                                      updateErrorState();
                                    }, 0);
                                  }}
                                  icon={<MinusCircleOutlined />}
                                />
                              ),
                            },
                          ...defaultHeaders.map((key) => ({
                            title: key,
                            dataIndex: key,
                            key,
                            render: (_, __, index) => (
                              <Form.Item
                                name={[index, key]}
                                style={{ margin: 0 }}
                                rules={validationRulesMap[key]}
                              >
                                <Input />
                              </Form.Item>
                            )
                          }))
                        ]}
                      />
                    </>
                  )}
                </Form.List>
                <Button
                 type="primary"
                 disabled={error}
                 htmlType="submit"
                 style={{ marginTop: 24 }}
                >Submit</Button>
                {error && <Alert type="error" message={error} />}
              </Form>
            ) : (
              <div>No data loaded</div>
            )
          }
        </Row>
      </Spin>
    </Layout>
  );
};
