// src/services/error.service.js

const printErrorMessages = (error) => {
  let errorMessage = "";

  console.log(error)

  if (error.name === "AxiosError"){
    if (error.response) {
      // Check if there's a top-level errorMessage.
      if (error.response.status === 401) {
        console.log("Token not valid");
        errorMessage = "Token is not valid. Please log in again."
      }
      if (error.response.message) {
        errorMessage = error.response.message; 
      } else if ( // Otherwise, if error.response.data is an array and has at least one element:
        error.response.data &&
        Array.isArray(error.response.data) &&
        error.response.data.length > 0
      ) {
        // If the first element has a 'data' key that is an array, use that:
        if (error.response.data[0].data &&
          Array.isArray(error.response.data[0].data) &&
          error.response.data[0].data.length > 0
        ) {
          for (const field in error.response.data[0].data[0]) {
            errorMessage = `Error. ${field}: ${error.response.data[0].data[0][field]}\n`
          };
        }
        // Otherwise, if the first element itself has 'field' and 'error', use those.
        else if (
          error.response.data[0].field &&
          error.response.data[0].error
        ) {
          errorMessage = `Error: ${error.response.data[0].field}: ${error.response.data[0].error}`;
        }
        // Otherwise, fall back to stringifying the first element.
        else {
          console.log("error.response.data[0] is likely a string type")
          if (error.response.data[0]["data"]) {
            errorMessage = error.response.data[0]["data"]
          }
          else { errorMessage = JSON.stringify(error.response.data[0]) }
        }
      }
    }
    else if (error.message) { errorMessage = error.message }
    else if (error.request) { errorMessage = error.request }
  }

  // Fallback generic message.
  else if (error.message==="Rejected") { errorMessage = error.message }
  else { errorMessage = "An unknown error occurred."; }
  console.log(errorMessage)
  return errorMessage;
}

const errorService = { printErrorMessages }

export default errorService;