// src/components/BoardSelector.js

import "../App.css";
import { useEffect } from "react";
import { Select, Tooltip } from "antd";
import { useNavigate, useParams } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { setActiveBoardId } from "../slices/uiSlice";
import { useMemo } from "react";

const { Option } = Select;

export default function BoardSelector() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { boardId: urlBoard } = useParams();
  
  const activeBoardId = useSelector((state) => state.ui?.activeBoardId);
  const activeBoards = useSelector((state) => state.ui?.activeBoard ?? {});
  const allIds = useSelector((state) => state.ui?.allIds ?? []);

  // Build [{id, title}, ...] in the order defined by ui.allIds
  const boards = useMemo(
    () => allIds.map((id) => activeBoards[id]).filter(Boolean),
    [allIds, activeBoards]
    );

  // Use URL if present, otherwise fall back to redux, otherwise first board
  const selectedId = urlBoard || activeBoardId || boards?.[0]?.id;
  
    // Keep redux in sync when URL changes
  useEffect(() => {
    if (urlBoard && urlBoard !== activeBoardId) {
      dispatch(setActiveBoardId(urlBoard));
    }
  }, [urlBoard, activeBoardId, dispatch]);

    // If user lands on /dashboard/board-view (no id), push them to a real board
  useEffect(() => {
    if (!urlBoard && boards.length && selectedId) {
      navigate(`/dashboard/board-view/${selectedId}`, { replace: true });
      dispatch(setActiveBoardId(selectedId));
    }
  }, [urlBoard, boards.length, selectedId, navigate, dispatch]);
  
  return (
    <Tooltip title="Select board" className="table-selector-container">
      Select Board:&nbsp;
      <Select
        className="table-selector"
        value={selectedId}
        onChange={(val) => {
          navigate(`/dashboard/board-view/${val}`)}
        }
      >
        {boards.map((b) => (
          <Option key={b.id} value={b.id} className="table-selector-options">
            {b.title}
          </Option>
        ))}
      </Select>
    </Tooltip>
  );
}