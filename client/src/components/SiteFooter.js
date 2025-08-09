//src/components/SiteFooter.js
import { Footer } from "antd/es/layout/layout";
import { Space, Tooltip } from "antd";
import { ApiOutlined, GithubOutlined, CopyOutlined } from '@ant-design/icons';

const GIT_VERSION = process.env.REACT_APP_VERSION

const SiteFooter = ({ showSwagger = true, showGitHub = true }) => {
  const APIDB = process.env.REACT_APP_APIDB;

  return (
    <Footer className="site-footer">
      <Space >
        <Tooltip title="UCI ICTS Dashboard">©2024 UCI</Tooltip>

        {showSwagger && (
          <Space>
            <Tooltip title="Swagger API site">
              <ApiOutlined />
              <a
                href={`${APIDB}api/swagger/`}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
              > Swagger API</a>
            </Tooltip>
            <Tooltip title="Redoc API docs">
              <CopyOutlined />
              <a
                href={`${APIDB}api/redoc/`}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
              > Redoc API docs</a>
            </Tooltip>
          </Space>
        )}

        {showGitHub ? (
          <Tooltip title="UCI ICTS Dashboard GitHub">
            <GithubOutlined />
            <a
              href={GIT_VERSION}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
            > GitHub</a>
          </Tooltip>
        ) : (
          <Tooltip title="UCI ICTS GitHub">
            <GithubOutlined />
            <a
              href="https://github.com/UCI-ICTS"
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
            > GitHub</a>
          </Tooltip>
        )}
      </Space>
    </Footer>
  );
};

export default SiteFooter;

