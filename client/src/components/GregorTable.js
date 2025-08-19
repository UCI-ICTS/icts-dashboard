// src/components/GregorTable.js

import { useMemo, useState } from "react";
import { Table, Dropdown, Button, Input, Radio, Space, Divider } from "antd";
import { Resizable } from "react-resizable";
import { FunnelPlotOutlined, ClearOutlined } from "@ant-design/icons";

const MIN_COL_WIDTH = 80;

const ResizableTitle = (props) => {
  const { onResize, width, ...rest } = props;
  if (!width) return <th {...rest} />;
  return (
    <Resizable
      width={width}
      height={0}
      onResize={onResize}
      minConstraints={[MIN_COL_WIDTH, 0]}
      draggableOpts={{ enableUserSelectHack: false }}
      handle={<span className="react-resizable-handle" onClick={(e) => e.stopPropagation()} />}
    >
      <th {...rest} />
    </Resizable>
  );
};

/** Small header popout for per-column sort/filter */
function TitleMenu({
  title,
  colKey,
  sorter,
  filters,
  onChangeSort,
  onChangeFilter,
  onClearFilter,
}) {
  const sortOrder = sorter?.key === colKey ? sorter.order : null;
  const filterValue = filters?.[colKey] ?? "";

  return (
    <Space size={6}>
<Dropdown
  trigger={["click"]}
  placement="bottomRight"
  dropdownRender={() => (
    <div
      className="column-filter-menu"
      onClick={(e) => e.stopPropagation()}
    >
      <div className="column-filter-header">
        <div className="column-filter-title">{title}</div>
        <button
          type="button"
          className="column-filter-reset"
          onClick={() => {
            onChangeSort(null);
            onClearFilter(colKey);
          }}
        >
          Reset
        </button>
      </div>

      <div className="column-filter-section">
        <div className="column-filter-label">Sort</div>
        <Radio.Group
          size="small"
          value={sortOrder || "none"}
          onChange={(e) => {
            const val = e.target.value;
            if (val === "none") onChangeSort(null);
            else onChangeSort({ key: colKey, order: val });
          }}
        >
          <Radio.Button value="ascend">Asc</Radio.Button>
          <Radio.Button value="descend">Desc</Radio.Button>
          <Radio.Button value="none">None</Radio.Button>
        </Radio.Group>
      </div>

      <div className="column-filter-divider" />

      <div className="column-filter-section">
        <div className="column-filter-label">Filter (contains)</div>
        <div className="column-filter-inputrow">
          <Input
            size="small"
            placeholder="Type to filter…"
            value={filters?.[colKey] ?? ""}
            onChange={(e) => onChangeFilter(colKey, e.target.value)}
          />
          <Button
            size="small"
            className="column-filter-clear"
            onClick={() => onClearFilter(colKey)}
          >
            Clear
          </Button>
        </div>
      </div>
    </div>
  )}
>
  <Button
    size="small"
    className="header-button"
    icon={<FunnelPlotOutlined />}
    onClick={(e) => e.stopPropagation()}
  />
</Dropdown>

      <span>{title}</span>
    </Space>
  );
}


export default function GregorTable({ rowKey, data, columns, onResizeColumn, onRow,
  sorter,              // { key, order } | null
  filters = {},        // { [colKey]: string }
  onChangeSort,        // (sorter|null) => void
  onChangeFilter,      // (key, value) => void
  onClearFilter,       // (key) => void
 }) {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  
  // Attach header cells for resize (kept here to decouple hook from AntD)
  const cols = useMemo(
    () =>
      columns.map((c) => ({
        ...c,
        title: (
          <TitleMenu
            title={c.title}
            colKey={c.key}
            sorter={sorter}
            filters={filters}
            onChangeSort={onChangeSort}
            onChangeFilter={onChangeFilter}
            onClearFilter={onClearFilter}
          />
        ),
        onHeaderCell: () => ({
          width: c.width,
          onResize: (_, { size }) => onResizeColumn(c.key, size.width),
        }),
        // (optional) reflect sort order icon on header if you also let AntD sort visuals show
        sortOrder: sorter?.key === c.key ? sorter.order : null,
        sorter: false, // we’re handling sort externally—set true if you want AntD to call onChange
        // (optional) if you want AntD’s filter icon behavior instead of our custom menu:
        // filterDropdown: ...,
        // filterIcon: <FunnelPlotOutlined />,
      })),
    [columns, sorter, filters, onResizeColumn, onChangeSort, onChangeFilter, onClearFilter]
  );

  const totalWidth = useMemo(
    () => cols.reduce((s, c) => s + (c.width || 180), 0),
    [cols]
  );

  const components = useMemo(
    () => ({ header: { cell: ResizableTitle } }),
    []
  );
  
  return (
    <Table
      className="table"
      bordered
      components={components}
      rowKey={rowKey || "id"}
      columns={cols}
      dataSource={data}
      tableLayout="fixed"
      scroll={{ x: totalWidth }}
      onRow={onRow}
      pagination={{
        current: page,
        pageSize,
        onChange: (page, pageSize) => {
          setPage(page);
          setPageSize(pageSize === "All" ? data.length : pageSize); // Handle "All" option
        },
        showSizeChanger: true,
        pageSizeOptions: ["10", "25", "50", "100", "All"],
      }}
    />
  );
}
