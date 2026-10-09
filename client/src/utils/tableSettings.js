// src/utils/useTableSettings.js
import { useEffect, useMemo, useState, useCallback, useRef } from "react";

const NOOP_STORAGE = { getItem: () => null, setItem: () => {}, removeItem: () => {} };

export function useTableSettings({
  schema,
  tableKey,
  defaults = [],
  persist = false,        // <-- NEW
  storagePrefix = "columns" // optional namespace
}) {
  const keys = useMemo(() => Object.keys(schema?.properties || {}), [schema]);
  const storage = useMemo(() => (persist ? localStorage : NOOP_STORAGE), [persist]);

  // Compare defaults by content, not by reference
  const defaultsSig = defaults.join("|");
  const stableDefaults = useMemo(
    () => (defaultsSig ? defaultsSig.split("|") : []),
    [defaultsSig]
  );

  // Compare keys by content too, so a fresh-but-identical schema can't retrigger
  const keysSig = keys.join("|");

  const storageKey = `${storagePrefix}:${tableKey}`;
  const hydratedKey = useRef(null);

  const [visible, setVisible] = useState({});
  const [widths, setWidths] = useState({});
  const [sorter, setSorter] = useState(null);   // { key, order } | null
  const [filters, setFilters] = useState({});   // { [key]: string }

  // init + hydrate
  useEffect(() => {
    let saved = {};
    try { saved = JSON.parse(storage.getItem(storageKey) || "{}"); } catch {}

    setVisible(keys.reduce((acc, k) => {
      const savedVis = saved.visible?.[k];
      acc[k] = savedVis != null ? savedVis : (stableDefaults.length ? stableDefaults.includes(k) : true);
      return acc;
    }, {}));
    setWidths(keys.reduce((acc, k) => { acc[k] = saved.widths?.[k] ?? 180; return acc; }, {}));

    const validKeys = new Set(keys);
    setFilters(
      Object.fromEntries(
        Object.entries(saved.filters ?? {}).filter(([k]) => validKeys.has(k))
      )
    );
    setSorter(saved.sorter && validKeys.has(saved.sorter.key) ? saved.sorter : null);

    setFilters(saved.filters ?? {});
    hydratedKey.current = storageKey;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [storageKey, keysSig, defaultsSig, storage]);

  // persist, but only once state belongs to the current table
  useEffect(() => {
    if (hydratedKey.current !== storageKey) return;
    try {
      storage.setItem(storageKey, JSON.stringify({ visible, widths, sorter, filters }));
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
      acc[k] = stableDefaults.length ? stableDefaults.includes(k) : true;
      return acc;
    }, {}));
    setWidths(keys.reduce((acc, k) => ({ ...acc, [k]: 180 }), {}));
    setSorter(null);
    setFilters({});
  }, [keys, stableDefaults]);

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
