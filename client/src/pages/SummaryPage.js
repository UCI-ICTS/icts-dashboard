// src/pages/SummaryPage.js

import axios from "axios";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, Row, Col, Layout, Typography, Tooltip, Button, Alert } from "antd";
import { HomeOutlined, CheckCircleTwoTone, WarningTwoTone, DatabaseOutlined } from "@ant-design/icons";
import SiteFooter from "../components/SiteFooter";
import SummaryPieChart from "../components/SummaryPieChart";
import SummaryCard from "../components/SummaryCard";
import { primaryBiosample } from "../utils/schemaAndTables";
import "../App.css";

const APIDB = process.env.REACT_APP_APIDB;
const { Header, Content } = Layout;
const { Title } = Typography;

const SummaryPage = () => {
  const navigate = useNavigate();
  const [summary, setSummary] = useState();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSummary = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${APIDB}/api/search/summary/`);
      setSummary(response.data);
      setError(null);
    } catch (err) {
      console.error("Error loading summary:", err);
      setError("Failed to load summary data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  const get = (obj, key, fallback = "-") =>
    loading ? "Loading..." : obj?.[key] ?? fallback;
  
  const kindredData = summary?.kindred
    ? Object.entries(summary.kindred).map(([label, value]) => ({ label, value }))
    : [];
  
  const solveStatusData = summary?.solve_status_counts
    ? Object.entries(summary.solve_status_counts).map(([label, value]) => ({label,value,}))
    : [];
  
  const biobankItems = [
    { label: "Total biobank entries", value: summary?.biobank },
    { label: "Biobank statuses", value: "" },
    ...Object.entries(summary?.biobank_status_counts || {}).map(([status, count]) => ({
      label: status,
      value: count,
      indent: true,
      // icon: <CaretRightOutlined />
    })),
  ];

  const analyteItems = [
    { label: "Total analyte entries", value: summary?.analytes },
    { label: "Analyte statuses", value: "" },
    ...Object.entries(summary?.analyte_biosample_counts || {}).map(([status, count]) => ({
      label: `${status} ${primaryBiosample[status] || ""}`.trim(),
      value: count,
      indent: true,
      // icon: <CaretRightOutlined />
    })),
  ];

  const findingsItems = [
    { label: "Total genetic findings", value: summary?.findings },
    { label: "Phenotype contribution", value: ""},
    ...Object.entries(summary?.findings_contribution || {}).map(([status, count]) => ({
      label: (status === "") ? "None" : status,
      value: count,
      indent: true
    })) 
  ]

  const sequencingItems = summary?.sequencing_vs_alignment
    ? summary.sequencing_vs_alignment.map(({ label, experiments }) => ({
        label,
        value: experiments,
        indent: true,
      }))
    : [];

  const alignedItems = summary?.sequencing_vs_alignment
  ? summary.sequencing_vs_alignment.map(({ label, alignments }) => ({
      label,
      value: alignments,
      indent: true,
    }))
  : [];

  const comparisonItems = summary?.sequencing_vs_alignment
    ? summary.sequencing_vs_alignment.map(({label, experiments, alignments, delta}) =>({
      label,
      value: `${experiments} seq, ${alignments} aln`,
      icon: (delta === 0) ? <CheckCircleTwoTone twoToneColor="#52c41a" /> : <WarningTwoTone twoToneColor="#faad14" />
    }))
    : [];
    console.log(comparisonItems)
  return (
    <Layout className="fullscreen-bg">
        <Header className="summary-header">
          <div >
            <Tooltip title="Home page">
              <Button
                onClick={() => navigate("/")}
                icon={<HomeOutlined />}
                className="header-button"
              />
            </Tooltip>
            &nbsp;&nbsp;&nbsp;
            <Tooltip title="Dashboard">
              <Button
                onClick={() => navigate("/dashboard/participant-detail")}
                icon={<DatabaseOutlined />}
                className="header-button"
              />
            </Tooltip>
          </div>

          <Title className="summary-title">GREGoR Project Status Summary</Title>

          <div /> 
        </Header>

      {error && (
        <Alert
          message="Warning"
          description="Some data failed to load. Displaying partial or placeholder results."
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Content className="site-content">

        <div style={{ marginBottom: "24px" }} /> 

        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <Card title={<span className="card-title">Proband Solve Status</span>} className="summary-card">
              <SummaryPieChart 
                data={solveStatusData}
                chartType="doughnut"
              />
            </Card>
          </Col>

          <Col xs={24} md={8}>
            <Card title={<span className="card-title">Participant Snapshot</span>} className="summary-card">
              <SummaryPieChart 
                data={[
                  {label: "Total Participants", value:summary?.participants},
                  {label: "Total Probands", value:summary?.probands},
                  {label: "Families Enrolled", value: summary?.families},
                  {label: "Total Analytes", value: summary?.analytes},
                  {label: "Samples Sequenced", value: summary?.aligned}
                ]}
                label="Participant counts"
                chartType="bar"
              />
            </Card>
          </Col>

          <Col xs={24} md={8}>
            <Card title={<span className="card-title">Families by Type</span>} className="summary-card">
              <SummaryPieChart
                data={kindredData}
                label="Family Classification"
              />
            </Card>
          </Col>
        </Row>

        <Row><br /></Row>

        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <SummaryCard
              title="Biobank Snapshot"
              items={biobankItems}
              loading={loading}
            />
          </Col>

          <Col xs={24} md={8}>
            <SummaryCard
              title="Analyte Snapshot"
              items={analyteItems}
              loading={loading}
            />
          </Col>

          <Col xs={24} md={8}>
            <SummaryCard
              title="Genetic Findings Snapshot"
              items={findingsItems}
              loading={loading}
            />
          </Col>
        </Row>

        <Row><br /></Row>

        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <SummaryCard
              title="Sequencing Experiments"
              items={sequencingItems}
              loading={loading}
            />
          </Col>

          <Col xs={24} md={8}>
            <SummaryCard
              title="Aligned Experiments"
              items={alignedItems}
              loading={loading}
            />
          </Col>

          <Col xs={24} md={8}>
            <SummaryCard
              title="Sequencing vs Alignment Counts"
              items={comparisonItems}
              loading={loading}
            />
          </Col>
        </Row>
      </Content>

      <SiteFooter showSwagger={false} showGitHub={true} />
    </Layout>
  );
};

export default SummaryPage;
