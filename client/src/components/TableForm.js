// src/components/TableForm.js
import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Form, Input, Button, Table, Space, Alert } from 'antd';
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
// import { submitParticipant } from '../slices/dataSlice'; // adjust import as needed

const participant_head = [
  'participant_id', 'internal_project_id', 'gregor_center', 'consent_code', 'recontactable',
  'pmid_id', 'family_id', 'paternal_id', 'maternal_id', 'twin_id', 'proband_relationship',
  'proband_relationship_detail', 'sex', 'sex_detail', 'reported_race', 'reported_ethnicity',
  'ancestry_detail', 'age_at_last_observation', 'affected_status', 'phenotype_description',
  'age_at_enrollment', 'prior_testing', 'case_level_result', 'updated_at', 'phenotype_id',
  'solve_status', 'missing_variant_case', 'missing_variant_details'
];

const convertToJSON = (data) => {
  const actualHeaders = Object.keys(data[0] || {});
  const participant_valid = participant_head.every(header => actualHeaders.includes(header));
  return [data, participant_valid];
};

export const TableForm = () => {
  const dispatch = useDispatch();
  const tableData = useSelector(state => state.data['jsonData']);
  const [form] = Form.useForm();
  const [error, setError] = useState(null);

  const handleSubmit = (values) => {
    const [data_list, isValid] = convertToJSON(values.rows);
    if (isValid) {
      // dispatch(submitParticipant({ data_list }));
      console.log(data_list);
    } else {
      setError("Uploaded data does not match expected participant headers.");
    }
  };

  if (!tableData || tableData.length === 0) {
    return <div>Loading...</div>;
  }

  const defaultHeaders = tableData[0];
  const initialRows = tableData.slice(1);

  return (
    <Form form={form} onFinish={handleSubmit} initialValues={{ rows: initialRows }} layout="vertical">
      {error && <Alert type="error" message={error} />}
      <Form.List name="rows">
        {(fields, { add, remove }) => (
          <>
            <Table
              dataSource={fields}
              pagination={false}
              rowKey={(field) => field.key}
              columns={[
                ...Object.entries(defaultHeaders).map(([key, label]) => ({
                  title: label,
                  dataIndex: key,
                  key,
                  render: (_, __, index) => (
                    <Form.Item name={[index, key]} style={{ margin: 0 }}>
                      <Input />
                    </Form.Item>
                  )
                })),
                {
                  title: 'Actions',
                  key: 'actions',
                  render: (_, __, index) => (
                    <Button
                      icon={<MinusCircleOutlined />}
                      onClick={() => remove(index)}
                      danger
                    />
                  )
                }
              ]}
            />
            <Button
              type="dashed"
              onClick={() => add({})}
              icon={<PlusOutlined />}
              style={{ marginTop: 16 }}
            >
              Add Row
            </Button>
          </>
        )}
      </Form.List>
      <Button type="primary" htmlType="submit" style={{ marginTop: 24 }}>
        Submit
      </Button>
    </Form>
  );
};
