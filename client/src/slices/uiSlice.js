// src/slices/uiSlice.js
import { createSlice } from "@reduxjs/toolkit";
import schemas from '../schemas/v1.10schemas.json';
/**
 * Returns true if an object matches a simple {field: value} matcher.
 * - If matcher is empty, returns true.
 * - Strict equality is used.
 */
function matches(obj, matcher = {}) {
  return Object.entries(matcher).every(([k, v]) => obj?.[k] === v);
}

/**
 * Build lane ids for a board by filtering items from the source table.
 * Preserves any existing manual order already present in lane.ids.
 * - Keeps existing ids that still match
 * - Appends new matching ids that were not previously present
 */
function buildLaneIds({ lane, items, idKey }) {
  const matchingIds = items
    .filter((it) => matches(it, lane.match))
    .map((it) => it[idKey])
    .filter(Boolean);

  const existing = Array.isArray(lane.ids) ? lane.ids : [];

  // Keep existing ids that still match
  const kept = existing.filter((id) => matchingIds.includes(id));

  // Append any new ones
  const added = matchingIds.filter((id) => !kept.includes(id));

  return [...kept, ...added];
}

const initialState = {
  activeBoardId: "biobank-shipping",
  activeBoard: {
    "case-queue": {
      id: "case-queue",
      title: "Case Queue",
      source: { table: "participants", idKey: "participant_id" },
      laneKey: "solve_status",
      lanes: schemas.participants.properties.solve_status.enum,
      // {
      //   unsolved: { title: "Unsolved", match: { solve_status: "Unsolved" }, ids: [] },
      //   in_review: { title: "In review", match: { needs_review: true }, ids: [] },
      //   solved: { title: "Solved", match: { solve_status: "Solved" }, ids: [] },
      // },
      laneOrder: ["unsolved", "in_review", "solved"],
    },
    "biobank-shipping": {
      id: "biobank-shipping",
      title: "Biobank Shipping",
      source: { table: "biobank_entries", idKey: "biobank_id" },
      laneKey: "status",
      lanes: schemas.biobank_entries.properties.status.enum,
      laneOrder: [],
    },
  },
  allIds: ["case-queue", "biobank-shipping"],
};

const uiSlice = createSlice({
  name: "ui",
  initialState,
  reducers: {
    setActiveBoardId(state, action) {
      state.activeBoardId = action.payload;
    },

    /**
     * Syncs a single board's lane ids from items passed in.
     * You call this after you load participants (or any source table).
     */
    syncBoardFromItems(state, action) {
      const { boardId, items } = action.payload;
      const board = state.byId[boardId];
      if (!board) return;

      const { idKey } = board.source;
      for (const laneId of board.laneOrder) {
        const lane = board.lanes[laneId];
        if (!lane) continue;
        lane.ids = buildLaneIds({ lane, items, idKey });
      }
    },

    /**
     * Move a card from one lane to another (or within same lane).
     * This is what your DnD handler will dispatch.
     */
    moveCard(state, action) {
      const { boardId, fromLaneId, toLaneId, cardId, toIndex } = action.payload;
      const board = state.byId[boardId];
      if (!board) return;

      const fromLane = board.lanes[fromLaneId];
      const toLane = board.lanes[toLaneId];
      if (!fromLane || !toLane) return;

      // remove from source lane
      fromLane.ids = (fromLane.ids || []).filter((id) => id !== cardId);

      // insert into target lane
      const next = [...(toLane.ids || [])].filter((id) => id !== cardId);
      const idx = typeof toIndex === "number" ? Math.max(0, Math.min(toIndex, next.length)) : next.length;
      next.splice(idx, 0, cardId);
      toLane.ids = next;
    },
  },
});

export const { setActiveBoardId, syncBoardFromItems, moveCard } = uiSlice.actions;
export const uiReducer = uiSlice.reducer;