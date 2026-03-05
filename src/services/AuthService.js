import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000/users_authentication";

export const registerUser = (data) => {
  return axios.post(`${BASE_URL}/register/`, data);
};

export const loginUser = (data) => {
  return axios.post(`${BASE_URL}/login/`, data);
};