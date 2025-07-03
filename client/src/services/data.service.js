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


const createFamily = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/family/create/", [
    data
  ], {
    headers: getAuthHeaders()
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

const createPhenotype = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/phenotype/create/", [
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

const createGeneticFindings = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/genetic_findings/create/", [
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

const createExperiment = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/experiment/create/", [
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


const getFamilyTable = async (data, token) => {
  const response = await axios.post(APIDB + "api/search/get_family_table/", {
    headers: getAuthHeaders()
  });
  return response;
}

const getParticipantTable = async (data, token) => {
  const response = await axios.post(APIDB + "api/search/get_participant_table/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const getPhenotypeTable = async (data, token) => {
  const response = await axios.post(APIDB + "api/search/get_phenotype_table/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const getAnalyteTable = async (data, token) => {
  const response = await axios.post(APIDB + "api/search/get_analyte_table/", {
    headers: getAuthHeaders()
  });
  return response;
}

const getGeneticFindingsTable = async (data, token) => {
  const response = await axios.post(APIDB + "api/search/get_genetic_findings_table/", {
    headers: getAuthHeaders()
  });
  return response;
}

const getBiobankEntriesTable = async (data, token) => {
  const response = await axios.post(APIDB + "api/search/get_biobank_table/", {
    headers: getAuthHeaders()
  });
  return response;
}

const getExperimentTable = async (data, token) => {
  const response = await axios.post(APIDB + "api/search/get_experiment_table/", {
    headers: getAuthHeaders()
  });
  return response;
}

const getExpDnaShortReadTable = async (data, token) => {
  const response = await axios.post(APIDB + "api/search/get_experiment_dna_short_read_table/", {
    headers: getAuthHeaders()
  });
  return response;
}

const getExpRnaShortReadTable = async (data, token) => {
  const response = await axios.post(APIDB + "api/search/get_experiment_rna_short_read_table/", {
    headers: getAuthHeaders()
  });
  return response;
}


const getExpPacBioTable = async (data, token) => {
  const response = await axios.post(APIDB + "api/search/get_experiment_pac_bio_table/", {
    headers: getAuthHeaders()
  });
  return response;
}

const getExpNanoporeTable = async (data, token) => {
  const response = await axios.post(APIDB + "api/search/get_experiment_nanopore_table/", {
    headers: getAuthHeaders()
  });
  return response;
}

const getAlignedTable = async (data, token) => {
  const response = await axios.post(APIDB + "api/search/get_aligned_table/", {
    headers: getAuthHeaders()
  });
  return response;
}

const getAlnDnaShortReadTable = async (data, token) => {
  const response = await axios.post(APIDB + "api/search/get_aligned_dna_short_read_table/", {
    headers: getAuthHeaders()
  });
  return response;
}

const getAlnRnaShortReadTable = async (data, token) => {
  const response = await axios.post(APIDB + "api/search/get_aligned_rna_short_read_table/", {
    headers: getAuthHeaders()
  });
  return response;
}

const getAlnPacBioTable = async (data, token) => {
  const response = await axios.post(APIDB + "api/search/get_aligned_pac_bio_table/", {
    headers: getAuthHeaders()
  });
  return response;
}

const getAlnNanoporeTable = async (data, token) => {
  const response = await axios.post(APIDB + "api/search/get_aligned_nanopore_table/", {
    headers: getAuthHeaders()
  });
  return response;
}


const updateFamily = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/family/update/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const updateParticipant = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/participant/update/", [
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

const updateAnalyte = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/analyte/update/", [
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

const updateBiobankEntries = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/biobank/update/", [
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

const updateExpDnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/experiment_dna_short_read/update/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const updateExpRnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/experiment_rna_short_read/update/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const updateExpPacBio = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/experiment_pac_bio/update/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const updateExpNanopore = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/experiment_nanopore/update/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const updateAligned = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/submit_experiment/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const updateAlnDnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/aligned_dna_short_read/update/", [
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

const updateAlnPacBio = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/aligned_pac_bio/update/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const updateAlnNanopore = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/aligned_nanopore/update/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const deleteFamily = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/family/delete/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const deleteParticipant = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/participant/delete/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const deletePhenotype = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/phenotype/delete/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const deleteAnalyte = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/analyte/delete/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const deleteGeneticFindings = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/genetic_findings/delete/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const deleteBiobankEntries = async (data, token) => {
  const response = await axios.post(APIDB + "api/metadata/biobank/delete/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const deleteExperiment = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/submit_experiment/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const deleteExpDnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/experiment_dna_short_read/delete/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const deleteExpRnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/experiment_rna_short_read/delete/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const deleteExpPacBio = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/experiment_pac_bio/delete/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const deleteExpNanopore = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/experiment_nanopore/delete/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const deleteAligned = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/submit_experiment/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const deleteAlnDnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/aligned_dna_short_read/delete/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const deleteAlnRnaShortRead = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/aligned_rna_short_read/delete/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const deleteAlnPacBio = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/aligned_pac_bio/delete/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}

const deleteAlnNanopore = async (data, token) => {
  const response = await axios.post(APIDB + "api/experiments/aligned_nanopore/delete/", [
    data
  ], {
    headers: getAuthHeaders()
  });
  return response;
}


const dataService = {
  createFamily,
  createParticipant,
  createPhenotype,
  createAnalyte,
  createGeneticFindings,
  createBiobankEntries,

  createExperiment,
  createExpDnaShortRead,
  createExpRnaShortRead,
  createExpPacBio,
  createExpNanopore,

  createAligned,
  createAlnDnaShortRead,
  createAlnNanopore,
  createAlnPacBio,
  createAlnRnaShortRead,

  getAllTables,

  getFamilyTable,
  getParticipantTable,
  getPhenotypeTable,
  getAnalyteTable,
  getGeneticFindingsTable,
  getBiobankEntriesTable,

  getExperimentTable,
  getExpDnaShortReadTable,
  getExpRnaShortReadTable,
  getExpPacBioTable,
  getExpNanoporeTable,

  getAlignedTable,
  getAlnDnaShortReadTable,
  getAlnRnaShortReadTable,
  getAlnPacBioTable,
  getAlnNanoporeTable,

  updateFamily,
  updateParticipant,
  updatePhenotype,
  updateAnalyte,
  updateGeneticFindings,
  updateBiobankEntries,

  updateExperiment,
  updateExpDnaShortRead,
  updateExpRnaShortRead,
  updateExpPacBio,
  updateExpNanopore,

  updateAligned,
  updateAlnDnaShortRead,
  updateAlnRnaShortRead,
  updateAlnPacBio,
  updateAlnNanopore,

  deleteFamily,
  deleteParticipant,
  deletePhenotype,
  deleteAnalyte,
  deleteGeneticFindings,
  deleteBiobankEntries,

  deleteExperiment,
  deleteExpDnaShortRead,
  deleteExpRnaShortRead,
  deleteExpPacBio,
  deleteExpNanopore,

  deleteAligned,
  deleteAlnDnaShortRead,
  deleteAlnRnaShortRead,
  deleteAlnPacBio,
  deleteAlnNanopore,
}

export default dataService;