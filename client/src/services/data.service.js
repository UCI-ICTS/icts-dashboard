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

const dataService = {
    submitParticipant,
}

  export default dataService;