// src/services/geneyx.service.js

import axios from "axios";
import { store } from "../store";
import { message } from "antd";

const GENEYX_APIDB = "https://analysis.geneyx.com/";

const geneyxApi = axios.create({
  baseURL: `${GENEYX_APIDB}`
});

const headers = {
  "Content-Type": "application/json",
  "ApiUserId": process.env.GENEYX_USER_ID,
  "ApiUserKey": process.env.GENEYX_USER_KEY,
  "PageSize": process.env.GENEYX_PAGE_SIZE,  // Only used for getting bulk samples or cases
}

const body = {}

const getSamples = async () => {  // The samples API is used to retrieve the list of samples in the account.
  const response = geneyxApi.post(`${GENEYX_APIDB}api/Samples`, body, { headers: headers });
  return response;
}

const getSample = async (sample_id) => {  // Returns a description of the sample (e.g. its associated files and locations, setup configurations, when and by it was created etc.)
  body["SampleSn"] = sample_id
  const response = geneyxApi.post(`${GENEYX_APIDB}api/Sample`, body, { headers: headers });
  return response;
}

const getCases = async () => {  //The cases API is used to retrieve the list of cases in the account.
  const response = geneyxApi.post(`${GENEYX_APIDB}api/cases`, body, { headers: headers });
  return response;
}

const getCase = async (case_id) => {  // Generates a summary of all the details of a case
  body["CaseSn"] = case_id
  const response = geneyxApi.post(`${GENEYX_APIDB}api/Case`, body, { headers: headers });
  return response;
}

const getCaseNotes = async (case_id) => {  // Get user notes from a given case_id
  body["CaseSn"] = case_id
  const response = geneyxApi.post(`${GENEYX_APIDB}api/CaseNotes`, body, { headers: headers });
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