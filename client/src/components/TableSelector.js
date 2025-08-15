// src/components/TableSelector.js

import "../App.css"
import { Select, Tooltip } from "antd";
import { useNavigate, useParams } from "react-router-dom";
import { useSelector } from "react-redux";
import { TABLE_MAPPING } from "../utils/schemaAndTables";

const { Option } = Select;

export default function TableSelector() {
  const navigate = useNavigate();
  const { table: urlTable } = useParams();
  const reduxTable = useSelector(s => s.data.tableView);

  const validSchemas = new Set(TABLE_MAPPING.map(t => t.schema));
  const selected =
    (urlTable && validSchemas.has(urlTable) && urlTable) ||
    (reduxTable && validSchemas.has(reduxTable) && reduxTable) ||
    TABLE_MAPPING[0].schema; // final fallback

  return (
    <Tooltip title="Select table" className="table-selector-container">
      Select Table:&nbsp;
      <Select
        className="table-selector"
        value={selected}
        onChange={(val) => navigate(`/dashboard/table-data/${val}`)}
      >
        {TABLE_MAPPING.map((t) => (
          <Option key={t.schema} value={t.schema} className="table-selector-options">
            {t.name}
          </Option>
        ))}
      </Select>
    </Tooltip>
  );
}
