import { io, Socket } from 'socket.io-client';
import { 
  CarTelemetry, 
  WeatherZone, 
  Alert, 
  Incident,
  RaceSession,
  WebSocketMessage 
} from '../../../shared/src/types';

/**
 * WebSocket Service for real-time communication with backend
 */

export type EventCallback<T = any> = (data: T) => void;

class SocketService {
  private socket: Socket | null = null;
  private url: string = import.meta.env.VITE_SOCKET_URL || 'http://localhost:3001';
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  /**
   * Connect to WebSocket server
   */
  public connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.socket = io(this.url, {
          transports: ['websocket', 'polling'],
          reconnection: true,
          reconnectionDelay: 1000,
          reconnectionDelayMax: 5000,
          reconnectionAttempts: this.maxReconnectAttempts
        });

        this.socket.on('connect', () => {
          console.log('✅ Connected to WebSocket server');
          this.reconnectAttempts = 0;
          resolve();
        });

        this.socket.on('connect_error', (error) => {
          console.error('❌ Connection error:', error);
          this.reconnectAttempts++;
          
          if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            reject(new Error('Failed to connect to server'));
          }
        });

        this.socket.on('disconnect', (reason) => {
          console.log('🔌 Disconnected from server:', reason);
        });

      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Disconnect from server
   */
  public disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  /**
   * Check if connected
   */
  public isConnected(): boolean {
    return this.socket?.connected ?? false;
  }

  /**
   * Listen for telemetry updates
   */
  public onTelemetryUpdate(callback: EventCallback<CarTelemetry[]>): void {
    this.socket?.on('telemetry_update', (message: WebSocketMessage<CarTelemetry[]>) => {
      callback(message.data);
    });
  }

  /**
   * Listen for weather updates
   */
  public onWeatherUpdate(callback: EventCallback<WeatherZone[]>): void {
    this.socket?.on('weather_update', (message: WebSocketMessage<WeatherZone[]>) => {
      callback(message.data);
    });
  }

  /**
   * Listen for alerts
   */
  public onAlert(callback: EventCallback<Alert>): void {
    this.socket?.on('alert', (message: WebSocketMessage<Alert>) => {
      callback(message.data);
    });
  }

  /**
   * Listen for incidents
   */
  public onIncident(callback: EventCallback<Incident>): void {
    this.socket?.on('incident', (message: WebSocketMessage<Incident>) => {
      callback(message.data);
    });
  }

  /**
   * Listen for session updates
   */
  public onSessionUpdate(callback: EventCallback<RaceSession>): void {
    this.socket?.on('session_update', (message: WebSocketMessage<RaceSession>) => {
      callback(message.data);
    });
  }

  /**
   * Request to start session
   */
  public startSession(): void {
    this.socket?.emit('start_session');
  }

  /**
   * Request to stop session
   */
  public stopSession(): void {
    this.socket?.emit('stop_session');
  }

  /**
   * Request to reset session
   */
  public resetSession(): void {
    this.socket?.emit('reset_session');
  }

  /**
   * Remove event listener
   */
  public off(event: string, callback?: EventCallback): void {
    if (callback) {
      this.socket?.off(event, callback);
    } else {
      this.socket?.off(event);
    }
  }

  /**
   * Remove all listeners
   */
  public removeAllListeners(): void {
    this.socket?.removeAllListeners();
  }
}

// Export singleton instance
export const socketService = new SocketService();

