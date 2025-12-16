// src/pages/Home.js

import axios from "axios";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, Col, Row, Layout, Space, Typography, Popover } from 'antd';
import SiteFooter from "../components/SiteFooter";
import ReactMarkdown from 'react-markdown'
import { home, home2 } from "../utils/Home";
const { Content } = Layout;
const { Title } = Typography;

const APIDB = process.env.REACT_APP_APIDB;
const MIA = process.env.REACT_APP_MIA;
const SNP = process.env.REACT_APP_SNP;

const HomePage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState();
  const README_URL = "https://raw.githubusercontent.com/UCI-ICTS/icts-dashboard/refs/heads/dev/docs/HomePage.MD"
  const fetchSummary = async () => {
    try {
      setLoading(true);
      const response = await axios.get(README_URL);
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
  console.log((typeof summary === "string"), (summary instanceof String))
  return (
    <Layout className="fullscreen-bg">
        <Title level={1} className='site-title'>UCI Institute for Clinical & Translational Science </Title>
        <Content className="site-content">
          <Row gutter={[16, 16]} className="cards-equal-row" >
            <Col className="card-col flex-col">
              <Popover
                overlayClassName="themed-popover"
                title="ICTS Dashboard"
                content={<div className="card-label">An application for clinicians, technicians, and informaticians
                  to interact with the UCI site GREGoR data</div>}
              >
                <Card
                  hoverable
                  className="primary-card card-fill"
                  onClick={()=> navigate("/dashboard")}
                >
                  <span className="home-card">ICTS Dashboard</span> 
                  <span className="home-card">by</span> 
                  <img
                      src="/health-blue.png"
                      alt="UCI Health logo"
                      className="card-icon"
                      style={{width: 130}}
                    />
                </Card>
              </Popover>
            </Col>
            <Col className="card-col flex-col">
              <Popover
                overlayClassName="themed-popover"
                title="GREGoR Data Model"
                content={
                  <span className="card-label">
                    The Consortium Data Model has been designed to reflect the relationships between families, 
                    participants, and molecular sequencing data in the GREGoR Consortium. It is expanded over
                    time through a process of versioned releases.
                  </span>}
                >
                  <Card
                    hoverable
                    className="primary-card"
                    onClick={()=> {window.open("https://github.com/UW-GAC/gregor_data_models?tab=readme-ov-file", "_blank")}}
                  >
                    <span className="home-card">GREGoR Data Model</span>
                    <div/>
                    <img
                      src="/GREGoR_Final_Logo.png"
                      alt="GREGoR logo"
                      className="card-icon"
                      style={{width: 130}}
                    />
                  </Card>
              </Popover>
            </Col>
            <Col className="card-col flex-col">
              <Popover
              overlayClassName="themed-popover"
              title="Kauro by University of California, Irvine"
              content={
                <span className="card-label">
                  A consentbot that facilitates virtual conversations with patients.
                </span>
              }>
                <Card
                  hoverable
                  className="primary-card card-fill"
                  onClick={()=> {window.open(`${MIA}`, "_blank")}}
                >
                  <img
                    src="/kauro192.png"
                    alt="MIA logo"
                    className="card-icon"
                    style={{width: 60}}
                  />
                  <span className="home-card">Kauro<br/>by<br/> UCI</span>
                    
                </Card>
              </Popover>
            </Col>
            <Col className="card-col flex-col">
              <Popover
                overlayClassName="themed-popover"
                title="Geneyx"
                content={
                  <span className="card-label">
                    NGS data analysis and interpretation platform.
                  </span>}
                >
                  <Card
                    hoverable
                    className="primary-card"
                    onClick={()=> {window.open("https://analysis.geneyx.com/account/logon", "_blank")}}
                  >
                    <img
                      src="/geneyx-clean.svg"
                      alt="geneyx"
                      className="card-icon"
                      style={{height: 70, background: "black"}}
                    />
                    <br/>
                    <span className="home-card">Geneyx</span>
                  </Card>
              </Popover>
            </Col>
          </Row>
        {/* Collabs */}
          
            <Row gutter={[16, 16]} className="cards-equal-row" >
              <Col className="card-col flex-col">
                <Popover
                  overlayClassName="themed-popover"
                  title="The GREGoR Consortium"
                  content={<div className="card-label">The GREGoR Consortium (Genomics Research to Elucidate
                    the Genetics of Rare diseases) seeks to develop and apply approaches to discover the
                    cause of currently unexplained rare genetic disorders.</div>}
                >
                  <Card
                    hoverable
                    className="primary-card card-fill"
                    onClick={()=> {window.open("https://gregorconsortium.org/", "_blank")}}
                  >
                    
                      <span className="home-card">The GREGoR Consortium</span>
                      <img
                        src="/GREGoR_Final_Logo.png"
                        alt="GREGoR logo"
                        className="card-icon"
                        style={{width: 130}}
                      />
                    
                  </Card>
                </Popover>
              </Col>
              <Col className="card-col flex-col">
                <Popover
                  overlayClassName="themed-popover"
                  title="SNP Consortium Archive"
                  content={
                    <span className="card-label">
                      Landing page and interface for the SNP Consortium archival material.
                    </span>}
                  >
                    <Card
                      hoverable
                      className="primary-card card-fill"
                      onClick={()=> {window.open(`${SNP}`, "_blank")}}
                    >
                      <span className="home-card">SNP Consortium Archive</span>
                    </Card>
                </Popover>
              </Col>
              <Col className="card-col flex-col">
                <Popover
                overlayClassName="themed-popover"
                title="Undiagnosed Diseases Network (UDN)"
                content={
                  <span className="card-label">
                    The Undiagnosed Diseases Network (UDN) is a research study backed by
                    the National Institutes of Health that seeks to provide answers for 
                    patients and families affected by these mysterious conditions.
                  </span>
                }>
                  <Card
                    hoverable
                    className="primary-card card-fill"
                    onClick={()=> {window.open("https://undiagnosed.hms.harvard.edu/", "_blank")}}
                  >
                    <span className="home-card">Undiagnosed<br/>Diseases<br/>Network</span>
                    <img
                      src="/udn_logo.png"
                      alt="UDN logo"
                      className="card-icon"
                      style={{width: 130}}
                    />
                  </Card>
                </Popover>
              </Col>
            </Row>
            {/* Other Content */}
            {summary instanceof String ? (
              <Card className="primary-card">
                <ReactMarkdown
                  // Make links open in new tab safely
                  components={{
                    a: ({ node, ...props }) => (<a {...props} target="_blank" rel="noopener noreferrer" />),
                    img: ({ node, ...props }) => (<img {...props} style={{ maxWidth: "100%" }} alt={props.alt || ""} />),
                  }}
                >
                  {summary}
                </ReactMarkdown>
              </Card>
              ) : (
                <div></div>
            )}
        </Content>
        <SiteFooter showSwagger={false} showGitHub={false} />
    </Layout>
  )
};

export default HomePage;
