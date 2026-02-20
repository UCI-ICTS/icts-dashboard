// src/pages/CaseQue.js
import React, { useMemo, useState, useEffect } from "react";
import { useSelector /*, useDispatch*/ } from "react-redux";
import { DndContext } from "@dnd-kit/core";
import { Layout, Typography, Select } from "antd";

import Droppable from "../components/Droppable";
import Draggable from "../components/Draggable";
import BoardSelector from "../components/BoardSelector";

const { Header } = Layout;
const { Title } = Typography;
const { Option } = Select;

// Placeholder for now. Replace later with:
// dispatch(updateEntry({ table: "biobank", data: [payload] }))
function dispatchUpdateStatusPlaceholder({ biobank_id, nextStatus, payload }) {
  console.log("[TODO dispatch] biobank status change", {
    biobank_id,
    nextStatus,
    payload,
  });
}

export default function CaseQue() {
  // const dispatch = useDispatch();
  
  // Pull Board info
  const activeBoardId = useSelector((state) => state.ui.activeBoardId || []);
  const activeBoard = useSelector((state) => state.ui.activeBoard[activeBoardId]);
  
  // Pull source table dynamically
  const sourceTable = activeBoard?.source?.table
  const sourceKey = activeBoard?.source?.key
  const rows = useSelector((state) => sourceTable ? state.data?.[sourceTable] : []);
  
  // local lane state
  const laneOrder = activeBoard?.laneOrder || []
  
  const [laneById, setLaneById] = useState({});

  // initialize / re-initialize local lanes from redux data
  useEffect(() => {
    if (!activeBoard || !sourceKey) return;

    const initial = {};
    for (const row of rows) {
      if (!row?.biobank_id) continue;
      // fall back to a reasonable default if status missing/blank
      initial[row.biobank_id] = row.status || "Pending shipment";
    }
    setLaneById(initial);
  }, [rows]);

  const lanes = activeBoard.lanes;

  // handy lookup by id for payload building
  const byId = useMemo(() => {
    const map = {};
    for (const row of rows) {
      if (row?.biobank_id) map[row.biobank_id] = row;
    }
    return map;
  }, [rows]);

  const cardIds = useMemo(() => Object.keys(laneById), [laneById]);

  const handleDragEnd = ({ active, over }) => {
    const biobank_id = active?.id;
    const nextStatus = over?.id;

    if (!biobank_id || !nextStatus) return;

    const prevStatus = laneById[biobank_id];
    if (prevStatus === nextStatus) return;

    // optimistic UI update
    setLaneById((prev) => ({ ...prev, [biobank_id]: nextStatus }));

    // build payload for DB update (placeholder dispatch for now)
    const existing = byId[biobank_id] || {};

    // IMPORTANT: don't send shipment_date: "" if your backend rejects it.
    // If you later dispatch, prefer omitting blank fields or converting "" -> null.
    const payload = {
      ...existing,
      biobank_id,
      status: nextStatus,
      ...(existing.shipment_date === "" ? { shipment_date: null } : {}),
    };

    dispatchUpdateStatusPlaceholder({ biobank_id, nextStatus, payload });

    // Later:
    // dispatch(updateEntry({ table: "biobank", data: [payload] }));
  };
  console.log(activeBoard, rows)
  return (
    <Layout className="admin-layout">
      <Header className="primary-header">
        <Title className="primary-title">Kanban Boards</Title>
      </Header>
      <BoardSelector/>
      <DndContext
        onDragStart={(e) => console.log("drag start", e.active?.id)}
        onDragOver={(e) => console.log("drag over", e.active?.id, "->", e.over?.id)}
        onDragEnd={handleDragEnd}
      >
        <div style={{ padding: 12 }}>
          <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>
            Biobank Shipping Board
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(5, minmax(220px, 1fr))",
              gap: 12,
              overflowX: "auto",
              paddingBottom: 8,
            }}
          >
            {lanes.map((laneId) => (
              <div
                key={laneId}
                style={{
                  padding: 12,
                  border: "1px solid #eee",
                  borderRadius: 12,
                  background: "#fff",
                  minWidth: 220,
                }}
              >
                <div style={{ fontWeight: 600, marginBottom: 8 }}>{laneId}</div>

                <Droppable id={laneId}>
                  {cardIds
                    .filter((id) => laneById[id] === laneId)
                    .map((id) => {
                      const row = byId[id] || {};
                      return (
                        <Draggable key={id} id={id} style={{ marginBottom: 8 }}>
                          <div
                            style={{
                              padding: 10,
                              border: "1px solid #ddd",
                              borderRadius: 10,
                              background: "#fafafa",
                            }}
                          >
                            <div style={{ fontWeight: 600 }}>{row.biobank_id}</div>
                            <div style={{ fontSize: 12, opacity: 0.8 }}>
                              Participant: {row.participant_id || "-"}
                            </div>
                            <div style={{ fontSize: 12, opacity: 0.8 }}>
                              Specimen: {row.specimen_type || "-"}
                            </div>
                          </div>
                        </Draggable>
                      );
                    })}
                </Droppable>
              </div>
            ))}
          </div>
        </div>
      </DndContext>
    </Layout>
  );
}