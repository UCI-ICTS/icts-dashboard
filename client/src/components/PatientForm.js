import React from 'react';
import { Form, Input, DatePicker, Select } from 'antd';
import moment from 'moment';

const { Option } = Select;

const PatientForm = ({ form, initialValues = {} }) => {
  const SEX_CHOICES = {
    "male": "Male",
    "female": "Female",
    "unknown": "Unknown",
  };

  const RACE_CHOICES = {
    "american_indian_or_alaska_native": "American Indian or Alaska Native",
    "asian": "Asian",
    "black_or_african_american": "Black or African American",
    "middle_eastern_or_north_african": "Middle Eastern or North African",
    "native_hawaiian_or_other_pacific_islander": "Native Hawaiian or Other Pacific Islander",
    "white": "White",
  };

  const ETHNICITY_CHOICES = {
    "hispanic_or_latino": "Hispanic or Latino",
    "not_hispanic_or_latino": "Not Hispanic or Latino",
  };

  return (
    <Form form={form} layout="vertical" initialValues={{
      ...initialValues,
      date_of_birth: initialValues.date_of_birth ? moment(initialValues.date_of_birth) : undefined,
    }}>
      <Form.Item name="first_name" label="First Name" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <Form.Item name="last_name" label="Last Name" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <Form.Item name="date_of_birth" label="Date of Birth" rules={[{ required: true }]}>
        <DatePicker />
      </Form.Item>
      <Form.Item name="sex" label="Sex" rules={[{ required: true }]}>
        <Select>
          {Object.entries(SEX_CHOICES).map(([value, label]) => (
            <Option key={value} value={value}>{label}</Option>
          ))}
        </Select>
      </Form.Item>
      <Form.Item
        name="uci_mrn"
        label="UCI MRN"
      >
        <Input />
      </Form.Item>
      <Form.Item
        name="choc_mrn"
        label="CHOC MRN"
      >
        <Input />
      </Form.Item>
      <Form.Item name="udn_id" label="UDN ID" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <Form.Item name="race" label="Race" rules={[{ required: true }]}>
        <Select>
          {Object.entries(RACE_CHOICES).map(([value, label]) => (
            <Option key={value} value={value}>{label}</Option>
          ))}
        </Select>
      </Form.Item>
      <Form.Item name="ethnicity" label="Ethnicity" rules={[{ required: true }]}>
        <Select>
          {Object.entries(ETHNICITY_CHOICES).map(([value, label]) => (
            <Option key={value} value={value}>{label}</Option>
          ))}
        </Select>
      </Form.Item>
    </Form>
  );
};

export default PatientForm;
