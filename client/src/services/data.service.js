// src/servcices/data.service.js

import api from "../api";

// Generic helper for POST array-wrapped data
const postArray = (url, data) => api.post(url, [data]); // returns full response

// Fetch all tables
const getAllTables = () => api.get("search/get_all_tables/"); // returns full response

// =======================
// Update functions
// =======================

const updateParticipant = (data) => postArray("metadata/participant/update/", data);
const updateFamily = (data) => postArray("metadata/family/update/", data);
const updateGeneticFindings = (data) => postArray("metadata/genetic_findings/update/", data);
const updateAnalyte = (data) => postArray("metadata/analyte/update/", data);
const updateBiobankEntries = (data) => postArray("metadata/biobank/update/", data);
const updatePhenotype = (data) => postArray("metadata/phenotype/update/", data);
const updateExperiment = (data) => postArray("experiments/submit_experiment/", data);
const updateExperimentStage = (data) => postArray("metadata/experiment_stage/update/", data);
const updateDnaShortRead = (data) => postArray("experiments/experiment_dna_short_read/update/", data);
const updateRnaShortRead = (data) => postArray("experiments/experiment_rna_short_read/update/", data);
const updatePacBio = (data) => postArray("experiments/pac_bio/update/", data);
const updateNanoPore = (data) => postArray("experiments/nanopore/update/", data);

// =======================
// Create functions
// =======================

const createParticipant = (data) => postArray("metadata/participant/create/", data);
const createFamily = (data) => postArray("metadata/family/create/", data);
const createGeneticFindings = (data) => postArray("metadata/genetic_findings/create/", data);
const createAnalyte = (data) => postArray("metadata/analyte/create/", data);
const createBiobankEntries = (data) => postArray("metadata/biobank/create/", data);
const createPhenotype = (data) => postArray("metadata/phenotype/create/", data);
const createExperiment = (data) => postArray("experiments/submit_experiment/", data);
const createExperimentStage = (data) => postArray("metadata/experiment_stage/create/", data);
const createDnaShortRead = (data) => postArray("experiments/experiment_dna_short_read/create/", data);
const createRnaShortRead = (data) => postArray("experiments/experiment_rna_short_read/create/", data);
const createPacBio = (data) => postArray("experiments/pac_bio/create/", data);
const createNanoPore = (data) => postArray("experiments/nanopore/create/", data);

// Export all services
const dataService = {
  getAllTables,
  updateParticipant,
  updateFamily,
  updateGeneticFindings,
  updateAnalyte,
  updateBiobankEntries,
  updatePhenotype,
  updateExperiment,
  updateExperimentStage,
  updateDnaShortRead,
  updateRnaShortRead,
  updatePacBio,
  updateNanoPore,
  createParticipant,
  createFamily,
  createGeneticFindings,
  createAnalyte,
  createBiobankEntries,
  createPhenotype,
  createExperiment,
  createExperimentStage,
  createDnaShortRead,
  createRnaShortRead,
  createPacBio,
  createNanoPore,
};

export default dataService;
