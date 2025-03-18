// src/slices/dataSlice.test.js

import { configureStore } from "@reduxjs/toolkit";
import { dataReducer, setTableView, setJsonData } from "./dataSlice";

describe("dataSlice", () => {
  let store;

  beforeEach(() => {
    store = configureStore({ reducer: { data: dataReducer } });
  });

  it("should return the initial state", () => {
    expect(store.getState().data).toMatchObject({
      tableView: "participants",
      jsonData: [],
      status: "idle",
    });
  });

  it("should update table view", () => {
    store.dispatch(setTableView({ schema: "new_view", identifier: "new_id", name: "New Table" }));
    expect(store.getState().data.tableView).toBe("new_view");
  });

  it("should update JSON data", () => {
    const mockData = [{ id: 1, name: "Test" }];
    store.dispatch(setJsonData(mockData));
    expect(store.getState().data.jsonData).toEqual(mockData);
  });
});
