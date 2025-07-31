// src/pages/SummaryPage.js

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, Row, Col, Layout, Typography, Tooltip, Button, Alert } from "antd";
import { HomeOutlined, CheckCircleTwoTone, WarningTwoTone } from "@ant-design/icons";
import axios from "axios";
import SiteFooter from "../components/SiteFooter";
import { primaryBiosample } from "../utils/schemaAndTables";
import "../App.css";

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
      const response = await axios.get("/api/search/summary/");
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

  return (
    <Layout className="fullscreen-bg">
      <Title level={1} className="site-title">
        UCI Institute for Clinical & Translational Science (ICTS)
      </Title>

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
        <Header className="summary-header">
          <div className="home-container">
            <Tooltip title="Home page">
              <Button
                onClick={() => navigate("/")}
                icon={<HomeOutlined />}
                className="home-button"
              />
            </Tooltip>
          </div>

          <Title className="summary-title">GREGoR Project Status Summary</Title>

          <div className="home-container" /> {/* Invisible placeholder for spacing */}
        </Header>


        <div style={{ marginBottom: "24px" }} /> 

        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <Card title="Participant Snapshot">
              <p>Total Participants: {get(summary, "participants")}</p>
              <p>Families Enrolled: {get(summary, "families")}</p>
              <p>Total Analytes: {get(summary, "analytes")}</p>
              <p>Samples Sequenced: {get(summary, "aligned")}</p>
            </Card>
          </Col>

          <Col xs={24} md={8}>
            <Card title="Proband Solve Status">
              {Object.entries(summary?.solve_status_counts || {}).map(([status, count]) => (
                <p key={status}>{status}: {count}</p>
              ))}
            </Card>
          </Col>

          <Col xs={24} md={8}>
            <Card title="Kindrid">
              {Object.entries(summary?.kindrid || {}).map(([label, count]) => (
                <p key={label}>{label}: {count}</p>
              ))}
            </Card>
          </Col>
        </Row>

        <Row><br /></Row>

        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <Card title="Biobank Snapshot">
              <p>Total Biobank Entries: {
                Object.values(summary?.biobank_status_counts || {}).reduce((a, b) => a + b, 0)
              }</p>
              <p>Biobank Status:</p>
              <div style={{ paddingLeft: 16 }}>
                {Object.entries(summary?.biobank_status_counts || {}).map(([status, count]) => (
                  <p key={status}>{status}: {count}</p>
                ))}
              </div>
            </Card>
          </Col>

          <Col xs={24} md={8}>
            <Card title="Analyte Snapshot">
              <p>Total Analyte Entries: {get(summary, "analytes")}</p>
              <p>Primary Biosamples:</p>
              <div style={{ paddingLeft: 16 }}>
                {Object.entries(summary?.analyte_biosample_counts || {}).map(([status, count]) => (
                  <p key={status}>{status} {primaryBiosample[status] || ""}: {count}</p>
                ))}
              </div>
              <p>Analyte Types:</p>
              <div style={{ paddingLeft: 16 }}>
                {Object.entries(summary?.analyte_type_counts || {}).map(([status, count]) => (
                  <p key={status}>{status}: {count}</p>
                ))}
              </div>
            </Card>
          </Col>

          <Col xs={24} md={8}>
            <Card title="Genetic Findings Snapshot">
              <p>Total Genetic Findings: {get(summary, "findings")}</p>
              <p>Phenotype Contribution:</p>
              <div style={{ paddingLeft: 16 }}>
                {Object.entries(summary?.findings_contribution || {}).map(([status, count]) => (
                  status === "" 
                  ? (<p key={status}>Na: {count}</p>)
                  : (<p key={status}>{status}: {count}</p>)
                ))}
              </div>
            </Card>
          </Col>
        </Row>

        <Row><br /></Row>

        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <Card title="Sequencing Experiments">
              {summary?.sequencing_vs_alignment?.map(({ label, experiments }) => (
                <p key={label}><strong>{label}:</strong> {experiments}</p>
              )) || "Loading..."}
            </Card>
          </Col>

          <Col xs={24} md={8}>
            <Card title="Aligned Experiments">
              {summary?.sequencing_vs_alignment?.map(({ label, alignments }) => (
                <p key={label}><strong>{label}:</strong> {alignments}</p>
              )) || "Loading..."}
            </Card>
          </Col>

          <Col xs={24} md={8}>
            <Card title="Sequencing vs Alignment Counts">
              {summary?.sequencing_vs_alignment?.map(({ label, experiments, alignments, delta }) => (
                <p key={label}>
                  <strong>{label}:</strong> {experiments} seq, {alignments} aln{" "}
                  {delta === 0 ? (
                    <CheckCircleTwoTone twoToneColor="#52c41a" />
                  ) : (
                    <WarningTwoTone twoToneColor="#faad14" />
                  )}
                </p>
              )) || "Loading..."}
            </Card>
          </Col>
        </Row>
      </Content>

      <SiteFooter showSwagger={false} showGitHub={false} />
    </Layout>
  );
};

export default SummaryPage;
