import React from 'react';
import { Form, Button, message } from 'antd';
import PatientForm from './PatientForm';

const AddPatient = ({ onSubmit }) => {
  const [form] = Form.useForm();

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const formattedValues = {
        ...values,
        date_of_birth: values.date_of_birth.format('YYYY-MM-DD'),
      };
      await onSubmit(formattedValues);
      form.resetFields();
    } catch (error) {
      console.error('Validation failed:', error);
      message.error('Please fill in all required fields correctly');
    }
  };

  return (
    <div>
      <PatientForm form={form} />
      <Form.Item>
        <Button type="primary" onClick={handleSubmit}>
          Add Patient
        </Button>
      </Form.Item>
    </div>
  );
};

export default AddPatient;
