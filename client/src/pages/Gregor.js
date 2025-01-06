// src/components/auth/Login.js

import React, { useEffect, useState  } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Navigate, useNavigate } from "react-router-dom";
import { getAllParticipants } from "../slices/dataSlice";
import { TableForm } from "../components/TableForm";


// import { Formik, Form } from "formik";
import * as Yup from "yup";
import { Box, Button, Container, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Grid, TextField, Typography, Paper } from "@material-ui/core";
import { Link } from "react-router-dom";
import { login } from "../slices/accountSlice";

const Gregor = () => {
  let navigate = useNavigate();
  const dispatch = useDispatch();
  const tableData = useSelector(state => state.data['participants']);
  const [open, setOpen] = React.useState(false);
  const [loading, setLoading] = useState(false);
//   const [schema, setSchema] = useState({});
  const [formData, setFormData] = useState({});

  const formType = "Participant"
  const schema = "/Users/hadleyking/GitHub/UCI-GREGoR/GREGor_dashboard/server/utilities/json_schemas/participant.json"
  const token = useSelector((state) => state.account.user?.access_token)
  const onSubmit = ({ formData }) => {
    console.log(formData)
  }
  const handleGet = () => {
    dispatch(getAllParticipants({token}))
  }
  
  return (
    <Container>
      <Button
        id="Cancel-resetPassword"
        onClick={handleGet}
        variant="outlined"
        color="primary"
      >get</Button>
      <TableForm />
    </Container>
  );
};

export default Gregor;
