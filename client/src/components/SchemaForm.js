// src/components/SchemaForm.js

import React, { useEffect, useState} from "react";
import { Form, Input, InputNumber, Select, Button, Switch, Tooltip } from "antd";
import { InfoCircleOutlined, MinusCircleOutlined, PlusOutlined } from "@ant-design/icons";

const { Option } = Select;

const getValidationRules = (key, schema, requiredFields = []) => {
  const rules = [];

  if (requiredFields.includes(key)) {
    rules.push({ required: true, message: `${key} is required` });
  }

  if (schema.type === "string") {
    if (schema.minLength)
      rules.push({ min: schema.minLength, message: `${key} must be at least ${schema.minLength} characters` });
    if (schema.maxLength)
      rules.push({ max: schema.maxLength, message: `${key} must be at most ${schema.maxLength} characters` });
  }

  if (schema.type === "number" || schema.type === "integer") {
    if (schema.minimum !== undefined)
      rules.push({ type: "number", min: schema.minimum, message: `${key} must be at least ${schema.minimum}` });
    if (schema.maximum !== undefined)
      rules.push({ type: "number", max: schema.maximum, message: `${key} must be at most ${schema.maximum}` });
  }

  return rules;
};

const SchemaField = ({ keyName, schema, requiredFields, form, readOnly }) => {
  const label = (
    <span>
      {schema.title || keyName}
      {schema.description && (
        <Tooltip title={schema.description}>
          <InfoCircleOutlined style={{ marginLeft: 4 }} />
        </Tooltip>
      )}
    </span>
  );

  const rules = getValidationRules(keyName, schema, requiredFields);

  if (schema.enum) {
    return (
      <Form.Item key={keyName} name={keyName} label={label} rules={rules}>
        <Select>
          {schema.enum.map((option) => (
            <Option key={option} value={option} disabled={readOnly}>
              {option}
            </Option>
          ))}
        </Select>
      </Form.Item>
    );
  }

  if (schema.type === "string") {
    return (
      <Form.Item key={keyName} name={keyName} label={label} rules={rules}>
        <Input disabled={readOnly}/>
      </Form.Item>
    );
  }

  if (schema.type === "number" || schema.type === "integer") {
    return (
      <Form.Item key={keyName} name={keyName} label={label} rules={rules}>
        <InputNumber style={{ width: "100%" }} disabled={readOnly} />
      </Form.Item>
    );
  }

  if (schema.type === "array") {
    if (schema.items?.enum) {
      // Render enum-based array as multi-select
      return (
        <Form.Item key={keyName} name={keyName} label={label} rules={rules}>
          <Select disabled={readOnly} mode="multiple">
            {schema.items.enum.map((option) => (
              <Option key={option} value={option}>
                {option}
              </Option>
            ))}
          </Select>
        </Form.Item>
      );
    }

    // Render free-form text input array using Form.List
    return (
      <Form.Item key={keyName} label={label}>
        <Form.List name={keyName} rules={rules}>
          {(fields, { add, remove }) => (
            <>
              {fields.map(({ key, name, ...restField }) => (
                <Form.Item
                  key={key}
                  {...restField}
                  name={name}
                  rules={[{ required: true, message: "Field cannot be empty" }]}
                >
                  <Input
                    disabled={readOnly}
                    placeholder="Enter value"
                    addonAfter={
                      !readOnly && (
                        <MinusCircleOutlined onClick={() => remove(name)} />
                      )
                    }
                  />
                </Form.Item>
              ))}
              {!readOnly && (
                <Form.Item>
                  <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                    Add item
                  </Button>
                </Form.Item>
              )}
            </>
          )}
        </Form.List>
      </Form.Item>
    );
  }

  return null;
};

//  initialValues + onCancel as props
const SchemaForm = ({ schema, initialValues = {}, onSubmit, onCancel, form, open }) => {
  const [editMode, setEditMode] = useState(false);
  const requiredFields = schema.required || [];

  // set form values every time they change
  useEffect(() => {
    form.setFieldsValue(initialValues);
  }, [initialValues, form]);

  // Reset editMode when modal closes
  useEffect(() => {
    if (!open) {
      setEditMode(false);
    }
  }, [open]);

  const handleFinish = (values) => {
    onSubmit(values);
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleFinish}
      style={{ maxWidth: 600 }}
    >
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 12 }}>
      <div style={{ display: "flex", justifyContent: "flex-end", alignItems: "center", marginBottom: 16 }}>
        <span style={{ marginRight: 8 }}>Edit Mode</span>
        <Tooltip title="Toggle edit mode">
          <Switch checked={editMode} onChange={setEditMode} />
        </Tooltip>
      </div>
      </div>
      {Object.entries(schema.properties || {}).map(([key, value]) => (
        <SchemaField
          key={key}
          keyName={key}
          schema={value}
          requiredFields={requiredFields}
          form={form}
          readOnly={!editMode}
        />
      ))}
      {editMode && (
        <Form.Item>
          <Button type="primary" htmlType="submit">Submit</Button>
          {onCancel && (
            <Button onClick={onCancel} style={{ marginLeft: 8 }}>
              Cancel
            </Button>
          )}
        </Form.Item>
      )}
    </Form>
  );
};

export default SchemaForm;
