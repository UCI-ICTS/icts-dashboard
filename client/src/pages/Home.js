// src/pages/Home.js

import { useNavigate } from "react-router-dom";
import { Card, Col, Row, Layout, Space, Typography } from 'antd';
import SiteFooter from "../components/SiteFooter";
import React, { Component } from 'react'
import ReactMarkdown from 'react-markdown'

const { Header, Content, Footer, Sider } = Layout;
const { Title } = Typography;

const APIDB = process.env.REACT_APP_APIDB;
const MIA = process.env.REACT_APP_MIA;
const SNP = process.env.REACT_APP_SNP;

const README_URL = "https://raw.githubusercontent.com/UCI-ICTS/.github/refs/heads/main/profile/README.md"

function withNavigate(Component) {
  return function WrappedComponent(props) {
    const navigate = useNavigate();
    return <Component {...props} navigate={navigate} />;
  }
}

class HomePage extends Component {
  constructor(props) {
    super(props)

    this.state = { terms: null }
  }

  componentWillMount() {
    fetch(README_URL).then((response) => response.text()).then((text) => {
      this.setState({ terms: text })
    })
  }
  render() {
    const navigate = this.props.navigate;
    return (
      <Layout className="fullscreen-bg">
          {/* <Header className="site-header" /> */}
          <Title level={1} className='site-title'>UCI Institute for Clinical & Translational Science (ICTS) </Title>
          <Content className="site-content">
            <Row gutter={[16, 16]}>
              <Col xs={24} md={8}>
                <Card
                  hoverable
                  onClick={()=> navigate("/dashboard")}
                  title={
                    <Space>
                      <span>ICTS Dashboard</span>
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
                The GREGoR Consortium (Genomics Research to Elucidate the Genetics of Rare diseases) seeks to develop and apply approaches to discover the cause of currently unexplained rare genetic disorders.
                </Card>
              </Col>
              <Col xs={24} md={8}>
                <Card
                  hoverable
                  onClick={()=> {window.open(`${SNP}`, "_blank")}}
                  title="SNP Consortium Archive"
                >Landing page and interface for the SNP Consortium archival material.</Card>
              </Col>
              <Col xs={24} md={8}>
                <Card
                  hoverable
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
                      <span>Medical Information Assistant (MIA)</span>
                    </Space>}
                >Our virtual Medical Information Assistant (Mia)
                  A consentbot that facilitates virtual conversations with patients.
                </Card>
              </Col>
              <Col xs={24} md={8}>
              </Col>
              <Col xs={24} md={8}>
              </Col>
              </Row>
              <Row gutter={[16, 16]}>
                <Col xs={24} md={24}>
                  <Card
                    hoverable
                    title="About UCI-ICTS"
                  ><ReactMarkdown children={this.state.terms}/>
                  </Card>
                </Col>
              </Row>
          </Content>
          <SiteFooter showSwagger={false} showGitHub={false} />
      </Layout>
    )
  }
};

export default withNavigate(HomePage);
