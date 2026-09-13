import axios from "axios";


const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api/v1",
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
  timeout: 5000,
});


export async function getHealth() {
  const response = await api.get("/health");
  return response.data;
}


export default api;
