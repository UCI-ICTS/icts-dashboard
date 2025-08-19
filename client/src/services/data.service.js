// src/services/data.service.js

import axios from "axios";
import { store } from "../store";
import api from "../api";


const APIDB = process.env.REACT_APP_APIDB;
const metadata = ["participant", "family", "genetic_findings", "analyte", "biobank", "phenotype"]

const getAuthHeaders = () => {
  const state = store.getState(); // Get Redux state
  const token = state.account.user.access_token; // Retrieve the latest token from Redux

  if (!token) {
    throw new Error("No authentication token found.");
  }

  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
};

const getAllTables = async () => {
  const response = await axios.get(`${APIDB}api/search/get_all_tables/`, {
    headers: getAuthHeaders(),
  });
  return response;
}

const familyDetail = async (participant_id) => {
    const response = await axios.get(APIDB + `api/search/family_detail/?ids=${participant_id}`, {headers: getAuthHeaders()})
    return response
}

const fetchTable = async (table) => {
  if (metadata.includes(table)) {
    const response = await axios.get(APIDB + `api/metadata/${table}/all/`, {headers: getAuthHeaders()})
    return response
  } else {
    const response = await axios.get(APIDB + `api/experiments/${table}/all/`, {headers: getAuthHeaders()})
    return response
  }
}

const createEntry = async (table, data) => {
  if (metadata.includes(table)) {
    const response = await axios.post(APIDB + `api/metadata/${table}/create/`, data, {headers: getAuthHeaders()})
    return response
  } else {
    const response = await axios.post(APIDB + `api/experiments/${table}/create/`, data, {headers: getAuthHeaders()})
    return response
  }
}

const updateEntry = async (table, data) => {
  if (metadata.includes(table)) {
    const response = await axios.post(APIDB + `api/metadata/${table}/update/`, data, {headers: getAuthHeaders()})
    return response
  } else {
    const response = await axios.post(APIDB + `api/experiments/${table}/update/`, data, {headers: getAuthHeaders()})
    return response
  }
}

const deleteEntry = async (table, idList) => {
  if (metadata.includes(table)) {
    const response = await axios.delete(APIDB + `api/metadata/${table}/delete/?ids=${idList}`, {
      headers: getAuthHeaders()
    })
    return response
  } else {
    const response = await axios.delete(APIDB + `api/experiments/${table}/delete/?ids=${idList}`, {
      headers: getAuthHeaders()
    })
    return response
  }
}

const dataService = {
  createEntry,
  familyDetail,
  fetchTable,
  updateEntry,
  deleteEntry,
  getAllTables
}

export default dataService;