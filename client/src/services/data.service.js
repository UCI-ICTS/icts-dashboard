import axios from "axios";

const APIDB = process.env.REACT_APP_APIDB;

const getAllTables = async (token) => {
  const response = await axios.get(APIDB + "/api/search/get_all_tables/", {
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    }
  });
  return response;
}

const updateParticipant = async (data, token) => {
  const response = await axios.post(APIDB + "/api/metadata/submit_participants/", [
    data
  ], {
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    }
  });
  return response;
}

const updateFamily = async (data, token) => {
  const response = await axios.post(APIDB + "/api/metadata/submit_families/", [
    data
  ], {
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    }
  });
  return response;
}


const updateGeneticFindings = async (data, token) => {
  const response = await axios.post(APIDB + "/api/metadata/submit_genetic_findings/", [
    data
  ], {
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    }
  });
  return response;
}


const updateAnalyte = async (data, token) => {
  const response = await axios.post(APIDB + "/api/metadata/submit_analyte/", [
    data
  ], {
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    }
  });
  return response;
}


const updateExperiment = async (data, token) => {
  const response = await axios.post(APIDB + "/api/metadata/submit_experiment/", [
    data
  ], {
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    }
  });
  return response;
}


const updatePhenotype = async (data, token) => {
  const response = await axios.post(APIDB + "/api/metadata/submit_phenotype/", [
    data
  ], {
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    }
  });
  return response;
}


const dataService = {
  updateExperiment,
  updatePhenotype,
  updateAnalyte,
  updateGeneticFindings,
  updateFamily,  
  updateParticipant,
  getAllTables
}

  export default dataService;