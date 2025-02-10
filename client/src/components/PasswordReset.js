import React from "react";
import { 
  Button, Card, Dialog, DialogActions, DialogContent, DialogTitle, TextField
} from "@mui/material";
import { useDispatch, useSelector } from "react-redux";
import { Form, Formik, Field, ErrorMessage, useField } from "formik";
import * as Yup from "yup";
import { changePassword } from "../slices/accountSlice";

export default function PasswordReset({ open, setOpen }) {
  const dispatch = useDispatch();
  const token = useSelector((state) => state.account.user.access_token);
  const handleClose = () => {
    setOpen(false);
  };

  return (
    <Dialog open={open} onClose={handleClose}>
      <Card sx={{ padding: 2 }}>
        <DialogTitle>Password Reset</DialogTitle>
        <Formik
          initialValues={{
            old_password: "",
            new_password: "",
            confirm_password: "",
            token: token
          }}
          validationSchema={Yup.object().shape({
            old_password: Yup.string()
              .min(6, "Password must be at least 6 characters.")
              .max(40, "Password must be at most 40 characters.")
              .required("This field is required!"),
            new_password: Yup.string()
              .min(6, "Password must be at least 6 characters.")
              .max(40, "Password must be at most 40 characters.")
              .required("This field is required!"),
            confirm_password: Yup.string()
              .oneOf([Yup.ref("new_password")], "Passwords must match")
              .required("This field is required!"),
          })}
          onSubmit={async (values, { setSubmitting, resetForm }) => {
            try {
              dispatch(changePassword(values)); 
              resetForm();
              setOpen(false);
            } catch (error) {
              console.error("Password reset failed:", error);
            } finally {
              setSubmitting(false); 
            }
          }}
        >
          {({ isSubmitting }) => (
            <Form>
              <DialogContent>
                <FieldWithError name="old_password" label="Old Password" autoComplete="current-password" />
                <FieldWithError name="new_password" label="New Password" autoComplete="new-password" />
                <FieldWithError name="confirm_password" label="Confirm Password" autoComplete="new-password" />
              </DialogContent>
              <DialogActions>
                <Button
                  id="submit-resetPassword"
                  disabled={isSubmitting}
                  variant="contained"
                  type="submit"
                  color="primary"
                >
                  Submit
                </Button>
                <Button
                  id="cancel-resetPassword"
                  onClick={handleClose}
                  variant="outlined"
                  color="secondary"
                >
                  Cancel
                </Button>
              </DialogActions>
            </Form>
          )}
        </Formik>
      </Card>
    </Dialog>
  );
}

// Extracted Component for Handling Field Errors Properly
function FieldWithError({ name, label, autoComplete }) {
  const [field, meta] = useField(name);
  return (
    <TextField
      {...field}
      label={label}
      fullWidth
      margin="dense"
      variant="outlined"
      type="password"
      autoComplete={autoComplete}
      error={meta.touched && Boolean(meta.error)}
      helperText={meta.touched && meta.error}
    />
  );
}
