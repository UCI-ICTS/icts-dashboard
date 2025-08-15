// src/pages/Home.js

import { useNavigate } from "react-router-dom";
import { Card, Col, Row, Layout, Space, Typography } from 'antd';
import SiteFooter from "../components/SiteFooter";
const { Header, Content, Footer, Sider } = Layout;
const { Title } = Typography;

const APIDB = process.env.REACT_APP_APIDB;
const MIA = process.env.REACT_APP_MIA;
const SNP = process.env.REACT_APP_SNP;

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <Layout className="fullscreen-bg">
        <Title level={1} className='site-title'>UCI Institute for Clinical & Translational Science (ICTS) </Title>
        <Content className="site-content">
          <Row gutter={[16, 16]}>
            <Col xs={24} md={8}>
              <Card 
                hoverable
                className="primary-card"
                onClick={()=> navigate("/dashboard")}
                title={
                  <Space>
                    <span className="card-title">ICTS Dashboard</span>
                      <img
                        src="/GREGoR_Final_Logo.png"
                        alt="GREGoR"
                        style={{
                          width: 130,
                          objectFit: "contain",
                          display: "inline-block"
                        }}
                      />
                  </Space>
              }>
              <span className="card-label">The GREGoR Consortium (Genomics Research to Elucidate the Genetics of Rare diseases) seeks to develop and apply approaches to discover the cause of currently unexplained rare genetic disorders.</span>
              </Card>
            </Col>
            <Col xs={24} md={8}>
              <Card 
                hoverable
                className="primary-card"
                onClick={()=> {window.open(`${SNP}`, "_blank")}}
                title={<span className="card-title">SNP Consortium Archive</span>}
              ><span className="card-label">Landing page and interface for the SNP Consortium archival material.</span></Card>
            </Col>
            <Col xs={24} md={8}>
              <Card
                hoverable
                className="primary-card"
                onClick={()=> {window.open(`${MIA}`, "_blank")}}
                title={
                  <Space>
                    <img
                      src="/miaLogo192.png"
                      alt="MIA logo"
                      style={{
                        width: 30,
                        objectFit: "contain",
                        display: "inline-block"
                      }}
                    />
                    <span className="card-title">Medical Information Assistant (MIA)</span>
                  </Space>}
              ><span className="card-label">Our virtual Medical Information Assistant (Mia)
                A consentbot that facilitates virtual conversations with patients.</span>
              </Card>
            </Col>
            <Col xs={24} md={8}>
            </Col>
            <Col xs={24} md={8}>
            </Col>
            </Row>
            <Row gutter={[16, 16]}>

            </Row>
        </Content>
        <SiteFooter showSwagger={false} showGitHub={false} />
    </Layout>
  )
};

export default HomePage;
