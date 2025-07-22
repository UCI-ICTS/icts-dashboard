// src/components/SchemaForm.js

import { useEffect, useState} from "react";
import { Form, Input, InputNumber, Select, Button, Switch, Tooltip } from "antd";
import { InfoCircleOutlined, MinusCircleOutlined, PlusOutlined } from "@ant-design/icons";
import { createEntry, updateTable, deleteEntry } from "../slices/dataSlice";
import { useDispatch } from "react-redux";
import { getValidationRules } from "../utils/schemaAndTables";

const { Option } = Select;


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

  // Handle foreign keys in tables
  // if (schema.title == "participant") {
  //   if (keyName == "internal_project_id") {
  //     return (
  //       <Form.Item key={keyName} name={keyName} label={label} rules={rules}>
  //         <Select>
  //           {schema.enum.map((option) => (
  //             <Option key={option} value={option} disabled={readOnly}>
  //               {option}
  //             </Option>
  //           ))}
  //         </Select>
  //       </Form.Item>
  //     );
  //   }
  //   if (keyName == "family_id") {
  //     return (
  //       <Form.Item key={keyName} name={keyName} label={label} rules={rules}>
  //         <Select>
  //           {schema.enum.map((option) => (
  //             <Option key={option} value={option} disabled={readOnly}>
  //               {option}
  //             </Option>
  //           ))}
  //         </Select>
  //       </Form.Item>
  //     );
  //   }
  // }
  // if (schema.title == "phenotype") {
  //   if (keyName == "participant_id") {
  //     return (
  //       <Form.Item key={keyName} name={keyName} label={label} rules={rules}>
  //         <Select>
  //           {schema.enum.map((option) => (
  //             <Option key={option} value={option} disabled={readOnly}>
  //               {option}
  //             </Option>
  //           ))}
  //         </Select>
  //       </Form.Item>
  //     );
  //   }
  // }

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

//  Pay attention to the props
const SchemaForm = ({
  schema,
  form,
  open,
  isAdmin = false,
  initialValues,
  setAddModalVisible,
  setEntry,
}) => {
  const dispatch = useDispatch();
  const [editMode, setEditMode] = useState(false);
  const requiredFields = schema.required || [];
  const table = schema.title

  useEffect(() => {
    form.setFieldsValue(initialValues || {});
  }, [initialValues, form]);

  useEffect(() => {
    if (!open) {
      setEditMode(false);
    }
  }, [open]);

  const handleDelete = () => {
    const idList = initialValues?.[`${table}_id`];
    dispatch(deleteEntry({ table: table, idList }))
      .unwrap()
      .then(() => {
        setAddModalVisible(false);
        setEntry(null);
        form.resetFields();
      })
      .catch((err) => console.error("Delete failed", err));
  };

  const handleSubmit = async (values) => {
    try {
      const updateForm = initialValues && Object.keys(initialValues).length > 0;
      const action = updateForm
        ? updateTable({ table: table, data: [values] })
        : createEntry({ table: table, data: [values] });
      console.log(action)
      const result = await dispatch(action);
      if (result.meta.requestStatus === "fulfilled") {
        setAddModalVisible(false);
        setEntry(null);
        form.resetFields();
      } else {
        console.warn("Submission failed:", result);
      }
    } catch (error) {
      console.error("Error submitting form:", error);
    }
  };

  const handleCancel = () => {
    form.resetFields();
    setAddModalVisible(false);
    setEntry(null);
  };

  return (
    <Form form={form} layout="vertical" onFinish={handleSubmit} style={{ maxWidth: 600 }}>
      {/* Edit/Delete Controls */}
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

      {/* Dynamic Fields */}
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

      {/* Submit/Cancel Buttons */}
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
