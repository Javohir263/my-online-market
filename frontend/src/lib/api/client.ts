/**
 * Axios API client — cookie-based auth (JWT in httpOnly cookies).
 *
 * - `withCredentials: true` → browser cookie'larni avtomatik yuboradi
 * - CSRF interceptor → `X-CSRFToken` header (csrftoken cookie'dan)
 * - 401 → /auth/refresh/ urinish (bir marta), keyin original requestni qaytarish
 */
import axios, {
  AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

function getCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(
    new RegExp("(^|;\\s*)" + name + "=([^;]*)"),
  );
  return match ? decodeURIComponent(match[2]) : null;
}

export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

// --- Request: attach CSRF token on unsafe methods ---
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const method = (config.method ?? "get").toLowerCase();
  if (!["get", "head", "options", "trace"].includes(method)) {
    const csrf = getCookie("csrftoken");
    if (csrf) {
      config.headers.set("X-CSRFToken", csrf);
    }
  }
  // Active locale → backend modeltranslation shu tilda content qaytaradi
  if (typeof document !== "undefined") {
    config.headers.set(
      "Accept-Language",
      document.documentElement.lang || "uz",
    );
  }
  return config;
});

// --- Response: refresh on 401 once ---
let isRefreshing = false;
let pendingQueue: Array<() => void> = [];

api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    const isAuthEndpoint =
      original?.url?.includes("/auth/login") ||
      original?.url?.includes("/auth/refresh");

    if (
      error.response?.status === 401 &&
      !original?._retry &&
      !isAuthEndpoint
    ) {
      original._retry = true;

      if (isRefreshing) {
        // Wait for the ongoing refresh
        await new Promise<void>((resolve) => pendingQueue.push(resolve));
        return api(original);
      }

      isRefreshing = true;
      try {
        await api.post("/auth/refresh/");
        pendingQueue.forEach((cb) => cb());
        pendingQueue = [];
        return api(original);
      } catch (refreshError) {
        pendingQueue = [];
        // Refresh failed — user must re-login (handled by UI)
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  },
);
