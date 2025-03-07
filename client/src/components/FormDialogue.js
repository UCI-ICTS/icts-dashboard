// src/components/FormDialogue.js
import React, { useState, useEffect, useMemo } from "react";
import PropTypes from "prop-types";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Tooltip,
  Grid,
  TextField,
  FormControl,
  FormControlLabel,
  FormGroup,
  Checkbox,
  Select,
  MenuItem,
  InputLabel,
  FormHelperText,
} from "@mui/material";
import { Formik, Form, FieldArray } from "formik";
import * as Yup from "yup";
import { useDispatch, useSelector } from "react-redux";
import { updateTable } from "../slices/dataSlice";
import AddCircleIcon from "@mui/icons-material/AddCircle";
import RemoveCircleIcon from "@mui/icons-material/RemoveCircle";
import ErrorBoundary from "./ErrorBoundary";

/**
 * Converts JSON schema into a Yup validation schema
 */
const jsonSchemaToYup = (jsonSchema) => {
  const yupSchema = {};

  Object.entries(jsonSchema.properties).forEach(([key, value]) => {
    let validator = Yup.mixed();

    if (value.type === "string") {
      validator = Yup.string().min(value.minLength || 0).max(value.maxLength || 255);
    } else if (value.type === "integer") {
      validator = Yup.number()
        .integer()
        .typeError(`${key} must be a valid integer`)
        .min(value.minimum || Number.MIN_SAFE_INTEGER)
        .max(value.maximum || Number.MAX_SAFE_INTEGER);
    } else if (value.type === "number") {
      validator = Yup.number()
        .typeError(`${key} must be a valid number`)
        .min(value.minimum || Number.MIN_SAFE_INTEGER)
        .max(value.maximum || Number.MAX_SAFE_INTEGER);
    } else if (value.type === "array" && value.items?.enum) {
      validator = Yup.array()
        .of(Yup.string().oneOf(value.items.enum))
        if (jsonSchema.required?.includes(key)) { // Only require if in required list
          validator = validator.min(1, `${key} must have at least one selected value`);
        }

    }

    if (jsonSchema.required?.includes(key)) {
      validator = validator.required(`${key} is required`);
    }

    yupSchema[key] = validator;
  });

  return Yup.object().shape(yupSchema);
};

const DialogForm = ({ open, onClose, schema, selectedRow, rowID, identifier }) => {
  const dispatch = useDispatch();
  const[editForm, setEditForm] = useState(false);
  const handleEdit = () => {setEditForm(!editForm)};
  const token = useSelector((state) => state.account.user?.access_token);

  const yupSchema = useMemo(() => jsonSchemaToYup(schema), [schema]);

  const initialValues = useMemo(() => {
    if (!selectedRow) return {};

    return Object.entries(schema.properties).reduce((acc, [key, fieldSchema]) => {
      acc[key] = fieldSchema.type === "array"
        ? Array.isArray(selectedRow[key]) ? selectedRow[key] : []
        : selectedRow[key] ?? (fieldSchema.type === "integer" ? null : "");
      return acc;
    }, {});
  }, [selectedRow, schema]);

  const [initialFieldValues, setInitialFieldValues] = useState({});

  useEffect(() => {
    setInitialFieldValues(initialValues);
  }, [initialValues]);

  /**
   * Renders the appropriate input field based on the schema definition
   */
  const renderField = (key, fieldSchema, values, handleChange, handleBlur, touched, errors) => {
    if (!fieldSchema) {
      console.error(`Field schema for "${key}" is undefined`);
      return (
        <div>Error: {key}</div>
      )
    }

    if (fieldSchema.type === "array" && fieldSchema.items?.enum) {
      return (
        <div className="form-checkbox-group">
          {/* Title above the checkbox group */}
          <Tooltip title={fieldSchema.description || `Options for ${key}`} arrow>
            <span className="form-checkbox-title">{key}</span>
          </Tooltip>

          <FormGroup>
            {fieldSchema.items.enum.map((option) => (
              <FormControlLabel
                key={option}
                className="form-checkbox"
                control={
                  <Checkbox
                    name={key}
                    value={option}
                    checked={values[key]?.includes(option)}
                    onChange={(e) => {
                      const updatedValues = e.target.checked
                        ? [...(values[key] || []), option]
                        : values[key].filter((val) => val !== option);
                      handleChange({ target: { name: key, value: updatedValues } });
                    }}
                  />
                }
                label={option}
              />
            ))}
          </FormGroup>

          {touched[key] && errors[key] && <FormHelperText error>{errors[key]}</FormHelperText>}
        </div>
      );
    }


    if (fieldSchema.type === "array" && fieldSchema.items?.type === "string") {
      return (
        <FieldArray name={key}>
          {(arrayHelpers) => (
            <>
              {Array.isArray(values[key]) &&
                values[key]?.map((item, index) => (
                  <Grid container spacing={1} alignItems="center" key={index}>
                    <Grid item xs={10}>
                    <Tooltip title={fieldSchema.description || `Item ${index + 1}`} arrow>
                      <TextField
                        name={`${key}.${index}`}
                        value={item}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        fullWidth
                        margin="normal"
                        error={touched[key]?.[index] && Boolean(errors[key]?.[index])}
                        helperText={touched[key]?.[index] && errors[key]?.[index]}
                        label={`${key} ${index + 1}`}
                      />
                      </Tooltip>
                    </Grid>
                    <Grid item xs={2}>
                      <Button onClick={() => arrayHelpers.remove(index)} color="secondary">
                        <RemoveCircleIcon />
                      </Button>
                    </Grid>
                  </Grid>
                ))}
              <Button onClick={() => arrayHelpers.push("")} color="primary" startIcon={<AddCircleIcon />}>
                Add Item
              </Button>
            </>
          )}
        </FieldArray>
      );
    }

    if (fieldSchema.enum) {
      return (
        <FormControl fullWidth margin="normal">
          <InputLabel id={`${key}-label`}>{key}</InputLabel>
          <Select
            labelId={`${key}-label`}
            id={key}
            name={key}
            value={values[key] || ""}
            onChange={handleChange}
            onBlur={handleBlur}
            error={touched[key] && Boolean(errors[key])}
          >
            {fieldSchema.enum.map((option) => (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            ))}
          </Select>
          <FormHelperText>{touched[key] && errors[key]}</FormHelperText>
        </FormControl>
      );
    }

    return (
      <TextField
        label={key}
        name={key}
        type={fieldSchema.type === "integer" ? "number" : "text"}
        inputProps={fieldSchema.type === "integer" ? { step: 1 } : {}}
        value={values[key] || ""}
        onChange={handleChange}
        onBlur={handleBlur}
        fullWidth
        disabled={initialFieldValues[key] !== "" && identifier === key}
        margin="normal"
        error={touched[key] && Boolean(errors[key])}
        helperText={touched[key] && errors[key]}
      />
    );
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>{schema.title.charAt(0).toUpperCase()+schema.title.slice(1) ||
        "Form"} Details</DialogTitle>
      <DialogContent>
        {selectedRow && (
          <Formik
            initialValues={initialValues}
            validationSchema={yupSchema}
            onSubmit={async (values) => {
              try {
                const result = dispatch(updateTable({ table: rowID, data: values, token }));
                if (result.meta.requestStatus === "fulfilled") onClose();
              } catch (error) {
                console.error("Form error", error);
                onClose();
              }
            }}
          >
            {({ values, handleChange, handleBlur, touched, errors }) => (
              <Form>
                <DialogActions>
                  <Button onClick={handleEdit} color="primary" Toggle Statue>Edit</Button>
                  <Button onClick={onClose} color="secondary">Close</Button>
                  <Button type="submit" color="primary">Submit</Button>
                </DialogActions>
                {Object.entries(selectedRow).map(([key]) => (
                  <Grid container spacing={2} key={key} alignItems="center">
                    {editForm ? (
                      <Grid item xs>
                        {renderField(
                          key, schema.properties[key], values, handleChange,
                          handleBlur=false, touched=false, errors=false
                        )}
                      </Grid>
                    ) : (
                    <Grid item>
                      <Tooltip title={
                        schema.properties[key]?.description ||
                        schema.properties[key]?.items?.description ||
                        "Description unavailable"} arrow>
                        <div style={{ display: "inline-block", fontWeight: "bold", cursor: "help" }}>
                          {key}:&nbsp;&nbsp;
                        </div>
                        <div style={{ display: "inline-block" }}>{selectedRow[key]}</div>
                      </Tooltip>
                    </Grid>
                    )}
                  </Grid>
                ))}
              </Form>
            )}
          </Formik>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default DialogForm;
