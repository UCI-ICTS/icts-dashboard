import React, { useState, useEffect, useCallback } from 'react';
import { Modal, Form, Button, message } from 'antd';
import axios from 'axios';
import ReferralForm from './ReferralForm';
import moment from 'moment';

const ReferralEdit = ({ visible, onCancel, onSave, referralId }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [initialValues, setInitialValues] = useState({});

  const fetchReferralData = useCallback(async (id) => {
    try {
      const response = await axios.get(`/api/private/v1/referrals/${id}/`);
      setInitialValues(response.data);
    } catch (error) {
      console.error('Error fetching referral data:', error);
      message.error('Failed to fetch referral data');
    }
  }, []);

  useEffect(() => {
    if (visible && referralId) {
      fetchReferralData(referralId);
    }
  }, [visible, referralId, fetchReferralData]);

  useEffect(() => {
    if (Object.keys(initialValues).length > 0) {
      form.setFieldsValue({
        ...initialValues,
        dt_referred: initialValues.dt_referred ? moment(initialValues.dt_referred) : null,
        demographics_completion_dt: initialValues.demographics_completion_dt ? moment(initialValues.demographics_completion_dt) : null,
        estimated_review_dt: initialValues.estimated_review_dt ? moment(initialValues.estimated_review_dt) : null,
      });
    }
  }, [initialValues, form]);

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);
      const dataToSend = {
        ...values,
        dt_referred: values.dt_referred ? values.dt_referred.format('YYYY-MM-DD') : null,
        demographics_completion_dt: values.demographics_completion_dt ? values.demographics_completion_dt.format('YYYY-MM-DD') : null,
        estimated_review_dt: values.estimated_review_dt ? values.estimated_review_dt.format('YYYY-MM-DD') : null,
      };
      const response = await axios.put(`/api/private/v1/referrals/${referralId}/`, dataToSend);
      setLoading(false);
      onSave(response.data);
      message.success('Referral updated successfully');
    } catch (error) {
      console.error('Error updating referral:', error);
      setLoading(false);
      if (error.response && error.response.status === 400) {
        message.error('Validation error: ' + error.response.data.detail);
      } else {
        message.error('Failed to update referral');
      }
    }
  };

  return (
    <Modal
      open={visible}
      title="Edit Referral"
      onCancel={onCancel}
      width={800}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          Cancel
        </Button>,
        <Button key="save" type="primary" loading={loading} onClick={handleSave}>
          Save
        </Button>,
      ]}
    >
      <ReferralForm form={form} initialValues={initialValues} />
    </Modal>
  );
};

export default ReferralEdit;