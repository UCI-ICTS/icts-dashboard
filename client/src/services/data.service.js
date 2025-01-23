import axios from "axios";

const submitParticipant = async (data) => {
  console.log("service",data)
  const response = await axios.post("http://localhost:8000/metadata/submit_participant/", {
      "participant_list": data
  }, {
    headers: {
      "Content-Type": "application/json"
    }
  });
  return response;
}

const getAllTables = async (token) => {
  console.log("service",token)
  const response = await axios.get("http://localhost:8000/api/metadata/get_all_tables/", {
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    }
  });
  return response;
}

const updateParticipant = async (data, token) => {
  console.log("service",token)
  const response = await axios.post("http://localhost:8000/api/metadata/update_participants/", [
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
    updateParticipant,
    getAllTables
}

  export default dataService;