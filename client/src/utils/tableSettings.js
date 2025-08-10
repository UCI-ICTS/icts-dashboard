// src/utils/useTableSettings.js
import { useEffect, useMemo, useState, useCallback } from "react";

export function useTableSettings({ schema, tableKey, defaults = [] }) {
  const keys = useMemo(() => Object.keys(schema?.properties || {}), [schema]);

  const [visible, setVisible] = useState({});
  const [widths, setWidths] = useState({});
  const [sorter, setSorter] = useState(null);      // optional future
  const [filters, setFilters] = useState({});      // optional future

  // init + hydrate
  useEffect(() => {
    const saved = JSON.parse(localStorage.getItem(`columns:${tableKey}`) || "{}");
    // const saved = {};
    const nextVisible = keys.reduce((acc, k) => {
      const savedVis = saved.visible?.[k];
      acc[k] = savedVis != null ? savedVis : (defaults.length ? defaults.includes(k) : true);
      return acc;
    }, {});
    const nextWidths = keys.reduce((acc, k) => {
      acc[k] = saved.widths?.[k] ?? 180;
      return acc;
    }, {});
    setVisible(nextVisible);
    setWidths(nextWidths);
  }, [tableKey, keys, defaults]);

  // persist
  useEffect(() => {
    localStorage.setItem(`columns:${tableKey}`, JSON.stringify({ visible, widths }));
  }, [tableKey, visible, widths]);

  // actions
  const toggleColumn = useCallback((k, on) => {
    setVisible((v) => ({ ...v, [k]: on }));
  }, []);

  const toggleAll = useCallback((on) => {
    setVisible((v) => Object.fromEntries(Object.keys(v).map((k) => [k, on])));
  }, []);

  const reset = useCallback(() => {
    setVisible(keys.reduce((acc, k) => {
      acc[k] = defaults.length ? defaults.includes(k) : true;
      return acc;
    }, {}));
    setWidths(keys.reduce((acc, k) => ({ ...acc, [k]: 180 }), {}));
    setSorter(null);
    setFilters({});
  }, [keys, defaults]);

  const setWidth = useCallback((k, w) => {
    setWidths((prev) => ({ ...prev, [k]: Math.max(80, w) }));
  }, []);

  return {
    // state
    keys, visible, widths, sorter, filters,
    // actions
    toggleColumn, toggleAll, reset, setWidth, setSorter, setFilters,
  };
}

export function buildColumns({ schema, visible, widths, onResize }) {
  const entries = Object.entries(schema?.properties || {});
  const cols = entries
    .map(([key, prop]) => ({
      key,
      dataIndex: key,
      title: prop?.title || key,
      width: widths[key] ?? 180,
      // AntD header resize hook is attached by the view, not here
    }))
    .filter((c) => visible[c.key]);

  return cols;
}
