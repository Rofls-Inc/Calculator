import { useCallback, useEffect, useState } from "react";

import { getHealth } from "../api/client.js";


const PING_INTERVAL_MS = 30_000;


/** Poll GET /health and report whether the backend is reachable. */
export function useBackendStatus() {
  const [status, setStatus] = useState("checking");

  const ping = useCallback(async () => {
    try {
      await getHealth();
      setStatus("online");
    } catch {
      setStatus("offline");
    }
  }, []);

  useEffect(() => {
    let active = true;

    const run = () => {
      if (active) ping();
    };

    run();
    const timer = setInterval(run, PING_INTERVAL_MS);

    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [ping]);

  return { status, refresh: ping };
}
