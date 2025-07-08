// src/services/data.service.js

import axios from "axios";
import { store } from "../store";
import api from "../api";


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


const createFamily = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/family/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const createExpDnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/experiment_dna_short_read/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const createExpRnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/experiment_rna_short_read/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const createExpPacBio = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/experiment_pac_bio/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const createExpNanopore = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/experiment_nanopore/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const createAligned = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/alignment/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const createAlnDnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/alignment_dna_short_read/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const createAlnRnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/alignment_rna_short_read/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const createAlnPacBio = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/alignment_pac_bio/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const createAlnNanopore = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/alignment_nanopore/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const getAllTables = async () => {
  const response = await axios.get(`${APIDB}api/search/get_all_tables/`, {
    headers: getAuthHeaders(),
  });
  return response;
}

const createParticipant = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/participant/create/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const updateAlnRnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/aligned_rna_short_read/update/", [
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
  const response = await axios.post(APIDB + "api/metadata/analyte/create/", [
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

const updateEntry = async (table, data) => {
  const metadata = ["participant", "family", "genetic_findings", "analyte", "biobank", "phenotype"]

  if (metadata.includes(table)) {
    const response = await axios.post(APIDB + `api/metadata/${table}/update/`, [data], {headers: getAuthHeaders()})
    console.log("response: ", response)
    return response
  } else {
    const response = await axios.post(APIDB + `api/experiments/${table}/update/`, [data], {headers: getAuthHeaders()})
    console.log("response: ", response)
    return response
  }
}


const deleteEntry = async (table, idList) => {
  const metadata = ["participant", "family", "genetic_findings", "analyte", "biobank", "phenotype"]

  if (metadata.includes(table)) {
    const response = await axios.delete(APIDB + `api/metadata/${table}/delete/?ids=${idList}`, {
      headers: getAuthHeaders()
    })
    console.log("response: ", response)
    return response
  } else {
    const response = await axios.delete(APIDB + `api/experiments/${table}/delete/?ids=${idList}`, {
      headers: getAuthHeaders()
    })
    console.log("response: ", response)
    return response
  }
}

const dataService = {
  createAnalyte,
  createBiobankEntries,
  createDnaShortRead,
  createExperiment,
  createFamily,
  createParticipant,
  createPhenotype,
  createRnaShortRead,
  updateEntry,
  deleteEntry,
  getAllTables
}

export default dataService;