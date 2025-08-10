// src/pages/GregorDataSheets.js

import { useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { Layout, Typography, Spin } from "antd";
import { useTableSettings, buildColumns } from "../utils/tableSettings";
import { defaultVisibleColumns } from "../utils/schemaAndTables";
import { getCollectionName } from "../utils/tableNameMap";
import { fetchTable } from "../slices/dataSlice";
import GregorTable from "../components/GregorTable";
import schemas from "../schemas/v1.8schemas.json";
import TableToolBar from "../components/TableToolBar";

const { Header } = Layout; const { Title } = Typography;

export default function GregorDataSheets() {
  const dispatch = useDispatch()
  const dataStatus = useSelector((s) => s.data.status);
  const tableView  = useSelector((s) => s.data.tableView);
  const data       = useSelector((s) => s.data[tableView]) || [];
  const rowID      = useSelector((s) => s.data.tableID);
  const schema     = schemas[tableView] || { properties: {} };
 
  // Fetch table data when tableView changes or empty
  useEffect(() => {
    if ((!data || data.length === 0) && tableView) {
      dispatch(fetchTable(getCollectionName(tableView)));
    }
  }, [dispatch, tableView, data]);

  // table settings hook
  const table = useTableSettings({
    schema,
    tableKey: tableView,
    defaults: defaultVisibleColumns[tableView] || [],
  });

  const columns = buildColumns({
    schema,
    visible: table.visible,
    widths: table.widths,
  });

  return (
    <Layout className="admin-layout">
      <Header className="summary-header">
        <Title className="summary-title">GREGoR Data Sheets</Title>
      </Header>

      <TableToolBar
        schema={schema}
        visibleColumns={table.visible}
        onToggleColumn={table.toggleColumn}  // <-- matches toolbar
        onToggleAll={table.toggleAll}        // <-- matches toolbar
        onReset={table.reset}
        // extra={<YourCustomButtons />}
      />

      {dataStatus === "loading" ? (
        <Spin tip="Loading data..." style={{ display: "block", textAlign: "center", marginTop: 20 }}>
          <div style={{ minHeight: 100 }} />
        </Spin>
      ) : (
        <GregorTable
          rowKey={rowID}
          data={data}
          columns={columns}
          onResizeColumn={table.setWidth}
        />
      )}
    </Layout>
  );
}
