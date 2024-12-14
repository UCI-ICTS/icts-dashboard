// src/components/auth/Login.js

import React, { useEffect, useState  } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Navigate, useNavigate } from "react-router-dom";
import { getAllParticipants } from "../slices/dataSlice";
import { TableForm } from "../components/TableForm";
import Form from '@rjsf/core';
import { RJSFSchema } from '@rjsf/utils';
import validator from '@rjsf/validator-ajv8';

// import { Formik, Form } from "formik";
import * as Yup from "yup";
import { Box, Button, Container, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Grid, TextField, Typography, Paper } from "@material-ui/core";
import { Link } from "react-router-dom";
import { login } from "../slices/accountSlice";
import NotificationBox from "../components/NotificationBox";

const Gregor = () => {
  let navigate = useNavigate();
  const dispatch = useDispatch();
  const [open, setOpen] = React.useState(false);
  const [loading, setLoading] = useState(false);
  const [resetEmail, setResetEmail] = React.useState("");
  const { isLoggedIn } = useSelector((state) => state.account);
//   const [schema, setSchema] = useState({});
  const [formData, setFormData] = useState({});

  const formType = "Participant"
  const schema = "/Users/hadleyking/GitHub/UCI-GREGoR/GREGor_dashboard/server/utilities/json_schemas/participant.json"
  const onSubmit = ({ formData }) => {
    console.log(formData)
    
  }

  const handleGet = () => {
    dispatch(getAllParticipants({}))
  }
  return (
    <Paper>
    <Container>
      <Box display="flex" flexdirection="column" height="100%" >
        <Container>
          <Grid item>
            <Typography variant="h4">{formType} Form</Typography>
          </Grid>
          <br/>
          <TableForm />
          <Button
              id="Cancel-resetPassword"
              onClick={handleGet}
              variant="outlined"
              color="primary"
            >get</Button>
        </Container>
        <NotificationBox />
      </Box>
    </Container>
    </Paper>
  );
};

export default Gregor;
