const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

export class ApiError extends Error {
  constructor(status, message, data = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

export async function apiClient(endpoint, { method = "GET", body, params, ...customConfig } = {}) {
  const token = localStorage.getItem("token") || sessionStorage.getItem("token");

  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(customConfig.headers || {}),
  };

  const config = {
    method,
    credentials: "include",
    ...customConfig,
    headers,
  };

  if (body) {
    if (typeof FormData !== "undefined" && body instanceof FormData) {
      delete headers["Content-Type"];
      config.body = body;
    } else {
      config.body = JSON.stringify(body);
    }
  }

  // Serialize params object into query string if provided
  let url = `${BASE_URL}${endpoint}`;
  if (params && typeof params === "object") {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        searchParams.append(key, value);
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      url += (url.includes("?") ? "&" : "?") + queryString;
    }
  }

  let data;
  try {
    const response = await fetch(url, config);
    
    // Parse JSON if response is JSON
    if (response.headers.get("content-type")?.includes("application/json")) {
      data = await response.json();
    }
    
    if (response.ok) {
      return data;
    }
    
    // Handle 401 Unauthorized
    if (response.status === 401) {
      // Clear expired or invalid token
      if (token) {
        localStorage.removeItem("token");
        sessionStorage.removeItem("token");
        window.dispatchEvent(new CustomEvent("auth:unauthorized"));
      }
      throw new ApiError(401, data?.detail || "Authentication required", data);
    }

    // Handle 403 Forbidden
    if (response.status === 403) {
      throw new ApiError(403, data?.detail || "Access forbidden: insufficient permissions", data);
    }
    throw new ApiError(response.status, data?.detail || response.statusText || "Request failed", data);
  } catch (err) {
    if (err instanceof ApiError) {
      return Promise.reject(err);
    }
    return Promise.reject(new ApiError(0, err.message || "Network error"));
  }
}

apiClient.get = (endpoint, customConfig = {}) => apiClient(endpoint, { method: "GET", ...customConfig });
apiClient.post = (endpoint, body, customConfig = {}) => apiClient(endpoint, { method: "POST", body, ...customConfig });
apiClient.put = (endpoint, body, customConfig = {}) => apiClient(endpoint, { method: "PUT", body, ...customConfig });
apiClient.patch = (endpoint, body, customConfig = {}) => apiClient(endpoint, { method: "PATCH", body, ...customConfig });
apiClient.delete = (endpoint, customConfig = {}) => apiClient(endpoint, { method: "DELETE", ...customConfig });

