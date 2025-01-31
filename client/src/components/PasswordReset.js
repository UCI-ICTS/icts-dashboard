import React from "react";
import { 
  Button, Card, Dialog, DialogActions, DialogContent, DialogTitle, TextField
} from "@mui/material";
import { useDispatch } from "react-redux";
import { Form, Formik } from "formik";
import * as Yup from "yup";
// import { changePassword } from ""../slices/accountSlice";

export default function PasswordReset ({open, setOpen}) {
  const dispatch = useDispatch();
  const handleClose = () => {
    setOpen(false);
  }

  return (
    <Dialog open={open}>
      <Card>
        <DialogTitle>Password Reset</DialogTitle>
        <Formik
          initialValues={{
            old_password:"",
            new_password:"",
            confirm_password:""
          }}
          validationSchema={Yup.object().shape({
            old_password: Yup.string()
              .test(
                "len",
                "The password must be between 6 and 40 characters.",
                (val) =>
                  val &&
                val.toString().length >= 6 &&
                val.toString().length <= 40
              )
              .required("This field is required!"),
            new_password: Yup.string()
              .test(
                "len",
                "The password must be between 6 and 40 characters.",
                (val) =>
                  val &&
                val.toString().length >= 6 &&
                val.toString().length <= 40
              )
              .required("This field is required!"),
            confirm_password: Yup.string()
              .oneOf([Yup.ref("new_password")], "Passwords must match")
              .required("This field is required!"),
          })}
          onSubmit = {(values, {setSubmitting, resetForm}) => {
            setSubmitting(true)
            console.log(values)
            // dispatch(changePassword(values))
            //   .unwrap()
            //   .then((response) => {
            //     console.log(response)
            //   })
            //   .catch((error) => {
            //     console.log(error)
            //   })
            setOpen(false)
            resetForm()
            setSubmitting(false)
          }}
        >
          {({isSubmitting})=> (
            <Form>
              <DialogContent>
                <TextField name='old_password' type='password' lable='Old Password' placeholder='Old Password'/><br/>
                <TextField name='new_password' type='password' lable='New Password' placeholder='New Password'/><br/>
                <TextField name='confirm_password' type='password'lable='Confirm Password' placeholder='Confirm Password'/><br/>
              </DialogContent>
              <DialogActions>
                <Button
                  id="submit-resetPassword"
                  disabled={isSubmitting}
                  variant="outlined"
                  type="submit"
                  // disabled={isSubmitting}
                  color="primary"
                >submit</Button>
                <Button
                  id="cancel-resetPassword"
                  onClick={handleClose}
                  variant="outlined"
                  color="secondary"
                >CANCEL</Button>
              </DialogActions>
            </Form>
          )}
        </Formik>
      </Card>
    </Dialog>
  )
}