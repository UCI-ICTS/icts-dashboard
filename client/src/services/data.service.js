// src/services/data.service.js

import axios from "axios";
import { store } from "../store";


const APIDB = process.env.REACT_APP_APIDB;

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
};

const updateParticipant = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/update_participants/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const updateFamily = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/update_families/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const updateGeneticFindings = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/update_genetic_findings/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const updateAnalyte = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/update_analytes/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const updatePhenotype = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/update_phenotype/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const updateExperiment = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/submit_experiment/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const updateDnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/update_experiment_dna_short_read/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const updateRnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/update_experiment_rna_short_read/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const updatePacBio = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/update_pac_bio/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const updateNanoPore = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/update_nanopore/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const createParticipant = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/create_participants/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const createFamily = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/create_families/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const createGeneticFindings = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/create_genetic_findings/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const createAnalyte = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/create_analyte/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const createPhenotype = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/create_phenotype/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const createExperiment = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/submit_experiment/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const createDnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/create_experiment_dna_short_read/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const createRnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/create_experiment_rna_short_read/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const createPacBio = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/create_pac_bio/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const createNanoPore = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/create_nanopore/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const dataService = {
  updateNanoPore,
  updatePacBio,
  updateRnaShortRead,
  updateDnaShortRead,
  updateExperiment,
  updatePhenotype,
  updateAnalyte,
  updateGeneticFindings,
  updateFamily,  
  updateParticipant,
  createAnalyte,
  createDnaShortRead,
  createExperiment,
  createFamily,
  createGeneticFindings,
  createNanoPore,
  createPacBio,
  createParticipant,
  createPhenotype,
  createRnaShortRead,
  getAllTables
}

  export default dataService;