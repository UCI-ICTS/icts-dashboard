// src/components/SchemaForm.js

import { useEffect, useState, useMemo, useRef } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Form, Input, InputNumber, Select, Button, Switch, Tooltip, message, Modal, Checkbox } from "antd";
import { InfoCircleOutlined, MinusCircleOutlined, PlusOutlined } from "@ant-design/icons";
import { createEntry, updateEntry, deleteEntry, fetchTable } from "../slices/dataSlice";
import { getValidationRules, foreignKeyFields, onsetAgeRange, specimenType, biobankMapping } from "../utils/schemaAndTables";
import errorService from "../services/error.service";

const { Option } = Select;

/* const onChange = (date, dateString) => {  // From Antd DatePicker example
  console.log(date, dateString);
};*/

const SchemaField = ({ keyName, schema, requiredFields, form, readOnly, tableName, addEntry }) => {
  const dispatch = useDispatch();
  const listContainerRef = useRef(null);
  // Foreign-key mapping (expect: { sourceTable, apiKey, valueKey, labelKey? })
  const foreignMap = foreignKeyFields?.[tableName]?.[keyName];

  const rules = useMemo(
    () => getValidationRules(keyName, schema, requiredFields, form.getFieldValue),
    [keyName, schema, requiredFields, form]
  );

  // Collect conditional dependencies from rules
  const deps = useMemo(
    () => rules.flatMap(r => r?._conditionalDependencies ?? []),
    [rules]
  );

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

  // ---------- Foreign Key handling ----------
  const sourceTable = foreignMap?.sourceTable;
  const rawData = useSelector(state =>
    sourceTable ? state.data[sourceTable] : undefined
  );
  
  const dependantValue = foreignMap?.dependsOn ? form.getFieldValue(foreignMap.dependsOn) : null;
  
  const foreignData = useMemo(() => {
    if (foreignMap?.filterBy && dependantValue) {
      console.log(dependantValue, foreignMap.filterBy);
      return rawData?.filter(entry => entry[foreignMap.filterBy] == dependantValue) || [];
    }
    return rawData || [];
  }, [rawData, foreignMap, dependantValue]);
  
  useEffect(() => {
    if (foreignMap?.sourceTable && !foreignData.length) {
      dispatch(fetchTable(foreignMap.apiKey));
    }
  }, [dispatch, foreignMap, foreignData]);

  if (foreignMap) {
    // support labelKey for display; fallback to apiKey for backward-compat
    const { valueKey, apiKey, labelKey = apiKey } = foreignMap;
    
    // Check if foreignMap defines a default value (e.g., 0)
    const extendedOptions = [...foreignData];
    if (
      foreignMap.default !== undefined && 
      !foreignData.some(item => String(item[valueKey]) === String(foreignMap.default))
    ) {
      extendedOptions.unshift({
        [valueKey]: foreignMap.default,
        [labelKey]: `${foreignMap.default} (Not Available)`
      });
    }

    if (schema.type === "array") {
      return (
        <Form.Item
          key={keyName}
          name={keyName}
          label={label}
          dependencies={deps}
          rules={rules.map(({ _conditionalDependencies, ...r }) => r)}
        >
          <Select
            mode="multiple"
            showSearch
            allowClear
            optionFilterProp="label"
            disabled={readOnly}
          >
            {extendedOptions.map((item) => (
              <Select.Option
                key={item[valueKey]}
                value={item[valueKey]}
                label={item[labelKey]}
              >
                {item[labelKey]}
              </Select.Option>
            ))}
          </Select>
        </Form.Item>
      );
    }

    return (
      <Form.Item
        key={keyName}
        name={keyName}
        label={label}
        dependencies={deps}
        rules={rules.map(({ _conditionalDependencies, ...r }) => r)}
      >
        <Select showSearch allowClear optionFilterProp="label" disabled={readOnly}>
          {extendedOptions.map((item) => (
            <Select.Option
              key={item[valueKey]}
              value={item[valueKey]}
              label={item[labelKey]}
            >
              {item[labelKey]}
            </Select.Option>
          ))}
        </Select>
      </Form.Item>
    );
  }

  // ---------- Enums with special mapping ----------
  if (schema.enum) {
    if (keyName === "specimen_type") {
      return (
        <Form.Item
          key={keyName}
          name={keyName}
          label={label}
          dependencies={deps}
          rules={rules.map(({ _conditionalDependencies, ...r }) => r)}
        >
          <Select disabled={readOnly} showSearch allowClear optionFilterProp="label">
            {schema.enum.map((option) => (
              <Option key={option} value={option} label={`${option}; ${specimenType[option]}`}>
                {option}; {specimenType[option]}
              </Option>
            ))}
          </Select>
        </Form.Item>
      );
    }

    if (keyName === "onset_age_range") {
      return (
        <Form.Item
          key={keyName}
          name={keyName}
          label={label}
          dependencies={deps}
          rules={rules.map(({ _conditionalDependencies, ...r }) => r)}
        >
          <Select disabled={readOnly} showSearch allowClear optionFilterProp="label">
            {schema.enum.map((option) => (
              <Option key={option} value={option} label={`${option}; ${onsetAgeRange[option]}`}>
                {option}; {onsetAgeRange[option]}
              </Option>
            ))}
          </Select>
        </Form.Item>
      );
    }

    return (
      <Form.Item
        key={keyName}
        name={keyName}
        label={label}
        dependencies={deps}
        rules={rules.map(({ _conditionalDependencies, ...r }) => r)}
      >
        <Select disabled={readOnly} showSearch allowClear>
          {schema.enum.map((option) => (
            <Option key={option} value={option}>
              {option}
            </Option>
          ))}
        </Select>
      </Form.Item>
    );
  }

  // ---------- Primitives ----------
  if (schema.type === "string") {
    if (keyName === `${tableName}_id` && !readOnly) {
      return (
        <Form.Item
          key={keyName}
          name={keyName}
          label={label}
          dependencies={deps}
          rules={rules.map(({ _conditionalDependencies, ...r }) => r)}
        >
          <Input disabled={!addEntry}/>
        </Form.Item>
      );
    } else if (tableName === "phenotype" && keyName === "phenotype_id") {
      return (
        <Form.Item
          key={keyName}
          name={keyName}
          label={label}
          dependencies={deps}
          rules={rules.map(({ _conditionalDependencies, ...r }) => r)}
        >
          <Input disabled={true}/>
        </Form.Item>
      );
    }
    /* else if (tableName === "biobank" && keyName.includes("date")) {
      return (
        <Form.Item
          key={keyName}
          name={keyName}
          label={label}
          dependencies={deps}
          rules={rules.map(({ _conditionalDependencies, ...r }) => r)}
        >
          <DatePicker onChange={onChange} disabled={readOnly} />
        </Form.Item>
      )
    } */
    else if (tableName === "biobank" && keyName in biobankMapping) {
      return (
        <Form.Item
          key={keyName}
          name={keyName}
          label={label}
          dependencies={deps}
          rules={rules.map(({ _conditionalDependencies, ...r }) => r)}
        >
          <Select
            disabled={readOnly}
            showSearch
            allowClear
            optionFilterProp="label"
            options={biobankMapping[keyName]}
            />
        </Form.Item>
      )
    } else {
      return (
        <Form.Item
          key={keyName}
          name={keyName}
          label={label}
          dependencies={deps}
          rules={rules.map(({ _conditionalDependencies, ...r }) => r)}
        >
          <Input disabled={readOnly}/>
        </Form.Item>
      );
    }
  }

  if (schema.type === "number" || schema.type === "integer") {
    return (
      <Form.Item
        key={keyName}
        name={keyName}
        label={label}
        dependencies={deps}
        rules={rules.map(({ _conditionalDependencies, ...r }) => r)}
      >
        <InputNumber
          style={{ width: "100%" }}
          disabled={readOnly}
          parser={(value) => value === "" ? null : parseFloat(value)}
          formatter={(value) => value}
        />
      </Form.Item>
    );
  }

  if (schema.type === "boolean") {
    return (
      <Form.Item
        key={keyName}
        name={keyName}
        label={label}
        // Switch needs valuePropName="checked" to bind boolean
        valuePropName="checked"
        dependencies={deps}
        rules={rules.map(({ _conditionalDependencies, ...r }) => r)}
      >
        <Switch checkedChildren="Yes" unCheckedChildren="No" disabled={readOnly} />
      </Form.Item>
    );
  }

  // ---------- Arrays ----------
  if (schema.type === "array") {
    if (schema.items?.enum) {
      // enum-based array as multi-select
      return (
        <Form.Item
          key={keyName}
          name={keyName}
          label={label}
          dependencies={deps}
          rules={rules.map(({ _conditionalDependencies, ...r }) => r)}
        >
          <Select disabled={readOnly} mode="multiple" showSearch allowClear>
            {schema.items.enum.map((option) => (
              <Option key={option} value={option}>
                {option}
              </Option>
            ))}
          </Select>
        </Form.Item>
      );
    }

    // Free-form text array via Form.List
    // wrap in a dependency-aware noStyle Item so conditional rules re-run when drivers change
    return (
      <Form.Item key={keyName} label={label}>
        <Form.Item noStyle dependencies={deps}>
          {() => (
            <div ref={listContainerRef}>
              <Form.List name={keyName} rules={rules.map(({ _conditionalDependencies, ...r }) => r)}>
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
                        <Button
                          type="dashed"
                          onClick={() => {
                            add();
                            setTimeout(() => {
                              const inputs = listContainerRef.current?.querySelectorAll('input');
                              if (inputs?.length) inputs[inputs.length - 1].focus();
                            }, 0);
                          }}
                          block
                          icon={<PlusOutlined />}
                        >
                          Add item
                        </Button>
                      </Form.Item>
                    )}
                  </>
                )}
              </Form.List>
            </div>
          )}
        </Form.Item>
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
  addEntry,
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
    if (result["phenotype_id"] === null && result["participant_id"] && result["term_id"]) {
      result["phenotype_id"] = `${result["participant_id"]}_${result["term_id"]}`;
    }
    return result;
  };

  const handleSubmit = async (values) => {
    try {
      const normalized = normalizeArrays(values, schema.properties);
      const isUpdate = !!(initialValues && Object.keys(initialValues).length);
      if ("needs_review" in formInstance.getFieldsValue()) {
        normalized.needs_review = formInstance.getFieldValue("needs_review");
      }
      console.log(values, formInstance.getFieldValue("needs_review"))
      const action = isUpdate
        ? updateEntry({ table, data: [normalized] })
        : createEntry({ table, data: [normalized] });

      await dispatch(action).unwrap();
      formInstance.resetFields();
      onClose?.();
    } catch (error) {
      console.error("Error submitting form:", error);
    }
  };

  const handleCancel = () => {
    formInstance.resetFields();
    setEditMode(false);
    onClose?.();
  };

  return (
    <Form form={formInstance} layout="horizontal" onFinish={handleSubmit} style={{ maxWidth: 600 }}>
      <Form.Item name="needs_review" noStyle>
        <Input type="hidden" />
      </Form.Item>
      {isAdmin && (

<div className="schema-form-update">
  <div className="update-info">
    <span>
      Last update by <b>{initialValues["changed_by"]}</b> at{" "}
      <b>{initialValues["updated_at"]}</b>
    </span>
  </div>

  <div className="review-actions">
    
    <Tooltip title="Enable 'Edit Mode' to DELETE entry (not reversible)">
      <Button onClick={handleDelete} disabled={!editMode} danger>
        DELETE
      </Button>
    </Tooltip>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <Tooltip title="Toggle NEEDS REVIEW mode">
      <span> Needs Review </span>
      <Form.Item label="Needs Review" shouldUpdate noStyle>
        {({ getFieldValue, setFieldValue }) => {
          const currentValue = getFieldValue("needs_review");

          const handleToggle = () => {
            Modal.confirm({
              title: currentValue
                ? "Unset needs review flag? That action will make this object viewable to everyone."
                : "Mark this entry as needing review? That action will make this object viewable only by admins.",
              onOk: () => setFieldValue("needs_review", !currentValue),
            });
          };

          return (
            <Switch
              checked={currentValue}
              onChange={handleToggle}
              disabled={!editMode}
            />
          );
        }}
      </Form.Item>
    </Tooltip>
  </div>
</div>

      )}
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 12, gap: 8 }}>
        <span>Edit Mode</span>
        <Tooltip title="Toggle edit mode">
          <Switch checked={editMode} onChange={setEditMode} />
        </Tooltip>
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
          addEntry={addEntry}
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
