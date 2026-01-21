// src/pages/GregorDataSheets.js

import { useEffect, useMemo, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { Layout, Typography, Spin, Modal, Form, Input, Select, Button, message } from "antd";
import { useTableSettings, buildColumns } from "../utils/tableSettings";
import { setTableView, fetchTable, familyDetail, caseQueue } from "../slices/dataSlice";
import { defaultVisibleColumns, getCollectionName, getTableName } from "../utils/schemaAndTables";
import SchemaForm from "../components/SchemaForm";
import GregorTable from "../components/GregorTable";
import schemas from "../schemas/v1.9schemas.json";
import TableToolBar from "../components/TableToolBar";
import ParticipantDetail from "../components/ParticipantDetail";
import CaseQueue from "../components/CaseQueue";

const { Header } = Layout;
const { Title } = Typography;
const { Option } = Select;

export default function GregorDataSheets({ renderDetail=false, renderQueue=false }) {
  const { table } = useParams();
  const dispatch = useDispatch();
  const isAdmin  = useSelector((state) => state.account.user.is_superuser);
  const status   = useSelector((state) => state.data.status);
  const tableView = useSelector((state) => state.data.tableView);
  const data     = useSelector((state) => state.data[tableView]) || [];
  const rowKey   = useSelector((state) => state.data.tableID);
  const schema   = schemas[tableView] || { properties: {} };
  const rememberUI = Boolean(localStorage.getItem("user"));
// ---- Global search + regex toggle ----
  const [useRegex, setUseRegex] = useState(false);
  const [search, setSearch] = useState("");
  const [regexErr, setRegexErr] = useState(null);
// ----Advanced filters modal state (same shape as `filters`) ----
  const [advOpen, setAdvOpen] = useState(false);
  const [draft, setDraft] = useState({}); // temp edits before Apply
// ----Export modal state ----
  const [exportOpen, setExportOpen] = useState(false);
  const [exportFormat, setExportFormat] = useState("TSV"); // Default format
// ----Participant Detail state ----
  const [selectedRow, setSelectedRow] = useState(null);
  const [detailLoading, setDetailLoading ] = useState(true)
// ----Case Queue state ----
  const [queueLoading, setQueueLoading ] = useState(true)
// ---- Table URL state ----

  const tableValid = useMemo(() => !!schemas[table], [table]);

  // create object for setTableView
  const meta = (schema) => ({
    schema,
    identifier: schemas[schema]?.identifier || `${schema}_id`,
    name: schemas[schema]?.title || schema,
  })

  // Sync URL (only when NOT at ParticipantDetail)
  useEffect(() => {
    if (renderDetail || renderQueue) {
      if (tableView !== "participants") {
        dispatch(setTableView(meta("participants")));
      }
    }
    if (!tableValid) return;
    if (tableView !== table) {
      dispatch(setTableView(meta(table))); // one-way sync
    }
  }, [renderDetail, renderQueue, tableValid, table, tableView, dispatch]);

  // Enforce “participants” in detail mode
  useEffect(() => {
    if (!renderDetail) return;
    if (!renderQueue) return;
    if (tableView !== "participants") {
      dispatch(setTableView(meta("participants")));
    }
  }, [renderDetail, renderQueue, tableView, dispatch]);

  // Fetch data for the current table when empty
  useEffect(() => {
    if (!tableView) return;
    if (status === "loading") return;
    if (data.length === 0) {
      dispatch(fetchTable(getCollectionName(tableView)));
    }
  }, [tableView, data.length, status, dispatch]);

  // ---- Modal controller (add/edit) ----
  const [modal, setModal] = useState({ open: false, kind: null, payload: null });
  const openModal = (kind, payload = null) => setModal({ open: true, kind, payload });
  const closeModal = () => setModal({ open: false, kind: null, payload: null });

  // ---- Table settings (columns, widths) ----
  const dataTable = useTableSettings({
    schema,
    tableView,
    defaults: defaultVisibleColumns[tableView] || [],
    persist: rememberUI,  // switch persistence on/off
    storagePrefix: "uci:tableSettings", // namespace for table preferences
  });

  const { sorter, filters, setSorter, setFilters } = dataTable;

  const columns = buildColumns({ schema, visible: dataTable.visible, widths: dataTable.widths });

  const onChangeSort = (val) => setSorter(val);
  const onChangeFilter = (key, value) =>
    setFilters((prev) => ({ ...prev, [key]: value }));
  const onClearFilter = (key) =>
    setFilters((prev) => {
      const next = { ...prev };
      delete next[key];
      return next;
    });

  // Build a list of visible field keys once
  const visibleKeys = useMemo(
    () => Object.keys(schema?.properties || {}).filter((k) => dataTable.visible[k]),
    [schema, dataTable.visible]
  );

  // ---- Apply global search + advanced filters + header filters + sorting ----
  const displayData = useMemo(() => {
    let rows = [...data];

    // 1) Global search (regex or contains) across all fields
    if (search.trim()) {
      const q = search.trim();
      rows = rows.filter((row) => {
        return Object.entries(row).some(([k, v]) => {
          const str = String(v ?? "");
          const field = schema.properties?.[k];

          if (useRegex) {
            try {
              const re = new RegExp(q, "i");
              setRegexErr(null);
              return re.test(str);
            } catch {
              setRegexErr("Invalid regular expression");
              return false;
            }
          }

          // enums: require exact (case-insensitive)
          if (field?.enum) return str.toLowerCase() === q.toLowerCase();

          // default: partial match
          return str.toLowerCase().includes(q.toLowerCase());
        });
      });
    }

    // 2) Advanced filters (applied to same `filters` map)
    const mergedFilters = { ...filters }; // header + advanced are the same store
    rows = rows.filter((row) =>
      Object.entries(mergedFilters).every(([k, val]) => {
        if (!val) return true;
        const field = schema.properties?.[k];
        const str = String(row[k] ?? "");
        if (field?.enum) return str === val; // exact for enums
        return str.toLowerCase().includes(String(val).toLowerCase());
      })
    );

    // 3) Sort
    if (sorter?.key && sorter.order) {
      const { key, order } = sorter;
      rows.sort((a, b) => {
        const A = String(a[key] ?? "");
        const B = String(b[key] ?? "");
        const cmp = A.localeCompare(B, undefined, { numeric: true });
        return order === "ascend" ? cmp : -cmp;
      });
    }

    return rows;
  }, [data, schema, search, useRegex, filters, sorter]);

  const handleDownload = () => {
    const filename = tableView
    if (!displayData.length || !visibleKeys.length) {
      message.warning("No data to export.");
      return;
    }

    let fileContent = "";
    let fileExtension = "";
    let mimeType = "";

    if (exportFormat === "TSV" || exportFormat === "CSV") {
      const isTSV = exportFormat === "TSV";
      const delimiter = isTSV ? "\t" : ",";
      fileExtension = isTSV ? "tsv" : "csv";
      mimeType = isTSV
        ? "text/tab-separated-values;charset=utf-8"
        : "text/csv;charset=utf-8";

      // Escape function for CSV/TSV values
      const escapeValue = (value) => {
        if (Array.isArray(value)) {
          return `"${value.map(item => item.toString().trim()).join("|")}"`;
        }
        if (typeof value === "string") {
          let trimmedValue = value.trim();
          if (trimmedValue.includes(delimiter) || trimmedValue.includes('"') || trimmedValue.includes("\n")) {
            // Wrap in quotes if containing delimiter, quotes, or newlines
            trimmedValue = `"${trimmedValue.replace(/"/g, '""')}"`;
          }
          return trimmedValue;
        }
        return value !== undefined ? value : "";
      };

      // Extract column headers
      const getHeaderTitle = (k) =>
        schema?.properties?.[k]?.title || k;

      const keys = visibleKeys;

      const headers = keys
        .map((k) => escapeValue(getHeaderTitle(k), delimiter))
        .join(delimiter);

      // Convert rows to formatted CSV/TSV
      const fileRows = displayData.map((row) =>
        keys.map((k) => escapeValue(row?.[k])).join(delimiter)
      );

      // Combine headers and rows
      fileContent = [headers, ...fileRows].join("\n");

    } else if (exportFormat === "JSON") {
      fileExtension = "json";
      mimeType = "application/json;charset=utf-8";
      fileContent = JSON.stringify(displayData, null, 2);
    }
    // Create and trigger download
    const blob = new Blob([fileContent], { type: mimeType });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `${filename}.${fileExtension}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    message.success(`Current data exported as ${exportFormat}`);
    setExportOpen(false); // Close modal after download
  };

  const handleRefresh = () => {
    if (tableView) {
      dispatch(fetchTable(getCollectionName(tableView)));
    }
  };

  const handleDetail = (record) => {
    setSelectedRow(record);
    dispatch(familyDetail(record.participant_id))
  };

  const handleQueue = (record) => {
    console.log(record);
    setSelectedRow(record);
    dispatch(caseQueue(record.participant_id))
  };

  return (
    <Layout className="admin-layout">
      {renderDetail ? (
        <>
          <Header className="secondary-header">
            <Title className="secondary-title">GREGoR Participant Detail</Title>
          </Header>

          {selectedRow ? (
            <ParticipantDetail
              selectedRow={selectedRow}
              setSelectedRow={setSelectedRow}
              onRow={(record)=> {}}
              detailLoading={detailLoading}
              setDetailLoading={setDetailLoading}
              openModal={openModal}
            />
          ) : null}
        </>
      ) : renderQueue ? (
        <>
          <Header className="secondary-header">
            <Title className="secondary-title">GREGoR Case Queue</Title>
          </Header>

          {selectedRow ? (
            <CaseQueue
              selectedRow={selectedRow}
              setSelectedRow={setSelectedRow}
              onRow={(record)=> {}}
              queueLoading={queueLoading}
              setQueueLoading={setQueueLoading}
              openModal={openModal}
            />
          ) : null}
        </>
      ) : (
        <Header className="primary-header">
          <Title className="primary-title">GREGoR Data Sheets</Title>
        </Header>
      )}


      <TableToolBar
        schema={schema}
        visibleColumns={dataTable.visible}
        onToggleColumn={dataTable.toggleColumn}
        onToggleAll={dataTable.toggleAll}
        onReset={dataTable.reset}
        onOpenModal={openModal}
        // global search + regex stay here (page-level is fine)
        useRegex={useRegex}
        onToggleRegex={setUseRegex}
        search={search}
        onSearch={setSearch}
        regexError={regexErr}
        onOpenAdvanced={() => { setDraft(filters); setAdvOpen(true); }}
        onExportOpen={() => setExportOpen(true)}
        recordCount={displayData.length}
        onRefresh={handleRefresh}
        renderDetail={renderDetail}
        renderQueue={renderQueue}
      />
      {status === "loading" ? (
        <Spin tip="Loading data..." style={{ display: "block", textAlign: "center", marginTop: 20 }}>
          <div style={{ minHeight: 100 }} />
        </Spin>
      ) : (
        <GregorTable
          rowKey={rowKey}
          data={displayData}
          columns={columns}
          onResizeColumn={dataTable.setWidth}
          onRow={(record) => ({ onClick: () => {
            renderDetail ? (
              handleDetail(record)
            ) : renderQueue ? (
              handleQueue(record)
            ) : (
              openModal("edit", { record })
            )
          }})}
          sorter={sorter}
          filters={filters}
          onChangeSort={onChangeSort}
          onChangeFilter={onChangeFilter}
          onClearFilter={onClearFilter}
        />
      )}

      {/* Add/Edit row modal */}
      {(modal.kind === "add" || modal.kind === "edit") && (
        <Modal
          className="uci-modal"
          title={modal.kind === "edit" ? `Edit Record:  ${tableView}` : `Add Record: ${tableView}`}
          open={modal.open}
          onCancel={closeModal}
          footer={null}
          destroyOnClose
          width={800}
        >
          <SchemaForm
            schema={schemas[modal.payload?.schemaKey || tableView] || schema}
            initialValues={modal.kind === "edit" ? modal.payload?.record : {}}
            open={modal.open}
            addEntry={(modal.kind === "add")}
            onClose={closeModal}
            isAdmin={isAdmin}
          />
        </Modal>
      )}

      {/* Advanced Filters modal – edits `draft`, applies to `filters` */}
      <Modal
        className="uci-modal"
        title="Advanced Filters"
        open={advOpen}
        onCancel={() => setAdvOpen(false)}
        footer={[
          <Button key="clear" onClick={() => setDraft({})}>Clear</Button>,
          <Button
            key="apply"
            type="primary"
            onClick={() => {
              setFilters(draft);
              setAdvOpen(false);
            }}
          >
            Apply
          </Button>,
        ]}
      >
        <Form layout="horizontal">
          {visibleKeys.map((key) => {
            const def = schema.properties[key];
            return (
              <Form.Item key={key} label={`Filter by ${def?.title || key}`}>
                {def?.enum ? (
                  <Select
                    allowClear
                    value={draft[key]}
                    onChange={(val) => setDraft((p) => ({ ...p, [key]: val }))}
                  >
                    {def.enum.map((opt) => (
                      <Option key={opt} value={opt}>{opt}</Option>
                    ))}
                  </Select>
                ) : (
                  <Input
                    value={draft[key] ?? ""}
                    onChange={(e) => setDraft((p) => ({ ...p, [key]: e.target.value }))}
                  />
                )}
              </Form.Item>
            );
          })}
        </Form>
      </Modal>

      {/* Modal for Selecting Export Format */}
      <Modal
        className="uci-modal"
        title="Select Export Format"
        open={exportOpen}
        onCancel={() => setExportOpen(false)}
        onOk={handleDownload}
        okText="Download"
        cancelText="Cancel"
      >
        <Select
          value={exportFormat}
          onChange={setExportFormat}
          style={{ width: "100%" }}
        >
          <Option value="TSV">TSV</Option>
          <Option value="CSV">CSV</Option>
          <Option value="JSON">JSON</Option>
        </Select>
      </Modal>
    </Layout>
  );
}
