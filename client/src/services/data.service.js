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
  const response = await axios.post(APIDB + "api/metadata/participants/update/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const updateFamily = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/families/update/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const updateGeneticFindings = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/genetic_findings/update/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const updateAnalyte = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/analytes/update/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const updateBiobankEntries = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/biobank/update/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const updatePhenotype = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/phenotype/update/", [
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


const updateExperimentStage = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/experiment_stage/update/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const updateDnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/experiment_dna_short_read/update/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const updateRnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/experiment_rna_short_read/update/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const updatePacBio = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/pac_bio/update/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const updateNanoPore = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/nanopore/update/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const createParticipant = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/participants/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const createFamily = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/families/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const createGeneticFindings = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/genetic_findings/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const createAnalyte = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/analytes/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const createBiobankEntries = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/biobank/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const createPhenotype = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/phenotype/create/", [
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


const createExperimentStage = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/experiment_stage/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const createDnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/experiment_dna_short_read/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const createRnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/experiment_rna_short_read/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const createPacBio = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/pac_bio/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const createNanoPore = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/nanopore/create/", [
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
  updateExperimentStage,
  updateExperiment,
  updatePhenotype,
  updateBiobankEntries,
  updateAnalyte,
  updateGeneticFindings,
  updateFamily,
  updateParticipant,
  createAnalyte,
  createBiobankEntries,
  createDnaShortRead,
  createExperimentStage,
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