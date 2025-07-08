// src/pages/SummaryPage.js

import { Card, Row, Col, Typography, Tooltip, Button } from "antd";
import { UserOutlined, MessageOutlined, SolutionOutlined } from "@ant-design/icons";
import { useDispatch, useSelector } from "react-redux";
import { getAllTables, updateTable, addTable } from "../slices/dataSlice";

const { Title } = Typography;
const SummaryPage = () => {
  const dispatch = useDispatch();
  const data = useSelector(state => state.data)
  const biobank = useSelector(state => state.data.biobank_entries)
  
  function countByKey(data, key) {
    return data.reduce((acc, item) => {
      const value = item[key] || 'Unknown';
      acc[value] = (acc[value] || 0) + 1;
      return acc;
    }, {});
  }
  
  const biobankCounts = countByKey(biobank, 'status');
  const solvedStatusCounts = countByKey(data.participants, 'solve_status');
  console.log(biobankCounts, solvedStatusCounts);

  
  return(
    <div style={{ padding: 20 }}>
      <Row gutter={[16, 16]}>
        <Tooltip title="Fetch or refresh the table data">
            <Button
              onClick={() => dispatch(getAllTables())}
              type="primary"
            >
              Fetch/Refresh data
            </Button>
          </Tooltip>
      </Row>
      <Title level={3}>Project Status Summary</Title>
      <Row gutter={[16, 16]}>
        {/* participants Card */}
        <Col xs={24} md={8}>
          <Card title="Participants" bordered>
            <UserOutlined style={{ fontSize: "24px" }} />
            <p>Total participants: {data.participants.length}</p>
            <p>Families Enroled: {data.families.length}</p>
            <p>Samples Sequenced: {data.aligned.length}</p>
          </Card>
        </Col>

        {/* Biobank Entries Card */}
        <Col xs={24} md={8}>
          <Card title="Biobank Entries" bordered>
            <MessageOutlined style={{ fontSize: "24px" }} />
            <p>Total Biobank Entries: {biobank.length}</p>

            {/* Render status counts */}
            {Object.entries(biobankCounts).map(([status, count]) => (
                <p key={status}>
                <strong>{status}:</strong> {count}
                </p>
            ))}
          </Card>
        </Col>
        {/* Follow Up Card */}
        <Col xs={24} md={8}>
          <Card title="Solve Status" bordered>
            <SolutionOutlined style={{ fontSize: "24px" }} />
          {/* Render status counts */}
            {Object.entries(solvedStatusCounts).map(([status, count]) => (
                <p key={status}>
                <strong>{status}:</strong> {count}
                </p>
            ))}
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default SummaryPage;