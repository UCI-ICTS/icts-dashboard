import React from 'react';
import { Form, Input, DatePicker, Select, Checkbox, Row, Col } from 'antd';
import moment from 'moment';

const { Option } = Select;
const { TextArea } = Input;

const ReferralForm = ({ form, initialValues = {} }) => {
  const INSTITUTION_CHOICES = {
    "choc": "CHOC",
    "uci": "UCI",
  };

  const DECISION_CHOICES = {
    "tier_1": "Reject: chart review and feedback",
    "tier_2": "Accept: remote/televisit only",
    "tier_3": "Accept: in-person evaluation",
    "tier_4": "Accept: research basis evaluation",
  };

  return (
    <Form form={form} layout="vertical" initialValues={{
      ...initialValues,
      dt_referred: initialValues.dt_referred ? moment(initialValues.dt_referred) : null,
      demographics_completion_dt: initialValues.demographics_completion_dt ? moment(initialValues.demographics_completion_dt) : null,
      estimated_review_dt: initialValues.estimated_review_dt ? moment(initialValues.estimated_review_dt) : null,
    }}>
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name="institution" label="Institution" rules={[{ required: true }]}>
            <Select>
              {Object.entries(INSTITUTION_CHOICES).map(([value, label]) => (
                <Option key={value} value={value}>{label}</Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name="dt_referred" label="Date Referred" rules={[{ required: true }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name="referred_by" label="Referred By">
            <Input />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name="demographics_completion_dt" label="Demographics Completion Date">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name="estimated_review_dt" label="Estimated Review Date">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name="case_review_form_completed_by" label="Case Review Form Completed By">
            <Input />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name="case_review_form_complete" valuePropName="checked">
            <Checkbox>Case Review Form Complete</Checkbox>
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name="review_complete" valuePropName="checked">
            <Checkbox>Review Complete</Checkbox>
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name="records_requested" valuePropName="checked">
            <Checkbox>Records Requested</Checkbox>
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name="records_reviewed" valuePropName="checked">
            <Checkbox>Records Reviewed</Checkbox>
          </Form.Item>
        </Col>
      </Row>

      <Form.Item name="testing" label="Testing">
        <TextArea rows={4} />
      </Form.Item>

      <Form.Item name="specialist_evaluations" label="Specialist Evaluations">
        <TextArea rows={4} />
      </Form.Item>

      <Form.Item name="result" label="Result">
        <TextArea rows={4} />
      </Form.Item>

            <Form.Item name="decision" label="Decision">
        <Select>
          {Object.entries(DECISION_CHOICES).map(([value, label]) => (
            <Option key={value} value={value}>{label}</Option>
          ))}
        </Select>
      </Form.Item>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name="rejection_letter_review" valuePropName="checked">
            <Checkbox>Rejection Letter Review</Checkbox>
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name="rejection_letter_complete" valuePropName="checked">
            <Checkbox>Rejection Letter Complete</Checkbox>
          </Form.Item>
        </Col>
      </Row>

    </Form>
  );
};

export default ReferralForm;