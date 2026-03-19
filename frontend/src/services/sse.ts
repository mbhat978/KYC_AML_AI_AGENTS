/**
 * Server-Sent Events (SSE) Client for Real-Time Agent Streaming
 */
import type { AgentEvent } from '../types';

export class SSEClient {
  private eventSource: EventSource | null = null;
  private readonly baseUrl = 'http://localhost:8000/api';
  private reconnectAttempts = 0;
  private readonly maxReconnectAttempts = 3;

  /**
   * Connect to SSE stream
   */
  connect(
    sessionId: string,
    onMessage: (event: AgentEvent) => void,
    onError?: (error: Event) => void,
    onComplete?: () => void
  ): void {
    // Close any existing connection first
    this.disconnect();
    
    const url = `${this.baseUrl}/kyc/stream/${sessionId}`;
    console.log(`[SSE] Connecting to: ${url}`);
    
    this.eventSource = new EventSource(url);

    this.eventSource.onopen = () => {
      console.log('[SSE] Connection established successfully');
      this.reconnectAttempts = 0;
    };

    this.eventSource.onmessage = (event) => {
      try {
        // Brute-force cleanup: Strip any accidental ' ' prefix before parsing
        // This handles cases where backend double-prefixes the event
        const cleanData = event.data.replace(/^data:\s*/, '');
        const data: AgentEvent = JSON.parse(cleanData);
        
        // Reset reconnect attempts on successful message
        this.reconnectAttempts = 0;
        
        // Don't pass heartbeat events to UI, but log them
        if (data.step === 'heartbeat') {
          console.log('[SSE] Heartbeat received:', data.message);
          return;
        }
        
        onMessage(data);

        // Check if processing is complete
        if (data.step === 'complete' || data.step === 'error') {
          console.log('[SSE] Processing complete, closing connection');
          if (onComplete) {
            onComplete();
          }
          this.disconnect();
        }
      } catch (error) {
        console.error('[SSE] Error parsing message:', error);
        console.error('[SSE] Raw event.', event.data);
      }
    };

    this.eventSource.onerror = (error) => {
      console.error('[SSE] Connection error:', error);
      
      // Check the connection state before deciding to disconnect
      if (this.eventSource) {
        const readyState = this.eventSource.readyState;
        console.log(`[SSE] ReadyState: ${readyState} (0=CONNECTING, 1=OPEN, 2=CLOSED)`);
        
        // EventSource.CONNECTING (0) - don't disconnect, it's trying to connect
        // EventSource.OPEN (1) - should not happen in onerror
        // EventSource.CLOSED (2) - connection failed permanently
        
        if (readyState === EventSource.CLOSED) {
          console.log('[SSE] Connection closed by server or network error');
          this.reconnectAttempts++;
          
          if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('[SSE] Max reconnection attempts reached');
            if (onError) {
              onError(error);
            }
            this.disconnect();
          }
        } else if (readyState === EventSource.CONNECTING) {
          console.log('[SSE] Connection is reconnecting automatically...');
          // Let EventSource handle automatic reconnection
          // Don't disconnect - EventSource will retry automatically
        }
      } else {
        console.log('[SSE] EventSource is null during error');
        if (onError) {
          onError(error);
        }
      }
    };
  }

  /**
   * Disconnect from SSE stream
   */
  disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.eventSource !== null && this.eventSource.readyState === EventSource.OPEN;
  }
}

// Singleton instance
export const sseClient = new SSEClient();