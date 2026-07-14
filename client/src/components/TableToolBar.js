// src/components/TableToolBar.js

import { useState, useMemo } from "react";
import { Button, Checkbox, Collapse, Dropdown, Input, Space, Switch, Tooltip, Typography } from "antd";
import { SearchOutlined, DownloadOutlined, PlusOutlined, FilterOutlined, ReloadOutlined, ToolOutlined, SettingOutlined } from "@ant-design/icons";
import TableSelector from "./TableSelector";
import { fetchTable } from "../slices/dataSlice";

export default function TableToolBar({
  schema,
  onOpenModal,
  visibleColumns = {},           // from table.visible
  onToggleColumn = () => {},     // from table.toggleColumn
  onToggleAll = () => {},        // from table.toggleAll
  onReset = () => {},            // from table.reset
  useRegex,
  onToggleRegex,
  search,
  onSearch,
  regexError,
  onOpenAdvanced,
  onExportOpen,
  recordCount,
  onRefresh,
  renderDetail,
  renderQueue,
  extra,
}) {
  const [open, setOpen] = useState(false);
  const keys = useMemo(() => Object.keys(schema?.properties || {}), [schema]);
  const allSelected = keys.length > 0 && keys.every((k) => !!visibleColumns[k]);
  const restrictedView = renderDetail || renderQueue;

  const items = [
    {
      key: "tools",
      label: (
        <Space wrap>
          <ToolOutlined className="icon-blue"/>
          <div className="toolbar-title">Filtering tools</div>
          &nbsp;&nbsp;&nbsp;&nbsp;
          <div className="card-label">Number of records:</div>
          <div className="card-number">{recordCount}</div>
          &nbsp;&nbsp;&nbsp;&nbsp;
          <Tooltip title="Export the current data to a CSV, TSV, or JSON">
            <Button
              className="action-btn"
              icon={<DownloadOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                onExportOpen(true);
              }}
            >Export table</Button>
          </Tooltip>
        </Space>
      ),
      children: (
        <div className="table-search-controls">
            <div className="table-regex-switch">
              <Tooltip title={(useRegex) ? "Disable regular expressions for global search" : "Enable regular expressions for global search"}>
                <div className="table-regex-switch">
                  <Switch checked={useRegex} onChange={onToggleRegex} />
                </div>
              </Tooltip>
            </div>
            <Input
              className="table-search-input"
              prefix={<SearchOutlined />}
              placeholder={(useRegex) ? "Search with Regex" : "Search all fields"}
              value={search}
              onChange={(e) => onSearch(e.target.value)}
              status={useRegex && regexError ? "error" : undefined}
              style={{ width: 260 }}
            />

          <Tooltip title="Show/hide columns">
            <Dropdown
              trigger={["click"]}
              dropdownRender={() => (
                <div className="column-toggle-menu" onClick={(e) => e.stopPropagation()}>
                  <Space className="column-toggle-header">
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
                  </Space>
                  <div className="column-toggle-list">
                    <br/>
                    {keys.map((key) => (
                      <div key={key} className="column-toggle-item">
                        <Checkbox
                          checked={!!visibleColumns[key]}
                          onChange={(e) => onToggleColumn(key, e.target.checked)}
                        >
                          <span className="card-lable">{schema.properties[key]?.title || key}</span>
                        </Checkbox>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            >
            <Button
              className="action-btn"
              icon={<SettingOutlined />}
            >Columns</Button>
            </Dropdown>
          </Tooltip>
          <Tooltip title="Advanced Filters">
            <Button className="action-btn" icon={<FilterOutlined />} onClick={onOpenAdvanced}>
              Advanced Filters
            </Button>
          </Tooltip>
        </div>
      ),
    },
  ];

  return (
    <>
{!restrictedView && (
  <Space wrap>
    <Tooltip title="Add new row">
      &nbsp;
      <Button
        className="action-btn"
        icon={<PlusOutlined />}
        onClick={() => onOpenModal("add")}
      >
        Add Row
      </Button>
    </Tooltip>

    &nbsp;
    <TableSelector />
    &nbsp;

    <Tooltip title="Refresh Data">
      <Button
        className="action-btn"
        icon={<ReloadOutlined />}
        onClick={(event) => {
          event.stopPropagation();
          onRefresh?.();
        }}
      >
        Refresh data
      </Button>
    </Tooltip>

    &nbsp;
  </Space>
)}
      <Space >
      <Collapse
        // className="site-header"
        bordered={false}
        ghost
        activeKey={open ? ["tools"] : []}
        onChange={(keys) => setOpen(keys.includes("tools"))}
        items={items}
        style={{ margin: "8px 0" }}
      />
      </Space>
    </>
  );
};