// src/pages/profile.js

import React, { useState} from "react";
import { Button, Card, CardContent, CardHeader, Grid, TextField } from "@material-ui/core";
import "../App.css"
import PasswordReset from "../components/PasswordReset.js";
import { useDispatch, useSelector } from "react-redux";
import { Field, Form, Formik } from "formik";
import * as Yup from "yup";

const ProfilePage = () => {
  const dispatch = useDispatch();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const user = useSelector((state) => state.account.user);
  return (
    <Card className="container-test" >
      <CardHeader title="Profile Card" />
      <CardContent>
        <Grid>
          <Formik
            enableReinitialize
            initialValues={user}
            validationSchema={Yup.object().shape({
              email: Yup.string().email()
                .email("This is not a valid email.")
                .required("This field is required!"),
            })}
            onSubmit={(values, {setSubmitting}) => {
              setSubmitting(true);
              console.log(values)
              // dispatch(account(values));
              setSubmitting(false);
            }}
          >
          {({values, isSubmitting}) => (
            <Form>
              <PasswordReset 
                open={open}
                setOpen={setOpen}
              />
              <Button
                variant="outlined"
                onClick={()=> setOpen(true)}
              >Change Password</Button>
                <br/>
                <br/>
              <Grid item>
                <Field
                  name="first_name"
                  as={TextField}
                  type="text"
                  label="Given Name"
                  variant="outlined"
                  // error={touched.username && Boolean(errors.username)}
                  // helperText={touched.username && errors.username}
                />
                <Field
                  name="last_name"
                  as={TextField}
                  type="text"
                  label="Family Name"
                  variant="outlined"
                  // error={touched.username && Boolean(errors.username)}
                  // helperText={touched.username && errors.username}
                />
              </Grid>
              <br/>
              <Grid item>
                <Field
                  name="email"
                  as={TextField}
                  type="email"
                  label="Email"
                  variant="outlined"
                  disabled={true}
                  // error={touched.password && Boolean(errors.password)}
                  // helperText={touched.password && errors.password}
                />
              </Grid>
              <br/>
              <Grid item>
                <Field
                  name="access_token"
                  as={TextField}
                  type="password"
                  label="Access Token"
                  variant="outlined"
                  disabled={true}
                  // error={touched.password && Boolean(errors.password)}
                  // helperText={touched.password && errors.password}
                />
                <button onClick={() =>  global.navigator.clipboard.writeText(user.access_token)}>Copy</button><br/>
              </Grid>
              <br/>
              <Button
                  type="submit"
                  className="button-confirm"
                  disabled={loading}
                  variant="contained"
                >
                  {loading && (
                    <span className="spinner-border spinner-border-sm"></span>
                  )}
                  <span>Update Profile</span>
                </Button>
            </Form>
          )}
          </Formik>        
        </Grid>
      </CardContent>
      {/* {JSON.stringify(user)} */}
    </Card>
  )
}

export default ProfilePage;