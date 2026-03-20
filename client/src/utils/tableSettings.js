// src/utils/useTableSettings.js
import { useEffect, useMemo, useState, useCallback } from "react";

export function useTableSettings({
  schema,
  tableKey,
  defaults = [],
  persist = false,        // <-- NEW
  storagePrefix = "columns" // optional namespace
}) {
  const keys = useMemo(() => Object.keys(schema?.properties || {}), [schema]);
  const storage = persist ? localStorage : {
    getItem: () => null,
    setItem: () => {},
    removeItem: () => {}
  };

  const storageKey = `${storagePrefix}:${tableKey}`;

  const [visible, setVisible] = useState({});
  const [widths, setWidths] = useState({});
  const [sorter, setSorter] = useState(null);   // { key, order } | null
  const [filters, setFilters] = useState({});   // { [key]: string }

  // init + hydrate
  useEffect(() => {
    let saved = {};
    try {
      saved = JSON.parse(storage.getItem(storageKey) || "{}");
    } catch {}

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
    setSorter(saved.sorter ?? null);
    setFilters(saved.filters ?? {});
  }, [tableKey, keys, defaults, storageKey, storage]);

  // persist (debounced-ish write)
  useEffect(() => {
    const payload = JSON.stringify({ visible, widths, sorter, filters });
    try {
      storage.setItem(storageKey, payload);
    } catch {}
  }, [storage, storageKey, visible, widths, sorter, filters]);

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

  const clearSaved = useCallback(() => {
    try { storage.removeItem(storageKey); } catch {}
  }, [storage, storageKey]);

  return {
    // state
    keys, visible, widths, sorter, filters,
    // actions
    toggleColumn, toggleAll, reset, setWidth, setSorter, setFilters, clearSaved,
  };
}

export function buildColumns({ schema, visible, widths }) {
  const entries = Object.entries(schema?.properties || {});
  return entries
    .map(([key, prop]) => ({
      key,
      dataIndex: key,
      title: prop?.title || key,
      width: widths[key] ?? 180,
    }))
    .filter((c) => visible[c.key]);
}
