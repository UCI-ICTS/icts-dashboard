// src/pages/SummaryPage.js

import { Card, Row, Col, Typography, Tooltip, Button } from "antd";
import { UserOutlined, MessageOutlined, SolutionOutlined, CheckCircleTwoTone, WarningTwoTone } from "@ant-design/icons";
import { useDispatch, useSelector } from "react-redux";
import { getAllTables, updateTable, createEntry } from "../slices/dataSlice";

const { Title } = Typography;
const SummaryPage = () => {
  const dispatch = useDispatch();
  const data = useSelector(state => state.data)
  const biobank = useSelector(state => state.data.biobank_entries)
  

  // Count and format occurrences of values in an array of objects by a specified key.
  // Allows optional removal of specific words before formatting.
  function countByKey(data, key, wordsToRemove = []) {
    return data.reduce((acc, item) => {
      const value = item[key] || 'Unknown';
      const formatted = value
        .split('_')
        .filter(word => !wordsToRemove.includes(word.toLowerCase()))
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
      acc[formatted] = (acc[formatted] || 0) + 1;
      return acc;
    }, {});
  }

  //  Diff two count maps and return unified comparison with delta.
  function diffCounts(experiments, alignments) {
    const labels = new Set([...Object.keys(experiments), ...Object.keys(alignments)]);
    return Array.from(labels).map(label => {
      const exp = experiments[label] || 0;
      const aln = alignments[label] || 0;
      return {
        label,
        experiments: exp,
        alignments: aln,
        delta: exp - aln,
      };
    });
  }

  const biobankCounts = countByKey(biobank, 'status');
  const solvedStatusCounts = countByKey(data.participants, 'solve_status');
  const experimentCounts = countByKey(data.experiments, 'table_name', "experiment")
  const alignedCounts = countByKey(data.aligned, 'table_name', "aligned")
  const diff = diffCounts(experimentCounts, alignedCounts);
  
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
            <p>Total Analytes: {data.analytes.length}</p>
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
        {/* Solve Status Card */}
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
      <Row><br/></Row>
      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
         {/* Sequencing Experiments Card */}
          <Card title="Sequencing Experiments" bordered>
            <SolutionOutlined style={{ fontSize: "24px" }} />
            {/* Render status counts */}
            {Object.entries(experimentCounts).map(([status, count]) => (
                <p key={status}>
                <strong>{status}:</strong> {count}
                </p>
            ))}
          </Card>
        </Col>
        <Col xs={24} md={8}>
        {/* Aligned Experiments Card */}
          <Card title="Aligned Experiments" bordered>
            <SolutionOutlined style={{ fontSize: "24px" }} />
            {/* Render status counts */}
            {Object.entries(alignedCounts).map(([status, count]) => (
                <p key={status}>
                <strong>{status}:</strong> {count}
                </p>
            ))}
          </Card>
        </Col>
        <Col xs={24} md={8}>
        {/* Comparison Card */}
        <Card title="Sequencing vs Alignment Counts" bordered>
            {diff.map(({ label, experiments, alignments, delta }) => (
              <p key={label}>
                <strong>{label}:</strong> {experiments} exp, {alignments} aln{' '}
                {delta === 0 ? (
                  <CheckCircleTwoTone twoToneColor="#52c41a" />
                ) : (
                  <WarningTwoTone twoToneColor="#faad14" />
                )}
              </p>
            ))}
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default SummaryPage;