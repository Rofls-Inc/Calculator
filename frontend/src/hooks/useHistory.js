import { useCallback, useEffect, useMemo, useState } from "react";

import { getHistory } from "../api/client.js";


const LOCAL_ERRORS_KEY = "calc.localErrors";
const LOCAL_ERRORS_LIMIT = 50;


function readLocalErrors() {
  try {
    const raw = sessionStorage.getItem(LOCAL_ERRORS_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}


function writeLocalErrors(items) {
  try {
    sessionStorage.setItem(LOCAL_ERRORS_KEY, JSON.stringify(items));
  } catch {
    // Storage may be unavailable (private mode); history just won't persist.
  }
}


/**
 * Server history (successful calculations, per docs/api.md) merged with
 * failed attempts kept only in this browser tab. The backend never stores
 * errors, so they live in sessionStorage.
 */
export function useHistory() {
  const [serverItems, setServerItems] = useState([]);
  const [localErrors, setLocalErrors] = useState(readLocalErrors);
  const [status, setStatus] = useState("loading"); // loading | ready | unavailable

  const refresh = useCallback(async () => {
    try {
      const items = await getHistory();
      setServerItems(items);
      setStatus("ready");
    } catch {
      setStatus("unavailable");
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const addLocalError = useCallback((expression, error) => {
    setLocalErrors((previous) => {
      const next = [
        {
          id: `local-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
          expression,
          error: { code: error.code, message: error.message },
          created_at: new Date().toISOString(),
        },
        ...previous,
      ].slice(0, LOCAL_ERRORS_LIMIT);
      writeLocalErrors(next);
      return next;
    });
  }, []);

  const items = useMemo(() => {
    const merged = [
      ...serverItems.map((item) => ({ ...item, kind: "ok", key: `server-${item.id}` })),
      ...localErrors.map((item) => ({ ...item, kind: "error", key: item.id })),
    ];
    return merged.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  }, [serverItems, localErrors]);

  // TODO: "очистить" history needs DELETE /api/v1/history — not in the API
  // contract yet. Add a clear() here once the team agrees on the endpoint.

  return { items, status, refresh, addLocalError };
}
