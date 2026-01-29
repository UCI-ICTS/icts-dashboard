// src/pages/RAGHPO.js


import { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { 
  Alert,
  Button,
  Col,
  Form,
  Input,
  Layout,
  Modal,
  Row,
  Select,
  Space,
  Spin,
  Table,
  Tooltip,
  Typography,
} from "antd";
import { extractPhenotypes, createEntry, clearRagHpos, replaceRagHpoChoice } from "../slices/dataSlice";
import { HPODownloadModal, PhenotypeImportFormModal } from "../components/Modals"
import { dataDownload } from "../utils/utilitiyFunctions"; 

const { Header } = Layout;
const { Title } = Typography;
const { TextArea } = Input;
const { Column, ColumnGroup } = Table;

const RAGHPO = () => {
  const [form] = Form.useForm();
  const dispatch = useDispatch();
  const {rag_hpos, participants, status} = useSelector((state) => state.data);
  const [expandedRowKey, setExpandedRowKey] = useState(null);
  const [actionsOpen, setActionsOpen] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  const [flattenedRows, setFlattenedRows] = useState([]);
  const [importParticipantId, setImportParticipantId] = useState(null);

  const handleSubmit = ({ action, exportFormat, participant }) => {
    const filename = "rag_hpo_export";
    if (exportFormat === "JSON" && action === "download") {
      // Full state export
      dataDownload({
        filename,
        displayData: rag_hpos,
        visibleKeys: null, // Will use all keys
        exportFormat,
      });
    } else {
      // Flatten visible table rows (LLM choice only)
      const flattenedData = rag_hpos.map((row) => ({
        hpo_id: row.choice?.hpo_id,
        label: row.choice?.label,
        score: row.choice?.score,
        rank: row.choice?.rank,
        source: row.choice?.source,
        reason: row.choice?.reason,
        phrase: row.phrase,
      }));
      
      if (action === "import") {
        setImportParticipantId(participant);
        setFlattenedRows(rag_hpos.map((row) => ({
          ...row.choice,
          phrase: row.phrase
        })).filter((row) => row.source !== "llm-null"));
        setImportOpen(true);
      } else {
        const visibleKeys = ["hpo_id","label","score","rank","source","reason","phrase"];
        dataDownload({
          filename,
          displayData: flattenedData,
          visibleKeys,
          exportFormat,
        });
      }
    }
  };

  const handleExpand = (expanded, record) => {
    setExpandedRowKey(expanded ? record.key : null);
  };
  
  const handleReplace = (candidate) => {
    if (!expandedRowKey) return;

    const newChoice = {
      hpo_id: candidate.hpo_id,
      label: candidate.label,
      score: candidate.score,
      rank: candidate.rank,
      reason: "User selected",
      source: "user-select"
    }
    dispatch(replaceRagHpoChoice({
      id: expandedRowKey,
      choice: newChoice,
    }))

    setExpandedRowKey(null); // collapse row after replace
  }

  const onFinish = (userText) => {
    dispatch(extractPhenotypes(userText))
  };

  const onFinishFailed = (errorInfo) => {
    console.log('Failed:', errorInfo);
  };
  
  const expandedRowRender = (record) => (
    <Table
      rowKey={(caondidate) => caondidate.hpo_id}
      dataSource={Array.isArray(record.candidates) ? record.candidates : []} 
      columns={candidateColumns} 
      pagination={false}
    />
  );

  const candidateColumns =  [
    { title: "HPO Term",dataIndex: "hpo_id",key: "hpo_id" },
    { title: "Label",dataIndex: "label",key: "label" },
    { title: "score",dataIndex: "score",key: "score" },
    { title: "rank", dataIndex: "rank", key: "rank" },
    { 
      title: "Replace",
      dataIndex: "replace",
      key: "replace",
      render: (_, candidate, index) => ( 
      <Tooltip title="Replace LLM choice with this candidate">
        <Button
          className="replace-button"
          danger
          size="small"
          onClick={() => handleReplace(candidate, index)}
        >Replace</Button>
    </Tooltip>)
    }
    ]
  
  return (
    <Layout className="layout-container">
      <Header className="primary-header">
        <Title className="primary-title">RAG-HPO</Title>
      </Header>
      <Spin tip="Extracting HPOs from phenotype description...This may take a while" spinning={status === "loading"}>
        <Form
          form={form}
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
            <Space>
              {status === "fulfilled"  && rag_hpos.length > 0 ? (
                <Button 
                  type="primary" 
                  className="logout-button"
                  onClick={() => setActionsOpen(true)} 
                >
                  Import/Download
                </Button>
              ) : (
                <Button type="primary" htmlType="submit" className="logout-button">
                  Submit
                </Button>
              )}
              <Button
                danger
                type="default"
                className="logout-button"
                onClick={() => {
                  dispatch(clearRagHpos());
                  form.resetFields();
                }}
              >Clear</Button>
            </Space>
          </Form.Item>
        </Form>
        <Table
          rowKey={(record) => record.id}
          className="table"
          dataSource={
            (Array.isArray(rag_hpos)
             ? rag_hpos 
             : []).map((item, index) => ({ ...item, key: item.id || index })
            ) 
          }
          scroll
          expandable={{
            expandedRowRender,
            expandedRowKeys: expandedRowKey ? [expandedRowKey] : [],
            onExpand: handleExpand,
          }}
        >
          <ColumnGroup title="LLM Choice">
            <Column 
              title="HPO Term" 
              dataIndex="hpo_id" 
              render={(text, record) => {
                return(<>{record.choice?.hpo_id ?? "-"}</>)
              }}
            />
            <Column 
              title="Label" 
              dataIndex="label" 
              render={(text, record) => {
                return(<>{record.choice?.label ?? "-"}</>)
              }}
            />
            <Column 
              title="Score" 
              dataIndex="score" 
              render={(text, record) => {
                return(<>{record.choice?.score ?? "-"}</>)
              }}
            />
            <Column 
              title="Rank" 
              dataIndex="rank" 
              render={(text, record) => {
                return(<>{record.choice?.rank ?? "-"}</>)
              }}
            />
            <Column 
              title="Source" 
              dataIndex="source" 
              render={(text, record) => {
                return(<>{record.choice?.source ?? "-"}</>)
              }}
            />
            <Column 
              title="Reason" 
              dataIndex="reason" 
              render={(text, record) => {
                return(<>{record.choice?.reason ?? "-"}</>)
              }}
            />
          </ColumnGroup>
          <Column 
            title="Extracted Phrase" 
            dataIndex="phrase" 
            key="phrase"
          />
        </Table>
          <HPODownloadModal 
            visible={actionsOpen}
            onCancel={() => setActionsOpen(false)}
            handleSubmit={handleSubmit}
          />

        <PhenotypeImportFormModal
          visible={importOpen}
          onCancel={() => setImportOpen(false)}
          onSubmit={(finalEntries) => {
            dispatch(createEntry( {table:"phenotype", data:finalEntries})); 
            setImportOpen(false);
            form.resetFields(); // Clear form
            dispatch(clearRagHpos()); // Clear table (rag_hpos)
          }}
          flattenedData={flattenedRows}
          participantId={importParticipantId}
        />
      </Spin>
    </Layout>
  )
}

export default RAGHPO;