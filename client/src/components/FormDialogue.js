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
      validator = Yup.array().of(Yup.string().oneOf(value.items.enum));
      if (jsonSchema.required?.includes(key)) {
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
  const [editForm, setEditForm] = useState(false);
  const handleEdit = () => setEditForm(!editForm);
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

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>{schema.title?.charAt(0).toUpperCase() + schema.title?.slice(1) || "Form"} Details</DialogTitle>
      <DialogContent>
        {selectedRow && (
          <Formik
            initialValues={initialValues}
            validationSchema={yupSchema}
            onSubmit={async (values, { setSubmitting, setErrors }) => {
              try {
                const result = await dispatch(updateTable({ table: rowID, data: values, token }));
                if (result.meta.requestStatus === "fulfilled") {
                  onClose();
                } else {
                  setErrors({ form: "Submission failed. Please try again." });
                }
              } catch (error) {
                console.error("Form error", error);
                setErrors({ form: error.message || "An unexpected error occurred." });
              } finally {
                setSubmitting(false);
              }
            }}
          >
            {({ values, handleChange, handleBlur, touched, errors }) => (
              <Form>
                {errors.form && <div style={{ color: "red", marginBottom: "10px" }}>{errors.form}</div>}
                <DialogActions>
                  <Button onClick={handleEdit} color="primary">Edit</Button>
                  <Button onClick={onClose} color="secondary">Close</Button>
                  <Button type="submit" color="primary">Submit</Button>
                </DialogActions>
                {Object.entries(selectedRow).map(([key]) => (
                  <Grid container spacing={2} key={key} alignItems="center">
                    {editForm ? (
                      <Grid item xs>
                        <TextField
                          label={key}
                          name={key}
                          type={schema.properties[key].type === "integer" ? "number" : "text"}
                          inputProps={schema.properties[key].type === "integer" ? { step: 1 } : {}}
                          value={values[key] || ""}
                          onChange={handleChange}
                          onBlur={handleBlur}
                          fullWidth
                          disabled={initialFieldValues[key] !== "" && identifier === key}
                          margin="normal"
                          error={touched[key] && Boolean(errors[key])}
                          helperText={touched[key] && errors[key]}
                        />
                      </Grid>
                    ) : (
                      <Grid item>
                        <Tooltip title={schema.properties[key]?.description || "Description unavailable"} arrow>
                          <div style={{ fontWeight: "bold", cursor: "help" }}>{key}:&nbsp;</div>
                        </Tooltip>
                        <div>{selectedRow[key]}</div>
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
