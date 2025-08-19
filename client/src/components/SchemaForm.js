// src/components/SchemaForm.js

import { useEffect, useState, useMemo } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Form, Input, InputNumber, Select, Button, Switch, Tooltip, message } from "antd";
import { InfoCircleOutlined, MinusCircleOutlined, PlusOutlined } from "@ant-design/icons";
import { createEntry, updateEntry, deleteEntry, fetchTable } from "../slices/dataSlice";
import { getValidationRules, foreignKeyFields, onsetAgeRange } from "../utils/schemaAndTables";
import errorService from "../services/error.service";

const { Option } = Select;

const SchemaField = ({ keyName, schema, requiredFields, form, readOnly, tableName  }) => {
  const dispatch = useDispatch();
  const foreignMap = foreignKeyFields?.[tableName]?.[keyName]
  const rules = getValidationRules(keyName, schema, requiredFields);

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

 const sourceTable = foreignMap?.sourceTable;

  const rawData = useSelector(state =>
    sourceTable ? state.data[sourceTable] : undefined
  );

  const foreignData = useMemo(() => rawData || [], [rawData]);


  useEffect(() => {
    if (foreignMap?.sourceTable && !foreignData.length) {
      dispatch(fetchTable(foreignMap.apiKey));
    }
  }, [dispatch, foreignMap, foreignData]);


  if (foreignMap) {
    const { valueKey, apiKey } = foreignMap;

    if (schema.type === "array") {
      return (
        <Form.Item key={keyName} name={keyName} label={label} rules={rules}>
          <Select
            mode="multiple"
            showSearch
            allowClear
            optionFilterProp="label"
            disabled={readOnly}
          >
            {foreignData.map((item) => (
              <Select.Option
                key={item[valueKey]}
                value={item[valueKey]}
                label={item[valueKey]}
              >
                {item[apiKey]}
              </Select.Option>
            ))}
          </Select>
        </Form.Item>
      );
    }

    return (
      <Form.Item key={keyName} name={keyName} label={label} rules={rules}>
        <Select showSearch allowClear optionFilterProp="label" disabled={readOnly}>
          {foreignData.map((item) => (
            <Select.Option
              key={item[valueKey]}
              value={item[valueKey]}
              label={item[valueKey]}
            >
              {item[apiKey]}
            </Select.Option>
          ))}
        </Select>
      </Form.Item>
    );
  }

  if (schema.enum) {
    if (keyName == "onset_age_range") {
      return (
        <Form.Item key={keyName} name={keyName} label={label} rules={rules}>
          <Select disabled={readOnly}>
            {schema.enum.map((option) => (
              <Option key={option} value={option} disabled={readOnly}>
                {option}; {onsetAgeRange[option]}
              </Option>
            ))}
          </Select>
        </Form.Item>
      );
    }
    return (
      <Form.Item key={keyName} name={keyName} label={label} rules={rules}>
        <Select disabled={readOnly}>
          {schema.enum.map((option) => (
            <Option key={option} value={option} >
              {option}
            </Option>
          ))}
        </Select>
      </Form.Item>
    );
  }

  if (schema.type === "string") {
    if (keyName == `${tableName}_id` && !readOnly) {
      return (
      <Form.Item key={keyName} name={keyName} label={label} rules={rules}>
        <Input disabled={true}/>
      </Form.Item>
      )
    }
    else if (tableName == "phenotype" && keyName == "phenotype_id") {
      return (
      <Form.Item key={keyName} name={keyName} label={label} rules={rules}>
        <Input disabled={true}/>
      </Form.Item>
      )
    }
    else {
      return (
        <Form.Item key={keyName} name={keyName} label={label} rules={rules}>
          <Input disabled={readOnly}/>
        </Form.Item>
      );
    }
  }

  if (schema.type === "number" || schema.type === "integer") {
    return (
      <Form.Item key={keyName} name={keyName} label={label} rules={rules}>
        <InputNumber style={{ width: "100%" }} disabled={readOnly} />
      </Form.Item>
    );
  }

  if (schema.type === "boolean") {
    return (
      <Form.Item key={keyName} name={keyName} label={label} rules={rules}>
        <Switch checkedChildren="Yes" unCheckedChildren="No" disabled={readOnly} />
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
                  rules={[{ required: true, message: "Field cannot be empty. Delete the entry or add a value." }]}
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

const SchemaForm = ({
  schema,
  form,
  open,
  isAdmin = false,
  initialValues,
  onClose,
}) => {
  const dispatch = useDispatch();
  const [editMode, setEditMode] = useState(false);
  const requiredFields = schema.required || [];
  const table = schema.title;

  const [internalForm] = Form.useForm();
  const formInstance = form ?? internalForm;

  useEffect(() => {
    formInstance.setFieldsValue(initialValues || {});
  }, [initialValues, formInstance]);

  useEffect(() => {
    if (open) {
      setEditMode(false);
      formInstance.setFieldsValue(initialValues || {});
    }
  }, [open, initialValues, formInstance]);

  const handleDelete = () => {
    const idList = initialValues?.[`${table}_id`];
    dispatch(deleteEntry({ table, idList }))
      .unwrap()
      .then(() => {
        formInstance.resetFields();
        onClose?.();
      })
      .catch((err) => message.error(errorService.printErrorMessages(err)));
  };

  const normalizeArrays = (obj, schemaProps) => {
    const result = { ...obj };
    Object.entries(schemaProps).forEach(([key, def]) => {
      if (def.type === "array" && result[key] === null) {
        result[key] = [];
      }
    });
    if (result["phenotype_id"] == null && result["participant_id"] && result["term_id"]) {
      result["phenotype_id"] = `${result["participant_id"]}_${result["term_id"]}`;
    }
    return result;
  };

  const handleSubmit = async (values) => {
    try {
      const normalized = normalizeArrays(values, schema.properties);
      const isUpdate = !!(initialValues && Object.keys(initialValues).length);
      const action = isUpdate
        ? updateEntry({ table, data: [normalized] })
        : createEntry({ table, data: [normalized] });

      await dispatch(action).unwrap();  // throws on error
      formInstance.resetFields();
      onClose?.();
    } catch (error) {
      console.error("Error submitting form:", error);
      message.error("Save failed");
    }
  };

  const handleCancel = () => {
    formInstance.resetFields();
    setEditMode(false);
    onClose?.();
  };

  return (
    <Form form={formInstance} layout="horizontal" onFinish={handleSubmit} style={{ maxWidth: 600 }}>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 12 }}>
        <span style={{ marginRight: 8 }}>Edit Mode</span>
        <Tooltip title="Toggle edit mode">
          <Switch checked={editMode} onChange={setEditMode} />
        </Tooltip>
        {isAdmin && (
          <Tooltip title="Enable 'Edit Mode' to DELETE entry (not reversible)">
            <Button onClick={handleDelete} disabled={!editMode} danger>
              DELETE
            </Button>
          </Tooltip>
        )}
      </div>

      {Object.entries(schema.properties || {}).map(([key, value]) => (
        <SchemaField
          key={key}
          keyName={key}
          schema={value}
          requiredFields={requiredFields}
          form={formInstance}
          readOnly={!editMode}
          tableName={schema.title}
        />
      ))}

      {editMode && (
        <Form.Item>
          <Button type="primary" htmlType="submit">Submit</Button>
          <Button onClick={handleCancel} style={{ marginLeft: 8 }}>Cancel</Button>
        </Form.Item>
      )}
    </Form>
  );
};

export default SchemaForm;
