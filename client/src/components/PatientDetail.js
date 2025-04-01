import React, { useState, useEffect, useCallback } from 'react';
import { Card, Descriptions, Spin, message, Button, Tabs, Divider, Row, Col } from 'antd';
import axios from 'axios';
import moment from 'moment';
import PatientEdit from './PatientEdit';
import ReferralEdit from './ReferralEdit';
import PatientNotes from './PatientNotes';

const { TabPane } = Tabs;

const PatientDetail = ({ patientId }) => {
  const [patient, setPatient] = useState(null);
  const [referral, setReferral] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editingPatientId, setEditingPatientId] = useState(null);
  const [referralEditModalVisible, setReferralEditModalVisible] = useState(false);
  const [editingReferralId, setEditingReferralId] = useState(null);
  const [activeTab, setActiveTab] = useState("1");

  const DECISION_CHOICES = {
    "tier_1": "Reject: chart review and feedback",
    "tier_2": "Accept: remote/televisit only",
    "tier_3": "Accept: in-person evaluation",
    "tier_4": "Accept: research basis evaluation",
  };

  const fetchPatientData = useCallback(async () => {
    try {
      const response = await axios.get(`/api/private/v1/patients/${patientId}/`, {
        headers: { Authorization: `Token ${localStorage.getItem('authToken')}` }
      });
      setPatient(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching patient data:', error);
      message.error('Failed to fetch patient data');
      setLoading(false);
    }
  }, [patientId]);

  const fetchReferrals = useCallback(async () => {
    try {
      const response = await axios.get(`/api/private/v1/referrals/${patientId}/`, {
        headers: { Authorization: `Token ${localStorage.getItem('authToken')}` }
      });
      setReferral(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching referrals:', error);
      message.error('Failed to fetch referral data');
      setLoading(false);
    }
  }, [patientId]);

  useEffect(() => {
    fetchPatientData();
    fetchReferrals();
  }, [fetchPatientData, fetchReferrals]);

  if (loading) {
    return <Spin size="large" />;
  }

  if (!patient) {
    return <div>Patient not found</div>;
  }

  const handleEdit = (patientId) => {
    setEditingPatientId(patientId);
    setEditModalVisible(true);
  };

  const handleEditCancel = () => {
    setEditModalVisible(false);
    setEditingPatientId(null);
  };

  const handleEditSave = async (updatedPatient) => {
    await fetchPatientData();
    setEditModalVisible(false);
    setEditingPatientId(null);
  };

  const handleReferralEdit = () => {
    setReferralEditModalVisible(true);
  };

  const handleReferralEditCancel = () => {
    setReferralEditModalVisible(false);
    setEditingReferralId(null);
  };

  const handleReferralEditSave = async (updatedReferral) => {
    await fetchReferrals();
    setReferralEditModalVisible(false);
    setEditingReferralId(null);
  };

  const handleTabChange = (key) => {
    setActiveTab(key);
  };

  return (
    <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', height: 'calc(100vh - 64px)' }}>
      <Row gutter={16}>
        <Col span={18}>
          <Tabs defaultActiveKey="1" onChange={handleTabChange} style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <TabPane tab="Patient Details" key="1" style={{ flex: 1, overflow: 'auto' }}>
              <Card
                title={
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span><h3>{`${patient.first_name} ${patient.last_name}`}</h3></span>
                  </div>
                }
              >
                <Descriptions bordered column={2}>
                  <Descriptions.Item label="Date of Birth">
                    {moment(patient.date_of_birth).format('MMMM D, YYYY')}
                  </Descriptions.Item>
                  <Descriptions.Item label="Sex">{patient.sex_display}</Descriptions.Item>
                  <Descriptions.Item label="UCI MRN">{patient.uci_mrn || 'N/A'}</Descriptions.Item>
                  <Descriptions.Item label="CHOC MRN">{patient.choc_mrn || 'N/A'}</Descriptions.Item>
                  <Descriptions.Item label="UDN ID">{patient.udn_id}</Descriptions.Item>
                  <Descriptions.Item label="Race">{patient.race_display}</Descriptions.Item>
                  <Descriptions.Item label="Ethnicity">{patient.ethnicity_display}</Descriptions.Item>
                  <Descriptions.Item label="Created Date">
                    {moment(patient.created_dt).format('MMMM D, YYYY, h:mm a')}
                  </Descriptions.Item>
                </Descriptions>
              </Card>
            </TabPane>
            <TabPane tab="Referral Details" key="2" style={{ flex: 1, overflow: 'auto' }}>
              <Card
                title={
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span><h3>{`${patient.first_name} ${patient.last_name}`}</h3></span>
                  </div>
                }
              >
                <Descriptions bordered column={2}>
                  <Descriptions.Item label="Institution">{referral?.institution || 'N/A'}</Descriptions.Item>
                  <Descriptions.Item label="Date Referred">{referral?.dt_referred ? moment(referral.dt_referred).format('MMMM D, YYYY') : 'N/A'}</Descriptions.Item>
                  <Descriptions.Item label="Referred By">{referral?.referred_by || 'N/A'}</Descriptions.Item>
                  <Descriptions.Item label="Created Date">{referral?.created_dt ? moment(referral.created_dt).format('MMMM D, YYYY') : 'N/A'}</Descriptions.Item>
                  <Descriptions.Item label="Demographics Completion Date">{referral?.demographics_completion_dt ? moment(referral.demographics_completion_dt).format('MMMM D, YYYY') : 'N/A'}</Descriptions.Item>
                  <Descriptions.Item label="Estimated Review Date">{referral?.estimated_review_dt ? moment(referral.estimated_review_dt).format('MMMM D, YYYY') : 'N/A'}</Descriptions.Item>
                  <Descriptions.Item label="Records Requested">{referral?.records_requested ? 'Yes' : 'No'}</Descriptions.Item>
                  <Descriptions.Item label="Records Reviewed">{referral?.records_reviewed ? 'Yes' : 'No'}</Descriptions.Item>
                  <Descriptions.Item label="Review Complete">{referral?.review_complete ? 'Yes' : 'No'}</Descriptions.Item>
                  <Descriptions.Item label="Case Review Form Complete">{referral?.case_review_form_complete ? 'Yes' : 'No'}</Descriptions.Item>
                  <Descriptions.Item label="Case Review Form Completed By">{referral?.case_review_form_completed_by || 'N/A'}</Descriptions.Item>
                  <Descriptions.Item label="Decision">{referral?.decision ? DECISION_CHOICES[referral.decision] : 'N/A'}</Descriptions.Item>
                  <Descriptions.Item label="Rejection Letter Review">{referral?.rejection_letter_review ? 'Yes' : 'No'}</Descriptions.Item>
                  <Descriptions.Item label="Rejection Letter Complete">{referral?.rejection_letter_complete ? 'Yes' : 'No'}</Descriptions.Item>
                  <Descriptions.Item label="Testing" span={2}>{referral?.testing || 'N/A'}</Descriptions.Item>
                  <Descriptions.Item label="Specialist Evaluations" span={2}>{referral?.specialist_evaluations || 'N/A'}</Descriptions.Item>
                  <Descriptions.Item label="Result" span={2}>{referral?.result || 'N/A'}</Descriptions.Item>
                </Descriptions>
              </Card>
            </TabPane>
          </Tabs>
          <Divider />
          <div style={{ display: 'flex', justifyContent: 'flex-end', padding: '16px 0' }}>
            {activeTab === "1" && (
              <Button
                type="primary"
                onClick={() => handleEdit(patientId)}
              >
                Edit Patient
              </Button>
            )}
            {activeTab === "2" && (
              <Button
                type="primary"
                onClick={() => handleReferralEdit(referral?.id)}
              >
                Edit Referral
              </Button>
            )}
          </div>
        </Col>
        <Col span={6}>
          <PatientNotes patientId={patientId} />
        </Col>
      </Row>
      <PatientEdit
        visible={editModalVisible}
        onCancel={handleEditCancel}
        onSave={handleEditSave}
        patientId={editingPatientId}
        patientData={patient}
      />
      <ReferralEdit
        visible={referralEditModalVisible}
        onCancel={handleReferralEditCancel}
        onSave={handleReferralEditSave}
        referralId={patientId}
      />
    </div>
  );
};

export default PatientDetail;