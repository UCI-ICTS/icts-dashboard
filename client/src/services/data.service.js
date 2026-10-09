// src/services/data.service.js

import axios from "axios";
import { store } from "../store";
import api from "../utils/axiosConfig";


const APIDB = process.env.REACT_APP_APIDB;
const metadata = ["family", "participant", "analyte", "phenotype", "genetic_findings", "biobank"]
const experiments = [
  "experiment_dna_short_read", "experiment_rna_short_read", "experiment_pac_bio", "experiment_nanopore",
  "aligned_dna_short_read", "aligned_rna_short_read", "aligned_pac_bio", "aligned_nanopore",
  "aligned_dna_short_read_set", "aligned_pac_bio_set", "aligned_nanopore_set",
  "called_variants_dna_short_read", "called_variants_pac_bio", "called_variants_nanopore",
]
const submodels = [
  "reported_race", "internal_project_id", "pmid_id", "twin_id",
  "library_prep_type", "prep_targets_detail", "experiment_type",
]

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
  } else if (experiments.includes(table)) {
    const response = api.get(APIDB + `api/experiments/${table}/all/`, {headers: getAuthHeaders()})
    return response
  } else if (submodels.includes(table)) {
    const response = api.get(APIDB + `api/submodels/${table}/all/`, {headers: getAuthHeaders()})
    return response
  } else {
    throw new Error(`Unknown table: ${table}`);
  }
}

const createEntry = async (table, data) => {
  if (metadata.includes(table)) {
    const response = api.post(APIDB + `api/metadata/${table}/create/`, data, {headers: getAuthHeaders()})
    return response
  } else if (experiments.includes(table)) {
    const response = api.post(APIDB + `api/experiments/${table}/create/`, data, {headers: getAuthHeaders()})
    return response
  } else if (submodels.includes(table)) {
    const response = api.post(APIDB + `api/submodels/${table}/create/`, data, {headers: getAuthHeaders()})
    return response
  } else {
    throw new Error(`Unknown table: ${table}`);
  }
}

const updateEntry = async (table, data) => {
  if (metadata.includes(table)) {
    const response = api.post(APIDB + `api/metadata/${table}/update/`, data, {headers: getAuthHeaders()})
    return response
  } else if (experiments.includes(table)) {
    const response = api.post(APIDB + `api/experiments/${table}/update/`, data, {headers: getAuthHeaders()})
    return response
  } else if (submodels.includes(table)) {
    const response = api.post(APIDB + `api/submodels/${table}/update/`, data, {headers: getAuthHeaders()})
    return response
  } else {
    throw new Error(`Unknown table: ${table}`);
  }
}

const deleteEntry = async (table, idList) => {
  if (metadata.includes(table)) {
    const response = api.delete(APIDB + `api/metadata/${table}/delete/?ids=${idList}`, {headers: getAuthHeaders()})
    return response
  } else if (experiments.includes(table)) {
    const response = api.delete(APIDB + `api/experiments/${table}/delete/?ids=${idList}`, {headers: getAuthHeaders()})
    return response
  } else if (submodels.includes(table)) {
    const response = api.delete(APIDB + `api/submodels/${table}/delete/?ids=${idList}`, {headers: getAuthHeaders()})
    return response
  } else {
    throw new Error(`Unknown table: ${table}`);
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