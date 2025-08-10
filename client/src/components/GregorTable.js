// src/components/GregorTable.js

import { useMemo } from "react";
import { Table } from "antd";
import { Resizable } from "react-resizable";

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

export default function GregorTable({ rowKey, data, columns, onResizeColumn }) {
  // Attach header cells for resize (kept here to decouple hook from AntD)
  const cols = useMemo(
    () =>
      columns.map((c) => ({
        ...c,
        onHeaderCell: () => ({
          width: c.width,
          onResize: (_, { size }) => onResizeColumn(c.key, size.width),
        }),
      })),
    [columns, onResizeColumn]
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
    />
  );
}
