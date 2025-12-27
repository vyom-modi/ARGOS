import { useEffect, useRef, useCallback, useState } from 'react';

interface UseWebSocketOptions {
    onMessage?: (data: any) => void;
    onOpen?: () => void;
    onClose?: () => void;
    onError?: (error: Event) => void;
}

export function useWebSocket(url: string, options: UseWebSocketOptions = {}) {
    const [isConnected, setIsConnected] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);
    const optionsRef = useRef(options);
    const reconnectTimeoutRef = useRef<number | null>(null);
    const mountedRef = useRef(true);

    useEffect(() => {
        optionsRef.current = options;
    }, [options]);

    const connect = useCallback(() => {
        // Don't reconnect if already connected or connecting
        if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
            return;
        }

        console.log('[WS] Connecting to', url);
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log('[WS] Connected');
            if (mountedRef.current) {
                setIsConnected(true);
                optionsRef.current.onOpen?.();
            }
        };

        ws.onmessage = (event) => {
            if (!mountedRef.current) return;
            try {
                const data = JSON.parse(event.data);
                optionsRef.current.onMessage?.(data);
            } catch {
                optionsRef.current.onMessage?.(event.data);
            }
        };

        ws.onclose = (event) => {
            console.log('[WS] Closed:', event.code);
            wsRef.current = null;
            if (mountedRef.current) {
                setIsConnected(false);
                optionsRef.current.onClose?.();

                // Auto-reconnect after 2 seconds if the component is still mounted
                if (event.code !== 1000) { // 1000 = normal closure
                    reconnectTimeoutRef.current = window.setTimeout(() => {
                        if (mountedRef.current) {
                            console.log('[WS] Reconnecting...');
                            connect();
                        }
                    }, 2000);
                }
            }
        };

        ws.onerror = (error) => {
            console.error('[WS] Error:', error);
            if (mountedRef.current) {
                optionsRef.current.onError?.(error);
            }
        };
    }, [url]);

    useEffect(() => {
        mountedRef.current = true;
        connect();

        return () => {
            mountedRef.current = false;
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (wsRef.current) {
                wsRef.current.close(1000, 'Component unmounted');
                wsRef.current = null;
            }
        };
    }, [connect]);

    const send = useCallback((data: any) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(typeof data === 'string' ? data : JSON.stringify(data));
            return true;
        }
        console.warn('[WS] Cannot send - not connected');
        return false;
    }, []);

    return { isConnected, send };
}
