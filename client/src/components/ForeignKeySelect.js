// src/components/ForeignKeySelect.js
import { useEffect, useMemo, useRef } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Select } from "antd";
import { fetchTable } from "../slices/dataSlice";
import { foreignKeyFields } from "../utils/schemaAndTables";

// Works as a direct child of <Form.Item>, which injects value/onChange.
export default function ForeignKeySelect({ table, field, value, onChange, ...rest }) {
  const dispatch = useDispatch();
  const fk = foreignKeyFields[table]?.[field];
  const rows = useSelector((s) => (fk ? s.data[fk.sourceTable] : undefined));
  const fetchedRef = useRef(false);

  useEffect(() => {
    if (!fk || fetchedRef.current) return;
    if (rows === undefined) {
      console.warn(`No state.data.${fk.sourceTable} (foreignKeyFields.${table}.${field})`);
      return;
    }
    if (rows.length === 0) {
      fetchedRef.current = true;
      dispatch(fetchTable(fk.apiKey));
    }
  }, [dispatch, fk, rows, table, field]);

  const options = useMemo(
    () => (fk ? (rows || []).map((r) => {
      const v = String(r[fk.valueKey] ?? "");
      return { value: v, label: v };
    }) : []),
    [rows, fk]
  );

  return (
    <Select
      showSearch
      allowClear
      value={value}
      onChange={onChange}
      options={options}
      optionFilterProp="label"
      {...rest}
    />
  );
}