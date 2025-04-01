import React, { useState, useEffect } from 'react';
import { Table, Space, Button, message, Modal } from 'antd';
import axios from 'axios';
import moment from 'moment';
import AddPatient from './AddPatient';

const PatientList = ({ onSelectPatient }) => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addModalVisible, setAddModalVisible] = useState(false);

  useEffect(() => {
    // fetchPatients();
    console.log("fetchPatients")
  }, []);

  const fetchPatients = async () => {
    try {
      const response = await axios.get('/api/private/v1/patients/');
      setPatients(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching patients:', error);
      setLoading(false);
      message.error('Failed to fetch patients');
    }
  };

  const handleAddPatient = async (patientData) => {
    try {
      const response = await axios.post('/api/private/v1/patients/', patientData);
      setPatients([...patients, response.data]);
      setAddModalVisible(false);
      message.success('Patient added successfully');
    } catch (error) {
      console.error('Error adding patient:', error);
      message.error('Failed to add patient');
    }
  };

  const columns = [
    {
      title: 'First Name',
      dataIndex: 'first_name',
      key: 'first_name',
    },
    {
      title: 'Last Name',
      dataIndex: 'last_name',
      key: 'last_name',
    },
    {
      title: 'Date of Birth',
      dataIndex: 'date_of_birth',
      key: 'date_of_birth',
    },
    {
      title: 'Sex',
      dataIndex: 'sex_display',
      key: 'sex',
    },
    {
      title: 'UCI MRN',
      dataIndex: 'uci_mrn',
      key: 'uci_mrn',
    },
    {
      title: 'CHOC MRN',
      dataIndex: 'choc_mrn',
      key: 'choc_mrn',
    },
    {
      title: 'UDN ID',
      dataIndex: 'udn_id',
      key: 'udn_id',
    },
    {
      title: 'Race',
      dataIndex: 'race_display',
      key: 'race',
    },
    {
      title: 'Ethnicity',
      dataIndex: 'ethnicity_display',
      key: 'ethnicity',
    },
    {
      title: 'Created',
      dataIndex: 'created_dt',
      key: 'created_dt',
      render: (date) => date ? moment(date).format('MMMM D, YYYY') : 'N/A',
    },
    {
      title: 'Estimated Review Date', //this needs to be correctly defined in the Serializers and Views to correctly pull the data from referrals
      dataIndex: 'estimated_review_dt',
      key: 'estimated_review_dt',
      render: (date) => date ? moment(date).format('MMMM D, YYYY') : 'N/A',
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button onClick={() => onSelectPatient(record.id)}>View Details</Button>
        </Space>
      ),
    },
  ];

  return (
    <>
      <Button
        onClick={() => setAddModalVisible(true)}
        type="primary"
        style={{ marginBottom: 16 }}
      >
        Add New Patient
      </Button>
      <Table
        columns={columns}
        dataSource={patients}
        loading={loading}
        rowKey="id"
      />
      <Modal
        title="Add New Patient"
        open={addModalVisible}
        onCancel={() => setAddModalVisible(false)}
        footer={null}
      >
        <AddPatient onSubmit={handleAddPatient} />
      </Modal>
    </>
  );
};

export default PatientList;