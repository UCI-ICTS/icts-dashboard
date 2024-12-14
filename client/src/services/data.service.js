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

const getAllParticipants = async () => {
  console.log("participoants service")
  const response = await axios.get("http://localhost:8000/api/metadata/get_all_participants/", {
    headers: {
      "Content-Type": "application/json"
    }
  });
  return response;
}


const dataService = {
    submitParticipant,
    getAllParticipants
}

  export default dataService;