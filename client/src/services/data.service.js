import axios from "axios";

const getAllTables = async (token) => {
  const response = await axios.get("http://localhost:8000/api/metadata/get_all_tables/", {
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    }
  });
  return response;
}

const updateParticipant = async (data, token) => {
  const response = await axios.post("http://localhost:8000/api/metadata/submit_participants/", [
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
  const response = await axios.post("http://localhost:8000/api/metadata/submit_families/", [
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
  const response = await axios.post("http://localhost:8000/api/metadata/submit_genetic_findings/", [
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
  updateGeneticFindings,
  updateFamily,  
  updateParticipant,
  getAllTables
}

  export default dataService;