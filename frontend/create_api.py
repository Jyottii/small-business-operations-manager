import os
import sqlite3

# Get business ID
conn = sqlite3.connect('../backend/smallbiz.db')
c = conn.cursor()
c.execute('SELECT id FROM businesses LIMIT 1')
biz_id = c.fetchone()[0]
conn.close()

os.makedirs('src/api', exist_ok=True)

with open('.env', 'w') as f:
    f.write('VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1\n')

with open('.env.example', 'w') as f:
    f.write('VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1\n')

client_code = f"""
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";
const BUSINESS_ID = "{biz_id}"; // Seeded Business ID for Phase 3 dev

export async function apiClient(endpoint, {{ method = "GET", body, ...customConfig }} = {{}}) {{
  const headers = {{
    "Content-Type": "application/json",
    "X-Business-ID": BUSINESS_ID,
  }};

  const config = {{
    method,
    headers,
    ...customConfig,
  }};

  if (body) {{
    config.body = JSON.stringify(body);
  }}

  let data;
  try {{
    const response = await fetch(`${{BASE_URL}}${{endpoint}}`, config);
    
    // Parse JSON
    if (response.headers.get("content-type")?.includes("application/json")) {{
      data = await response.json();
    }}
    
    if (response.ok) {{
      return data;
    }}
    
    throw new Error(data?.detail || response.statusText);
  }} catch (err) {{
    return Promise.reject(err.message ? err.message : "Network error");
  }}
}}
"""

with open('src/api/client.js', 'w') as f:
    f.write(client_code)

hooks_code = """
import { useState, useEffect, useCallback } from 'react';
import { apiClient } from './client';

export function useApi(endpoint, dependencies = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const result = await apiClient(endpoint);
      setData(result.data);
      if (result.pagination) {
        setPagination(result.pagination);
      }
      setError(null);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [endpoint]);

  useEffect(() => {
    fetchData();
  }, [fetchData, ...dependencies]);

  return { data, loading, error, pagination, refetch: fetchData };
}
"""

with open('src/api/hooks.js', 'w') as f:
    f.write(hooks_code)

