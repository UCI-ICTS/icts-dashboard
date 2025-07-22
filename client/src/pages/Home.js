// src/pages/Home.js

import React, { useState } from 'react';
import { useNavigate } from "react-router-dom";
import { Card, Col, Row, Layout, Space, Tooltip, Typography } from 'antd';
import { ApiOutlined, GithubOutlined} from '@ant-design/icons';

const { Header, Content, Footer, Sider } = Layout;
const APIDB = process.env.REACT_APP_APIDB;
const { Title } = Typography;

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <Layout>
        {/* <Header className="site-header" /> */}
        <Title level={1}>ICTS </Title>
        <Content className="site-content">
            <Row gutter={[16, 16]}>
                <Col xs={24} md={8}>
                  <Card 
                    title="ICTS Dashboard"
                    hoverable
                    onClick={()=> navigate("/dashboard")}
                  ></Card>
                </Col>
                <Col xs={24} md={8}>
                  <Card 
                    hoverable
                    onClick={()=> console.log("HI")}
                    title="SNP"
                  ></Card>
                </Col>
                <Col xs={24} md={8}>
                  <Card
                    title="MIA"
                    hoverable
                    onClick={()=> console.log("HI")}
                  ></Card>
                </Col>
                <Col xs={24} md={8}>
                </Col>
                <Col xs={24} md={8}>
                </Col>
            </Row>
            <Row gutter={[16, 16]}>

            </Row>
        </Content>
        <Footer className="site-footer">
          <Space >
            <Tooltip title="UCI ICTS Dashboard"> ©2024 UCI</Tooltip>
            <br/>
            <Tooltip title="Swagger API site">
              <ApiOutlined />
              <a
                href={`${APIDB}api/swagger/`} //"https://genomics.icts.uci.edu/"
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()} // prevent triggering `onClick` from Menu
                >
                Swagger API
              </a>
            </Tooltip>
            <br/>
            <Tooltip title="UCI ICTS Dashboard GitHub">
              <GithubOutlined />
              <a
                href="https://github.com/UCI-GREGoR/GREGor_dashboard"
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()} // prevent triggering `onClick` from Menu
              >GitHub</a>
            </Tooltip>
          </Space>
        </Footer>
    </Layout>
  )
};

export default HomePage;
