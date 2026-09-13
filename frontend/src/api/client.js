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


export async function calculate(expression) {
  const response = await api.post("/calculate", { expression });
  return response.data;
}


export async function getHistory() {
  const response = await api.get("/history");
  return response.data.items ?? [];
}


/**
 * Convert an axios error into a shape the UI can render.
 *
 * kind "api"     — backend understood the request and rejected it (HTTP 400
 *                  with {error: {code, message}} per docs/api.md).
 * kind "offline" — everything else: timeout, network failure, 5xx, or the
 *                  501 stub that the endpoint returns until it is implemented.
 */
export function normalizeApiError(error) {
  const status = error?.response?.status ?? null;
  const body = error?.response?.data;

  if (status === 400 && body?.error) {
    return {
      kind: "api",
      status,
      code: body.error.code || "INVALID_EXPRESSION",
      message: body.error.message || "Expression is invalid",
    };
  }

  if (error?.code === "ECONNABORTED") {
    return { kind: "offline", status, code: "TIMEOUT", message: "Сервис не ответил за 5 с" };
  }

  if (status === 501) {
    return { kind: "offline", status, code: "NOT_IMPLEMENTED", message: "Эндпоинт ещё не реализован" };
  }

  return {
    kind: "offline",
    status,
    code: status ? `HTTP_${status}` : "NETWORK",
    message: status ? `Сервис вернул ${status}` : "Нет соединения с сервисом",
  };
}


export default api;
