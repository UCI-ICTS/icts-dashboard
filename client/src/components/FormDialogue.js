// src/components/FormDialogue.js

import React from 'react';
import PropTypes from 'prop-types';
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
} from "@material-ui/core";
import { Formik, Form, FieldArray } from 'formik';
import * as Yup from 'yup';
import { useDispatch, useSelector } from 'react-redux';
import { updateTable } from '../slices/dataSlice';
import AddCircleIcon from '@mui/icons-material/AddCircle';
import RemoveCircleIcon from '@mui/icons-material/RemoveCircle';

// Utility function to convert JSON schema to Yup validation schema
const jsonSchemaToYup = (jsonSchema) => {
    const yupSchema = {};
  
    Object.entries(jsonSchema.properties).forEach(([key, value]) => {
      let validator = Yup.mixed();
  
      // Add validation based on type
      if (value.type === 'string') {
        validator = Yup.string();
        if (value.minLength) validator = validator.min(value.minLength);
        if (value.maxLength) validator = validator.max(value.maxLength);
      } else if (value.type === 'integer') {
        validator = Yup.number().integer();
        if (value.minimum) validator = validator.min(value.minimum);
        if (value.maximum) validator = validator.max(value.maximum);
       }else if (value.type === 'array' && value.items?.enum) {
        validator = Yup.array()
          .of(Yup.string().oneOf(value.items.enum))
          .min(1, `${key} must have at least one selected value`);
      }
    
      // Mark field as required if it's in the "required" list
      if (jsonSchema.required && jsonSchema.required.includes(key)) {
        validator = validator.required(`${key} is required`);
      }
  
      yupSchema[key] = validator;
    });
  
    return Yup.object().shape(yupSchema);
  };

const DialogForm = ({ open, onClose, schema, selectedRow, rowID }) => {
    const dispatch = useDispatch();
    const token = useSelector((state) => state.account.user?.access_token);
    const yupSchema = React.useMemo(() => jsonSchemaToYup(schema), [schema]);
    
    // Default initialization of selectedRow
    const initialValues = React.useMemo(() => {
        if (!selectedRow) return {};

        const defaultValues = {};
        Object.entries(schema.properties).forEach(([key, fieldSchema]) => {
            if (fieldSchema.type === "array" && fieldSchema.items?.type === "string") {
                // Initialize arrays with empty array if not provided
                defaultValues[key] = Array.isArray(selectedRow[key]) ? selectedRow[key] : [];
            } else {
                // Use provided value or an empty string as default
                defaultValues[key] = selectedRow[key] ?? "";
            }
        });
        return { ...defaultValues, ...selectedRow }; // Merge with the actual values
    }, [selectedRow, schema]);

    return (
    <Dialog open={open} onClose={onClose} className="dialog-form-container">
      <DialogTitle className="dialog-form-title">{schema.title || "Form" } Details</DialogTitle>
      <DialogContent className="dialog-form-content">
        {selectedRow && (
          <Formik
            initialValues={initialValues}
            validationSchema={yupSchema}
            onSubmit={async (values) => {
                console.log('Form Submitted', rowID, values);
                try {
                  const result = await dispatch(updateTable({table:rowID, data: values, token:token}));
                  if (result.meta.requestStatus === 'fulfilled') {
                  onClose();
                  } else {
                    console.log('Form error', result.error);
                    onClose();
                  }
                } catch (error) {
                  console.log('Form error', error);
                  onClose();
                }
              }}
          >
            {({ values, handleChange, handleBlur, touched, errors }) => (
              <Form>
                <DialogActions className="dialog-form-actions">
                  <Button onClick={onClose} color="secondary">
                    Close
                  </Button>
                  <Button type="submit" color="primary">
                    Submit
                  </Button>
                </DialogActions>

                {Object.entries(selectedRow).map(([key, value]) => {
                  const fieldSchema = schema.properties[key];
                  return (
                    <Grid container spacing={2} key={key} alignItems="center">
                      <Grid item>
                        <Tooltip title={fieldSchema.description || ''} arrow>
                          <span style={{ fontWeight: 'bold' }}>{key}</span>
                        </Tooltip>
                      </Grid>
                      <Grid item xs>
                        {fieldSchema.type === 'array' && fieldSchema.items?.enum ? (
                          <FormGroup>
                            {fieldSchema.items.enum.map((option) => (
                              <FormControlLabel
                                key={option}
                                control={
                                  <Checkbox
                                    name={key}
                                    value={option}
                                    checked={values[key]?.includes(option)}
                                    onChange={(event) => {
                                        const currentValues = values[key] || [];
                                        if (event.target.checked) {
                                        handleChange({
                                            target: {
                                            name: key,
                                            value: [...currentValues, option],
                                            },
                                        });
                                        } else {
                                        handleChange({
                                            target: {
                                            name: key,
                                            value: currentValues.filter((val) => val !== option),
                                            },
                                        });
                                        }
                                    }}
                                  />
                                }
                                label={option}
                              />
                            ))}
                            {touched[key] && errors[key] && (
                                <FormHelperText error>{errors[key]}</FormHelperText>
                            )}
                          </FormGroup>
                        ) : fieldSchema.type === 'array' && fieldSchema.items?.type === 'string' ? (
                        <FieldArray name={key}>
                          {(arrayHelpers) => (
                              <div>
                              {Array.isArray(values[key]) && values[key]?.map((item, index) => (
                                <Grid container spacing={1} alignItems="center" key={index}>
                                  <Grid item xs={10}>
                                    <TextField
                                      name={`${key}.${index}`}
                                      value={item}
                                      onChange={handleChange}
                                      onBlur={handleBlur}
                                      fullWidth
                                      margin="normal"
                                      error={touched[key]?.[index] && Boolean(errors[key]?.[index])}
                                      helperText={touched[key]?.[index] && errors[key]?.[index]}
                                      label={`Item ${index + 1}`}
                                    />
                                  </Grid>
                                  <Grid item xs={2}>
                                    <Button
                                      type="button"
                                      onClick={() => arrayHelpers.remove(index)}
                                      color="secondary"
                                    >
                                      <RemoveCircleIcon />
                                    </Button>
                                  </Grid>
                                </Grid>
                              ))}
                              <Button
                                type="button"
                                onClick={() => arrayHelpers.push([""])} // Add a new empty string to the array
                                color="primary"
                                startIcon={<AddCircleIcon />}
                              >
                                Add Item
                              </Button>
                            </div>
                          )}
                        </FieldArray>
                      ) : fieldSchema.enum ? (
                        <FormControl fullWidth margin="normal">
                          <InputLabel id={`${key}-label`}>{key}</InputLabel>
                            <Select
                              labelId={`${key}-label`}
                              id={key}
                              name={key}
                              value={values[key] || ''}
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
                        ) : (
                          <TextField
                            label={key}
                            name={key}
                            value={values[key] || ''}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            fullWidth
                            disabled={key === rowID && values[key] !== ''}
                            margin="normal"
                            error={touched[key] && Boolean(errors[key])}
                            helperText={touched[key] && errors[key]}
                          />
                        )}
                        </Grid>
                    </Grid>
                  );
                })}
              </Form>
            )}
          </Formik>
        )}
      </DialogContent>
    </Dialog>
  );
};

DialogForm.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  schema: PropTypes.object.isRequired,
  selectedRow: PropTypes.object,
  rowID: PropTypes.string.isRequired,
};

export default DialogForm;
