// src/pages/RAGHPO.js


import { useEffect, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { 
  Alert,
  Button,
  Col,
  Form,
  Input,
  Layout,
  Row,
  Select,
  Space,
  Spin,
  Table,
  Tooltip,
  Typography,
} from "antd";
import { extractPhenotypes } from "../slices/dataSlice";


const { Header } = Layout;
const { Title } = Typography;
const { TextArea } = Input;
const { Column, ColumnGroup } = Table;

const RAGHPO = () => {
  const dispatch = useDispatch();
  const isLoading = useSelector((state) => state.data.status);
  const rag_hpos = useSelector((state) => state.data.rag_hpos);
  
  const onFinish = (userText) => {
    console.log(userText)
    dispatch(extractPhenotypes(userText))
  };

  const onFinishFailed = (errorInfo) => {
    console.log('Failed:', errorInfo);
  };

  useEffect(()=> {
    console.log(isLoading)
  },[isLoading])

  return (
    <Layout className="layout-container">
      <Header className="primary-header">
        <Title className="primary-title">RAG-HPO</Title>
      </Header>
      <Spin tip="Extracting HPOs from phenotype description...This may take a while" spinning={isLoading === "loading"}>
        <Form
          name="phenotype_text"
          onFinish={onFinish}
          onFinishFailed={onFinishFailed}
          layout="vertical"
          rules={[{ required: true, message: 'Please enter your message!' }]}
        >
          <Form.Item
            name="userText"
          >
            <TextArea
              className="text-area-input"
              rows={3}
              allowClear
              placeholder="Enter your message here..." 
            /> 
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" className="logout-button">
              Submit
            </Button>
          </Form.Item>
        </Form>
        <Table dataSource={rag_hpos} className="table">
          <ColumnGroup title="LLM Choice">
            <Column 
              title="HPO Term" 
              dataIndex="hpo_id" 
              render={(text, record) => {
                return(<>{record.choice.hpo_id}</>)
              }}
            />
            <Column 
              title="Label" 
              dataIndex="label" 
              render={(text, record) => {
                return(<>{record.choice.label}</>)
              }}
            />
            <Column 
              title="Score" 
              dataIndex="score" 
              render={(text, record) => {
                return(<>{record.choice.score}</>)
              }}
            />
            <Column 
              title="Rank" 
              dataIndex="rank" 
              render={(text, record) => {
                return(<>{record.choice.rank}</>)
              }}
            />
            <Column 
              title="Source" 
              dataIndex="source" 
              render={(text, record) => {
                return(<>{record.choice.source}</>)
              }}
            />
            <Column 
              title="Reason" 
              dataIndex="reason" 
              render={(text, record) => {
                return(<>{record.choice.reason}</>)
              }}
            />
          </ColumnGroup>
          <Column 
            title="Extracted Phrase" 
            dataIndex="phrase" 
            key="phrase"
          />
        </Table>
      </Spin>
    </Layout>
  )
}

export default RAGHPO;