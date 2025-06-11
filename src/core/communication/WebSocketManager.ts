/* 等 */
*/
export enum MessageType {CHAT = 'CHAT','HEALTH_DATA = 'HEALTH_DATA',';
DIAGNOSIS_UPDATE = 'DIAGNOSIS_UPDATE','
AGENT_STATUS = 'AGENT_STATUS','
SYSTEM_NOTIFICATION = 'SYSTEM_NOTIFICATION',
}
}
    HEARTBEAT = 'HEARTBEAT'}
  }
  export interface WebSocketMessage {type: MessageType}payload: any,;
timestamp: number,
const messageId = string;
userId?: string;
}
}
    sessionId?: string}
}
  export interface ConnectionConfig {url: string}reconnectInterval: number,;
maxReconnectAttempts: number,
heartbeatInterval: number,
}
}
  const timeout = number}
}
  export interface MessageHandler {;
type: MessageType,
}
  handler: (message: WebSocketMessage) => void | Promise<void>}
}
  export class WebSocketManager {private static instance: WebSocketManager;
private ws: WebSocket | null = null;
private config: ConnectionConfig;
private messageHandlers: Map<MessageType, Set<(message: WebSocketMessage) => void>> = new Map();
private reconnectAttempts = 0;
private reconnectTimer: NodeJS.Timeout | null = null;
private heartbeatTimer: NodeJS.Timeout | null = null;
private isConnecting = false;
private messageQueue: WebSocketMessage[] = [];
private connectionPromise: Promise<void> | null = null;
private constructor(config: ConnectionConfig) {this.config = config}
}
      this.setupMessageHandlers()}
    }
    const public = static getInstance(config?: ConnectionConfig): WebSocketManager {if (!WebSocketManager.instance) {'const: defaultConfig: ConnectionConfig = {,'url: 'ws://localhost:8000/ws,''/,'/g,'/;
  reconnectInterval: 3000,
maxReconnectAttempts: 5,
}
          heartbeatInterval: 30000,}
          const timeout = 10000;};
WebSocketManager.instance = new WebSocketManager(config || defaultConfig);
      }
      return WebSocketManager.instance;
    }
    /* ; */
    */
const public = async connect(): Promise<void> {if (this.ws?.readyState === WebSocket.OPEN) {}
        return Promise.resolve()}
      }
      if (this.connectionPromise) {}
        return this.connectionPromise}
      }
      this.connectionPromise = new Promise(resolve, reject) => {try {}          this.isConnecting = true;
this.ws = new WebSocket(this.config.url);
const  timeout = setTimeout() => {if (this.ws?.readyState !== WebSocket.OPEN) {'this.ws?.close();
}
              reject(new Error('WebSocket connection timeout'));'}
            }
          }, this.config.timeout);
this.ws.onopen = () => {clearTimeout(timeout)this.isConnecting = false;
this.reconnectAttempts = 0;
this.startHeartbeat();
this.processMessageQueue();
}
            resolve()}
          };
this.ws.onmessage = (event) => {}
            this.handleMessage(event.data)}
          };
this.ws.onclose = (event) => {clearTimeout(timeout)this.isConnecting = false;
this.stopHeartbeat();
if (!event.wasClean && this.reconnectAttempts < this.config.maxReconnectAttempts) {}
              this.scheduleReconnect()}
            }
          };
this.ws.onerror = (error) => {clearTimeout(timeout)this.isConnecting = false;
}
            reject(error)}
          };
        } catch (error) {this.isConnecting = false}
          reject(error)}
        }
      });
return this.connectionPromise;
    }
    /* 接 */
    */
const public = disconnect(): void {this.stopHeartbeat()this.clearReconnectTimer();
if (this.ws) {'this.ws.close(1000, 'Client disconnect');
}
        this.ws = null}
      }
      this.connectionPromise = null;
    }
    /* 息 */
    *//,/g,/;
  public: async sendMessage(type: MessageType, payload: any, options?: {)userId?: string;)sessionId?: string;);
}
      priority?: boolean;)}
    }): Promise<void> {const  message: WebSocketMessage = {}        type,
payload,
timestamp: Date.now(),
messageId: this.generateMessageId(),
}
        userId: options?.userId,}
        const sessionId = options?.sessionId;};
if (this.ws?.readyState === WebSocket.OPEN) {}
        this.ws.send(JSON.stringify(message))}
      } else {// 如果连接未建立，将消息加入队列/if (options?.priority) {}}/g/;
          this.messageQueue.unshift(message)}
        } else {}
          this.messageQueue.push(message)}
        }
        // 尝试重新连接
if (!this.isConnecting) {}
          const await = this.connect()}
        }
      }
    }
    /* 器 */
    *//,/g,/;
  public: onMessage(type: MessageType, handler: (message: WebSocketMessage) => void): () => void {if (!this.messageHandlers.has(type)) {}
        this.messageHandlers.set(type, new Set())}
      }
      this.messageHandlers.get(type)!.add(handler);
      // 返回取消注册的函数
return () => {}
        this.messageHandlers.get(type)?.delete(handler)}
      };
    }
    /* 息 */
    *//,/g,/;
  public: async sendChatMessage(message: string, agentType: string, sessionId: string): Promise<void> {await: this.sendMessage(MessageType.CHAT, {)message,);
}
        agentType,)}
        timestamp: Date.now();}, { sessionId });
    }
    /* 据 */
    *//,/g,/;
  public: async sendHealthData(data: any, userId: string): Promise<void> {await: this.sendMessage(MessageType.HEALTH_DATA, {)}
        data,)}
        timestamp: Date.now();}, { userId });
    }
    /* 态 */
    */
const public = getConnectionStatus(): {connected: boolean}connecting: boolean,
reconnectAttempts: number,
}
  const queuedMessages = number}
    } {return {}        connected: this.ws?.readyState === WebSocket.OPEN,
connecting: this.isConnecting,
}
        reconnectAttempts: this.reconnectAttempts,}
        const queuedMessages = this.messageQueue.length;};
    }
    /* 息 */
    */
private handleMessage(data: string): void {try {}        const message: WebSocketMessage = JSON.parse(data);
        // 处理心跳响应
if (message.type === MessageType.HEARTBEAT) {}
          return}
        }
        // 调用注册的处理器
const handlers = this.messageHandlers.get(message.type);
if (handlers) {handlers.forEach(handler => {)try {)}
              handler(message)}
            } catch (error) {}
}
            }
          });
        }
      } catch (error) {}
}
      }
    }
    /* 器 */
    */
private setupMessageHandlers(): void {// 系统通知处理器/this.onMessage(MessageType.SYSTEM_NOTIFICATION, (message) => {}}/g/;
}
      });
      // 智能体状态更新处理器
this.onMessage(MessageType.AGENT_STATUS, (message) => {}
}
      });
    }
    /* 跳 */
    */
private startHeartbeat(): void {this.heartbeatTimer = setInterval() => {}
        if (this.ws?.readyState === WebSocket.OPEN) {}
          this.sendMessage(MessageType.HEARTBEAT, { timestamp: Date.now() ;});
        }
      }, this.config.heartbeatInterval);
    }
    /* 跳 */
    */
private stopHeartbeat(): void {if (this.heartbeatTimer) {}        clearInterval(this.heartbeatTimer);
}
        this.heartbeatTimer = null}
      }
    }
    /* 连 */
    */
private scheduleReconnect(): void {}
      this.reconnectAttempts++}
      console.log(`🔄 尝试重连 (${this.reconnectAttempts}/${this.config.maxReconnectAttempts})`);```/`,`/g`/`;
this.reconnectTimer = setTimeout() => {this.connect().catch(error => {)}
)}
        });
      }, this.config.reconnectInterval);
    }
    /* 器 */
    */
private clearReconnectTimer(): void {if (this.reconnectTimer) {}        clearTimeout(this.reconnectTimer);
}
        this.reconnectTimer = null}
      }
    }
    /* 列 */
    */
private processMessageQueue(): void {while (this.messageQueue.length > 0 && this.ws?.readyState === WebSocket.OPEN) {}        const message = this.messageQueue.shift();
if (message) {}
          this.ws.send(JSON.stringify(message))}
        }
      }
    }
    /* ; */
    */
private generateMessageId(): string {}
      return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;````;```;
    }
  }
  // 导出单例实例'/,'/g'/;
export const webSocketManager = WebSocketManager.getInstance();
