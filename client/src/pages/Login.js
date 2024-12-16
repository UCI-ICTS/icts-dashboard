import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Navigate, useNavigate } from "react-router-dom";
import { Formik, Form, Field } from "formik";
import * as Yup from "yup";
import { Box, Button, Container, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Grid, TextField, Typography } from "@material-ui/core";
import { Link } from "react-router-dom";
import { login } from "../slices/accountSlice";
import { CheckBox, RememberMe } from "@mui/icons-material";
import { removeListener } from "@reduxjs/toolkit";

const Login = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [resetEmail, setResetEmail] = useState("");
  const { isLoggedIn } = useSelector((state) => state.account);

  const initialValues = {
    username: "",
    password: "",
    rememberMe: false,
  };

  const validationSchema = Yup.object().shape({
    username: Yup.string().required("This field is required!"),
    password: Yup.string()
      .min(4, "The password must be at least 4 characters.")
      .max(40, "The password must be at most 40 characters.")
      .required("This field is required!"),
  });

  const handleLogin = (formValue) => {
    const { username, password, rememberMe } = formValue;
    setLoading(true);
    dispatch(login({ username, password, rememberMe }))
      .unwrap()
      .then(() => {
        navigate("/");
        // global.window.location.reload();
      })
      .catch(() => {
        setLoading(false);
      });
  };

  const handleClose = () => {
    setOpen(false);
  };

  if (isLoggedIn) {
    return <Navigate to="/" />;
  }

  return (
    <Container>
      <Box display="flex" flexDirection="column" height="100%">
        <Container>
          <Grid item>
            <Typography variant="h4">Sign in</Typography>
            <Typography>Sign in using your Portal credentials</Typography>
            <Typography component={Link} to="/register">
              Don&apos;t have an account? Request one here.
            </Typography>
          </Grid>
          <br />
          <Typography variant="h5">Or</Typography>
          <Formik
            initialValues={initialValues}
            validationSchema={validationSchema}
            onSubmit={handleLogin}
          >
            {({ errors, touched }) => (
              <Form>
                <Grid item>
                  <Field
                    name="username"
                    as={TextField}
                    type="text"
                    label="User Name"
                    variant="outlined"
                    error={touched.username && Boolean(errors.username)}
                    helperText={touched.username && errors.username}
                  />
                </Grid>
                <br/>
                <Grid item>
                  <Field
                    name="password"
                    as={TextField}
                    type="password"
                    label="Password"
                    variant="outlined"
                    error={touched.password && Boolean(errors.password)}
                    helperText={touched.password && errors.password}
                  />
                </Grid>
                <br/>
                <Grid item>
                  <label>
                  <Field
                    name="rememberMe"
                    type="checkbox"
                    label="rememberMe"
                    variant="outlined"
                  />Remember Me</label>
                </Grid>
                <br/>
                <div className="form-group">
                  <Button
                    type="submit"
                    className="btn btn-primary btn-block"
                    disabled={loading}
                    color="primary"
                    variant="contained"
                  >
                    {loading && (
                      <span className="spinner-border spinner-border-sm"></span>
                    )}
                    <span>Login</span>
                  </Button>
                </div>
                <Button onClick={() => setOpen(true)}>
                  Forgot password? Reset it here
                </Button>
              </Form>
            )}
          </Formik>
        </Container>
        <Dialog open={open}>
          <DialogContent>
            <DialogTitle>Password Reset</DialogTitle>
            <DialogContentText>
              Enter your email address. If there is an account associated with
              that address, we will provide you a link to reset your password.
            </DialogContentText>
            <TextField
              required
              id="email-for-password-reset"
              label="Email address"
              variant="filled"
              value={resetEmail}
              onChange={(e) => {
                setResetEmail(e.target.value);
              }}
            />
          </DialogContent>
          <DialogActions>
            <Button
              id="Cancel-resetPassword"
              onClick={handleClose}
              variant="outlined"
              color="secondary"
            >
              Cancel
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default Login;
