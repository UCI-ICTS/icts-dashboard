// src/components/TableSelector.js

import "../App.css"
import { Select, Tooltip } from "antd";
import { useNavigate, useParams } from "react-router-dom";
import { useSelector } from "react-redux";
import { TABLE_MAPPING, isSubmodel } from "../utils/schemaAndTables";

const { Option } = Select;

export default function TableSelector({ group = "main" }) {
  const navigate = useNavigate();
  const { table: urlTable } = useParams();
  const reduxTable = useSelector(s => s.data.tableView);

  const wantSub = group === "submodels";
  const tables = TABLE_MAPPING.filter((t) => isSubmodel(t.schema) === wantSub);
  const basePath = wantSub ? "/dashboard/submodels" : "/dashboard/table-data";

  const validSchemas = new Set(tables.map(t => t.schema));
  const selected =
    (urlTable && validSchemas.has(urlTable) && urlTable) ||
    (reduxTable && validSchemas.has(reduxTable) && reduxTable) ||
    tables[0].schema;

  return (
    <Tooltip title="Select table" className="table-selector-container">
      Select Table:&nbsp;
      <Select
        className="table-selector"
        value={selected}
        onChange={(val) => navigate(`${basePath}/${val}`)}
      >
        {tables.map((t) => (
          <Option key={t.schema} value={t.schema} className="table-selector-options">
            {t.name}
          </Option>
        ))}
      </Select>
    </Tooltip>
  );
}
