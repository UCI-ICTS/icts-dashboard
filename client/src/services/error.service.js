// src/services/error.service.js


const APIDB = process.env.REACT_APP_APIDB;

const printErrorMessages = (error) => {
  let errorMessage = "";
  console.log("Starting error decision tree")

  // Check if there's a top-level errorMessage.
  if (error.response && error.response.message) {
    errorMessage = error.response.message;
    console.log("Top-level message:", errorMessage);
  }
  // Otherwise, if error.response.data is an array and has at least one element:
  else if (
    error.response &&
    error.response.data &&
    Array.isArray(error.response.data) &&
    error.response.data.length > 0
  ) {
    console.log("error.response.data is an array of len > 0")
    const firstError = error.response.data[0];
    // If the first element has a 'data' key that is an array, use that:
    if (firstError.data && Array.isArray(firstError.data) && firstError.data.length > 0) {
      console.log("error.reponse.data[0].data has a value")
      let nestedResponse = firstError.data[0]
      for (const field in nestedResponse) {
        errorMessage += console.log(`Error. ${field}: ${nestedResponse[field]}\n`)
      };
    }
    // Otherwise, if the first element itself has 'field' and 'error', use those.
    else if (firstError.field && firstError.error) {
      console.log("error.response.data[0] has its own field and error attributes")
      errorMessage = `Error. ${firstError.field}: ${firstError.error}`;
    }
    // Otherwise, fall back to stringifying the first element.
    else {
      console.log("error.response.data[0] is likely a string type")
      errorMessage = JSON.stringify(firstError);
    }
    console.log("Constructed message from response data:", errorMessage);
  }
  // Fallback generic message.
  else {
    errorMessage = "An unknown error occurred.";
    console.log("Fallback message:", errorMessage);
  }

  console.log("ERROR! ", error.response.data);
  return JSON.stringify(errorMessage);
}

const errorService = {
  printErrorMessages
}

export default errorService;