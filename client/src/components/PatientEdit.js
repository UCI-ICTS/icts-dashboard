import React, { useState, useEffect, useCallback } from 'react';
import { Modal, Form, Button, message } from 'antd';
import axios from 'axios';
import PatientForm from './PatientForm';
import moment from 'moment';

const PatientEdit = ({ visible, onCancel, onSave, patientId }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [initialValues, setInitialValues] = useState({});

  const fetchPatientData = useCallback(async (id) => {
    try {
      const response = await axios.get(`/api/private/v1/patients/${id}/`);
      setInitialValues(response.data);
    } catch (error) {
      console.error('Error fetching patient data:', error);
      message.error('Failed to fetch patient data');
    }
  }, []);

  useEffect(() => {
    if (visible && patientId) {
      fetchPatientData(patientId);
    }
  }, [visible, patientId, fetchPatientData]);

  useEffect(() => {
    if (Object.keys(initialValues).length > 0) {
      form.setFieldsValue({
        ...initialValues,
        date_of_birth: initialValues.date_of_birth ? moment(initialValues.date_of_birth) : null,
      });
    }
  }, [initialValues, form]);

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);
      const dataToSend = {
        ...values,
        date_of_birth: values.date_of_birth.format('YYYY-MM-DD'),
        uci_mrn: values.uci_mrn || null,
        choc_mrn: values.choc_mrn || null,
      };
      const response = await axios.put(`/api/private/v1/patients/${patientId}/`, dataToSend);
      setLoading(false);
      onSave(response.data);
      message.success('Patient updated successfully');
    } catch (error) {
      console.error('Error updating patient:', error);
      setLoading(false);
      if (error.response && error.response.status === 400) {
        message.error('Validation error: ' + error.response.data.detail);
      } else {
        message.error('Failed to update patient');
      }
    }
  };

  return (
    <Modal
      open={visible}
      title="Edit Patient"
      onCancel={onCancel}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          Cancel
        </Button>,
        <Button key="save" type="primary" loading={loading} onClick={handleSave}>
          Save
        </Button>,
      ]}
    >
      <PatientForm form={form} initialValues={initialValues} />
    </Modal>
  );
};

export default PatientEdit;
