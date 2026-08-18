// src/services/data.service.js

import axios from "axios";
import { store } from "../store";
import api, {getAuthHeaders} from "../utils/axiosConfig";


const APIDB = process.env.REACT_APP_APIDB;
const metadata = ["participant", "family", "genetic_findings", "analyte", "biobank", "phenotype"]

const openReport = async (objectKey) => {
  const bucket = "icts-dashboard-analysis-files"
  const response = api.get(`${APIDB}api/s3/get_pre_signed_url/?bucket=${bucket}&key=${objectKey}`, {
    headers: getAuthHeaders(),
  });
  return response;
};

const familyDetail = async (participant_id) => {
    const response = api.get(APIDB + `api/search/family_detail/?ids=${participant_id}`, {headers: getAuthHeaders()})
    return response
}

const caseQueue = async (participant_id) => {
    const response = api.get(APIDB + `api/search/case_queue/?ids=${participant_id}`, {headers: getAuthHeaders()})
    return response
}

const createPhenotypeCohort = async (values) => {
    console.log("SERVICE", values)
    const response = api.post(APIDB + `api/hpo/cohorts/summary/`, values, {headers: getAuthHeaders()})
    return response
}

const fetchTable = async (table) => {
  if (metadata.includes(table)) {
    const response = api.get(APIDB + `api/metadata/${table}/all/`, {headers: getAuthHeaders()})
    return response
  } else {
    const response = api.get(APIDB + `api/experiments/${table}/all/`, {headers: getAuthHeaders()})
    return response
  }
}

const createEntry = async (table, data) => {
  if (metadata.includes(table)) {
    const response = api.post(APIDB + `api/metadata/${table}/create/`, data, {headers: getAuthHeaders()})
    return response
  } else {
    const response = api.post(APIDB + `api/experiments/${table}/create/`, data, {headers: getAuthHeaders()})
    return response
  }
}

const updateEntry = async (table, data) => {
  if (metadata.includes(table)) {
    const response = api.post(APIDB + `api/metadata/${table}/update/`, data, {headers: getAuthHeaders()})
    return response
  } else {
    const response = api.post(APIDB + `api/experiments/${table}/update/`, data, {headers: getAuthHeaders()})
    return response
  }
}

const deleteEntry = async (table, idList) => {
  if (metadata.includes(table)) {
    const response = api.delete(APIDB + `api/metadata/${table}/delete/?ids=${idList}`, {
      headers: getAuthHeaders()
    })
    return response
  } else {
    const response = api.delete(APIDB + `api/experiments/${table}/delete/?ids=${idList}`, {
      headers: getAuthHeaders()
    })
    return response
  }
}

const extractPhenotypes = async (userText) => {
  const response = api.post(APIDB + `api/hpo/extract_phenotypes/`, {"userText": userText}, {headers: getAuthHeaders()})
  return response
}

const dataService = {
  openReport,
  createEntry,
  familyDetail,
  createPhenotypeCohort,
  caseQueue,
  fetchTable,
  updateEntry,
  deleteEntry,
  extractPhenotypes
}

export default dataService;