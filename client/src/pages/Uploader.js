// src/pages/Uploader.js

import Papa from "papaparse";
import React, { useEffect, useRef, useState, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Alert, Table, Input, Form, Spin, Layout, Row, Col, Button } from "antd";
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import { setJsonData, clearJsonData, fetchTable, createEntry } from '../slices/dataSlice';
import TableSelector from '../components/TableSelector';
import schemas from '../schemas/v1.9schemas.json';
import { getValidationRules } from "../utils/schemaAndTables";
import { getCollectionName } from "../utils/tableNameMap";

export const Uploader = () => {
  const fileInputRef = useRef(null);
  const dispatch = useDispatch();
  const jsonData = useSelector(state => state.data['jsonData']);
  const { tableView, tableID } = useSelector(state => state.data);
  const tableName = getCollectionName(tableView)
  const tableData = useSelector(state => state.data[tableView])
  const initialRows = jsonData?.slice(1) || [];
  const schema = schemas[tableView] || { properties: {} };
  const defaultHeaders = Object.keys(schema.properties || {});
  const [form] = Form.useForm();
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleCsvUpload = (sheet, fileInfo) => {
    const expectedHeaders = Object.keys(schema.properties || {});
    const actualHeaders = Object.keys(sheet[0] || {});
    const headersValid = actualHeaders.every(h => expectedHeaders.includes(h));
    if (!headersValid) {
      alert("CSV headers do not match the expected schema. Please check your file.");
      handleClear();
      setIsLoading(false);
      return;
    }
    dispatch(setJsonData(sheet));
  };

  const handleClear = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    dispatch(clearJsonData());
    setError(null);
    setIsLoading(false);
  }

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
      form.setFieldsValue({ rows: jsonData.slice(1) });

      const timeout = setTimeout(() => {
        form.validateFields()
          .then(() => {
            setError(null);
            setIsLoading(false); // ✅ Already here
          })
          .catch((err) => {
            console.warn("Initial validation errors:", err);
            setError(`Initial validation errors: ${err.errorFields.length}`);
            setIsLoading(false); // ✅ Add this line
          });
      }, 0);

      return () => clearTimeout(timeout);
    }
  }, [jsonData, form]);

  return (
    <Layout className="layout-container">
      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <TableSelector />
        </Col>
        <Col xs={24} md={8}>
          <input
            ref={fileInputRef}
            type="file"
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
          <Button onClick={handleClear}>Clear Data</Button>
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
