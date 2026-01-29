// src/components/Modals.js

import { useState, useEffect } from "react";
import { Button, Form, Input, Modal, Select, Space, Typography } from "antd";
import { MinusCircleOutlined, PlusOutlined } from "@ant-design/icons";
import { onsetAgeRange } from "../utils/schemaAndTables";

const { Option } = Select;
const { Text } = Typography;

{/* Modal for HPO Download */}
export const HPODownloadModal = ({ visible, onCancel, handleSubmit }) => {
  const [form] = Form.useForm();

  const handleOk = () => {
    form.submit(); // triggers onFinish
  };

  const handleFinish = (values) => {
    handleSubmit(values); // all values: { action, exportFormat, participant }
    form.resetFields();
    onCancel();
  };

  const handleCancel = () => {
    form.resetFields();
    onCancel();
  };

  const currentAction = Form.useWatch("action", form);

  return (
    <Modal
      className="uci-modal"
      title="HPO Actions"
      open={visible}
      onCancel={handleCancel}
      onOk={handleOk}
      okButtonProps={{ disabled: !currentAction }}
      destroyOnClose
    >
      <Form form={form} onFinish={handleFinish} layout="vertical">
        <Form.Item
          name="action"
          label="Action"
          rules={[{ required: true, message: "Select an action" }]}
        >
          <Select placeholder="Select an action">
            <Option value="download">Download Results</Option>
            <Option value="import">Import Results</Option>
          </Select>
        </Form.Item>

        {currentAction === "import" && (
          <Form.Item
            name="participant"
            label="Participant ID"
            rules={[{ required: true, message: "Enter a participant ID" }]}
          >
            <Input placeholder="Participant ID" />
          </Form.Item>
        )}

        {currentAction === "download" && (
          <Form.Item
            name="exportFormat"
            label="Download Format"
            rules={[{ required: true, message: "Select a format" }]}
            initialValue="TSV"
          >
            <Select>
              <Option value="TSV">TSV: table only</Option>
              <Option value="CSV">CSV: table only</Option>
              <Option value="JSON">JSON: full results</Option>
            </Select>
          </Form.Item>
        )}
      </Form>
    </Modal>
  );
};

{/* Modal for HPO Import */}
export const PhenotypeImportFormModal = ({ visible, onCancel, onSubmit, flattenedData = [], participantId }) => {
  const [form] = Form.useForm();
  const defaultPresence = "Present";
  const defaultOntology = "HPO";

  useEffect(() => {
    if (visible && flattenedData.length > 0 && participantId) {
      const fields = flattenedData.map((row, idx) => ({
        phenotype_id: `${participantId}_${row.hpo_id}`,
        term_id: row.hpo_id,
        presence: defaultPresence,
        ontology: defaultOntology,
        additional_details: [
          `Source: ${row.source}`,
          `Extracted: ${row.phrase}`,
          `Label: ${row.label}`,
          `Reason: ${row.reason}`
        ].filter(Boolean).join("; "),
        onset_age_range: undefined,
        additional_modifiers: undefined,
        syndromic: undefined,
        participant_id: participantId,
      }));

      form.setFieldsValue({ phenotypes: fields });
    }
  }, [visible, flattenedData, participantId, form]);

  const handleOk = () => {
    form.submit();
  };

  const handleFinish = (values) => {
    const entries = values.phenotypes || [];
    onSubmit(entries);
    form.resetFields();
  };

  return (
    <Modal
      className="uci-modal"
      title="Review and Submit Phenotypes"
      open={visible}
      onCancel={onCancel}
      onOk={handleOk}
      okText="Submit"
      width={900}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleFinish}
        initialValues={{ phenotypes: [] }}
      >
        <Text type="secondary">
          You may review, add, or modify phenotype entries before submitting.
        </Text>
        <Form.List name="phenotypes">
          {(fields, { add, remove }) => (
            <>
              <Form.Item>
                <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                  Add Phenotype Entry
                </Button>
              </Form.Item>
              {fields.map(({ key, name, ...restField }) => (
                <Space
                  key={key}
                  style={{
                    display: "flex",
                    marginBottom: 12,
                    alignItems: "start",
                  }}
                  align="baseline"
                >
                  <MinusCircleOutlined onClick={() => remove(name)} />
                  <Form.Item
                    {...restField}
                    name={[name, "phenotype_id"]}
                    label="Phenotype ID"
                    rules={[{ required: true }]}
                    
                  >
                    <Input style={{ width: 120 }} disabled/>
                  </Form.Item>
                  <Form.Item
                    {...restField}
                    name={[name, "term_id"]}
                    label="Term ID"
                    rules={[{ required: true }]}
                  >
                    <Input style={{ width: 107 }} />
                  </Form.Item>
                  <Form.Item
                    {...restField}
                    name={[name, "presence"]}
                    label="Presence"
                    rules={[{ required: true }]}
                  >
                    <Select style={{ width: 104 }}>
                      <Option value="present">Present</Option>
                      <Option value="absent">Absent</Option>
                      <Option value="unknown">Unknown</Option>
                    </Select>
                  </Form.Item>
                  <Form.Item
                    {...restField}
                    name={[name, "ontology"]}
                    label="Ontology"
                    rules={[{ required: true }]}
                  >
                    <Select style={{ width: 100 }}>
                      <Option value="HPO">HPO</Option>
                      <Option value="MONDO">MONDO</Option>
                      <Option value="ORPHA">ORPHA</Option>
                      <Option value="OMIM">OMIM</Option>
                      <Option value="DOID">DOID</Option>
                      <Option value="NCIT">NCIT</Option>
                    </Select>
                  </Form.Item>
                  <Form.Item
                    {...restField}
                    name={[name, "additional_details"]}
                    label="Additional Details"
                  >
                    <Input.TextArea rows={3} style={{ width: 250 }} />
                  </Form.Item>
                    <Form.Item
                    {...restField}
                    name={[name, "onset_age_range"]}
                    label="Onset Age Range"
                    >
                    <Select showSearch allowClear optionFilterProp="label" style={{ width: 280 }}>
                        {Object.keys(onsetAgeRange).map((option) => (
                        <Option key={option} value={option} label={`${option}; ${onsetAgeRange[option]}`}>
                            {option}; {onsetAgeRange[option]}
                        </Option>
                        ))}
                    </Select>
                    </Form.Item>
                  <Form.Item
                    {...restField}
                    name={[name, "syndromic"]}
                    label="Syndromic"
                  >
                    <Select style={{ width: 100 }} allowClear>
                      <Option value="yes">yes</Option>
                      <Option value="no">no</Option>
                    </Select>
                  </Form.Item>
                </Space>
              ))}
            </>
          )}
        </Form.List>
      </Form>
    </Modal>
  );
};
