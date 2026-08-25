// src/services/anvil.service.js

import axios from "axios";
import { store } from "../store";
import api, {getAuthHeaders} from "../utils/axiosConfig";


const APIDB = process.env.REACT_APP_APIDB;
const BASE_URL = `${APIDB}api/anvil/uploads/`

const fetchAnvilUploadsService = async () => {
  const response = api.get(BASE_URL, {headers: getAuthHeaders()});
  return response;
};

const fetchAnvilUploadDetailService = async (uploadId) => {
  const response = api.get(`${BASE_URL}${uploadId}/`, {headers: getAuthHeaders()});
  return response;
};

const createAnvilUploadService = async (payload) => {
  const response = api.post(BASE_URL, payload, {headers: getAuthHeaders()});
  return response;
};

const initializeAnvilUploadService = async (uploadId) => {
  const response = api.post(`${BASE_URL}${uploadId}/initialize/`, {});
  return response;
};

const validateAnvilSourceService = async (uploadId) => {
  const response = api.post(`${BASE_URL}${uploadId}/validate-source/`, {});
  return response;
};

const generateAnvilTsvsService = async ({ uploadId }) => {
  const response = api.post(`${BASE_URL}${uploadId}/generate-tsvs/`, {});
  return response;
};

const generateAnvilManifestService = async ({ uploadId }) => {
  const response = api.post(`${BASE_URL}${uploadId}/generate-manifest/`, {});
  return response;
};

const validateAnvilPackageService = async (uploadId) => {
  const response = api.post(`${BASE_URL}${uploadId}/validate-package/`, {});
  return response;
};

const anvilService = {
    fetchAnvilUploadsService,
    fetchAnvilUploadDetailService,
    createAnvilUploadService,
    initializeAnvilUploadService,
    validateAnvilPackageService,
    validateAnvilSourceService,
    generateAnvilTsvsService,
    generateAnvilManifestService,
};

export default anvilService;