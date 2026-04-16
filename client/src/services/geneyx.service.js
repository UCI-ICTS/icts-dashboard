// src/services/geneyx.service.js

import axios from "axios";
import { store } from "../store";
import api from "../utils/axiosConfig";


const APIDB = process.env.GENEYX_APIDB;

const headers = {
  "Content-Type": "application/json",
  "ApiUserId": process.env.GENEYX_USER_ID,
  "ApiUserKey": process.env.GENEYX_USER_KEY,
  "PageSize": process.env.GENEYX_PAGE_SIZE,  // Only used for getting bulk samples or cases
}

const getSamples = async () => {  // The samples API is used to retrieve the list of samples in the account.
  const response = api.post(`${APIDB}api/Samples`, headers);
  return response;
}

const getSample = async (participant_id) => {  // Returns a description of the sample (e.g. its associated files and locations, setup configurations, when and by it was created etc.)
  const response = api.get(`${APIDB}api/Sample`, {"SampleSN": participant_id}, headers);
  return response;
}

const getCases = async () => {  //The cases API is used to retrieve the list of cases in the account.
  const response = api.get(`${APIDB}api/cases`, headers);
  return response;
}

const getCase = async (case_id) => {  // Generates a summary of all the details of a case
  const response = api.get(`${APIDB}api/Case`, {"CaseSN": case_id}, headers);
  return response;
}

const getCaseNotes = async (case_id) => {  // Get user notes from a given case_id
  const response = api.get(`${APIDB}api/CaseNotes`, {"CaseSN": case_id}, headers);
  return response;
}

const geneyxService = {
  getSamples,
  getSample,
  getCases,
  getCase,
  getCaseNotes,
}

export default geneyxService;