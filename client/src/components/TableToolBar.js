// src/components/TableToolBar.js

import { useState, useMemo } from "react";
import { Button, Checkbox, Collapse, Dropdown, Popconfirm, Space, Tooltip } from "antd";
import { DownloadOutlined, PlusOutlined, RedoOutlined, ReloadOutlined, ToolOutlined, SettingOutlined } from "@ant-design/icons";
import TableSelector from "./TableSelector";

export default function TableToolBar({
  schema,
  visibleColumns = {},           // from table.visible
  onToggleColumn = () => {},     // from table.toggleColumn
  onToggleAll = () => {},        // from table.toggleAll
  onReset = () => {},            // from table.reset
  defaultOpen = true,
  extra
}) {
  const [open, setOpen] = useState(false);
  const keys = useMemo(() => Object.keys(schema?.properties || {}), [schema]);
  const allSelected = keys.length > 0 && keys.every((k) => !!visibleColumns[k]);
  const someSelected = keys.some((k) => !!visibleColumns[k]) && !allSelected;

  const items = [
    {
      key: "tools",
      label: (
        <Space>
          <ToolOutlined /> Table tools
        </Space>
      ),
      children: (
        <Space wrap>
          <Tooltip title="Add new row">
            <Button  
              icon={<PlusOutlined />}
            >Add Row</Button>
          </Tooltip>
          <Tooltip title="Refresh Data">
            <Button icon={<ReloadOutlined />}
            >Refresh data</Button>
          </Tooltip>
          <Tooltip title="Download All">
            <Button icon={<DownloadOutlined />}>Export</Button>
          </Tooltip>
          <Tooltip title="Select Table">
            <TableSelector />
          </Tooltip>
          <Tooltip title="Show/hide columns">
            <Dropdown
                trigger={["click"]}
                dropdownRender={() => (
                <div className="column-toggle-menu" onClick={(e) => e.stopPropagation()}>
                  <div className="column-toggle-header">
                    <Button
                      size="small"
                      className="action-btn"
                      onClick={() => onToggleAll(!allSelected)}
                    >{allSelected ? "Deselect All" : "Select All"}</Button>
                    <Button
                      size="small"
                      className="action-btn"
                      onClick={() => onToggleAll(false)}
                    >Clear</Button>
                    <Button
                      size="small"
                      className="action-btn"
                      onClick={onReset}
                    >Restor defaults</Button>
                  </div>
                  <div className="column-toggle-list">
                    {keys.map((key) => (
                      <div key={key} className="column-toggle-item">
                        <Checkbox
                          checked={!!visibleColumns[key]}
                          onChange={(e) => onToggleColumn(key, e.target.checked)}
                        >{schema.properties[key]?.title || key}</Checkbox>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            >
            <Button icon={<SettingOutlined />}>Columns</Button>
          </Dropdown>
        </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <Collapse
      // className="site-header"
      bordered={false}
      ghost
      activeKey={open ? ["tools"] : []}
      onChange={(keys) => setOpen(keys.includes("tools"))}
      items={items}
      style={{ margin: "8px 0" }}
    />
  );
};