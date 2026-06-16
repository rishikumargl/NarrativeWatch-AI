import { useEffect, useState, useCallback } from 'react';

export default function useWebSocket(url) {
  const [data, setData] = useState(null);
  const [status, setStatus] = useState('connecting');
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!url) return;

    const ws = new WebSocket(url);

    ws.onopen = () => {
      setStatus('connected');
      setError(null);
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        setData(message);
      } catch (e) {
        console.error('WebSocket parse error:', e);
      }
    };

    ws.onerror = (event) => {
      setStatus('error');
      setError('WebSocket connection failed');
      console.error('WebSocket error:', event);
    };

    ws.onclose = () => {
      setStatus('closed');
    };

    return () => {
      ws.close();
    };
  }, [url]);

  return { data, status, error };
}
