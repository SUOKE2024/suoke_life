// 实时数据同步服务
// 支持WebSocket连接、数据同步、冲突解决等功能

interface SyncConfig {
  reconnectInterval: number;
  maxReconnectAttempts: number;
  heartbeatInterval: number;
  syncInterval: number;
}

interface SyncData {
  id: string;
  type: string;
  data: any;
  timestamp: number;
  version: number;
}

interface ConflictResolution {
  strategy: 'client_wins' | 'server_wins' | 'merge' | 'manual';
  resolver?: (clientData: any, serverData: any) => any;
}

// 简化的事件发射器
class SimpleEventEmitter {
  private listeners: Map<string, Function[]> = new Map();

  on(event: string, listener: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(listener);
  }

  emit(event: string, ...args: any[]): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(listener => listener(...args));
    }
  }

  off(event: string, listener: Function): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      const index = eventListeners.indexOf(listener);
      if (index > -1) {
        eventListeners.splice(index, 1);
      }
    }
  }
}

class RealTimeSync extends SimpleEventEmitter {
  private ws: WebSocket | null = null;
  private isConnected = false;
  private reconnectAttempts = 0;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private syncTimer: NodeJS.Timeout | null = null;
  private pendingSync: Map<string, SyncData> = new Map();
  private localData: Map<string, SyncData> = new Map();
  
  private config: SyncConfig = {
    reconnectInterval: 5000,
    maxReconnectAttempts: 10,
    heartbeatInterval: 30000,
    syncInterval: 60000
  };

  private conflictResolution: Map<string, ConflictResolution> = new Map();

  constructor(private wsUrl: string, private authToken: string) {
    super();
    this.loadLocalData();
    this.setupConflictResolvers();
  }

  private setupConflictResolvers(): void {
    // 健康数据：服务器优先
    this.conflictResolution.set('health_data', {
      strategy: 'server_wins'
    });

    // 用户偏好：客户端优先
    this.conflictResolution.set('user_preferences', {
      strategy: 'client_wins'
    });

    // 诊断结果：合并策略
    this.conflictResolution.set('diagnosis_result', {
      strategy: 'merge',
      resolver: (clientData, serverData) => ({
        ...serverData,
        clientNotes: clientData.clientNotes,
        localTimestamp: clientData.timestamp
      })
    });
  }

  async connect(): Promise<void> {
    if (this.isConnected) {
      return;
    }

    try {
      this.ws = new WebSocket(`${this.wsUrl}?token=${this.authToken}`);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.startHeartbeat();
        this.startPeriodicSync();
        this.syncPendingData();
        this.emit('connected');
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(JSON.parse(event.data));
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.isConnected = false;
        this.stopHeartbeat();
        this.stopPeriodicSync();
        this.emit('disconnected');
        this.scheduleReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', error);
      };

    } catch (error) {
      console.error('WebSocket connection failed:', error);
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.emit('maxReconnectAttemptsReached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.config.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1);
    
    setTimeout(() => {
      console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`);
      this.connect();
    }, delay);
  }

  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected && this.ws) {
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, this.config.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private startPeriodicSync(): void {
    this.syncTimer = setInterval(() => {
      this.requestFullSync();
    }, this.config.syncInterval);
  }

  private stopPeriodicSync(): void {
    if (this.syncTimer) {
      clearInterval(this.syncTimer);
      this.syncTimer = null;
    }
  }

  private handleMessage(message: any): void {
    switch (message.type) {
      case 'pong':
        // 心跳响应
        break;
        
      case 'data_update':
        this.handleDataUpdate(message.data);
        break;
        
      case 'sync_response':
        this.handleSyncResponse(message.data);
        break;
        
      case 'conflict':
        this.handleConflict(message.data);
        break;
        
      case 'error':
        this.emit('serverError', message.error);
        break;
        
      default:
        console.warn('Unknown message type:', message.type);
    }
  }

  private async handleDataUpdate(data: SyncData): Promise<void> {
    const localVersion = this.localData.get(data.id);
    
    if (!localVersion || data.version > localVersion.version) {
      // 服务器数据更新
      this.localData.set(data.id, data);
      await this.saveLocalData();
      this.emit('dataUpdated', data);
    } else if (data.version < localVersion.version) {
      // 本地数据更新，发送到服务器
      this.sendDataUpdate(localVersion);
    } else {
      // 版本相同，检查内容是否一致
      if (JSON.stringify(data.data) !== JSON.stringify(localVersion.data)) {
        // 数据冲突
        await this.resolveConflict(data, localVersion);
      }
    }
  }

  private async handleSyncResponse(syncData: SyncData[]): Promise<void> {
    for (const data of syncData) {
      await this.handleDataUpdate(data);
    }
    this.emit('syncCompleted');
  }

  private async handleConflict(conflictData: any): Promise<void> {
    const { clientData, serverData } = conflictData;
    const resolved = await this.resolveConflict(serverData, clientData);
    
    if (resolved) {
      this.sendDataUpdate(resolved);
    }
  }

  private async resolveConflict(serverData: SyncData, clientData: SyncData): Promise<SyncData | null> {
    const resolver = this.conflictResolution.get(serverData.type);
    
    if (!resolver) {
      // 默认策略：服务器优先
      this.localData.set(serverData.id, serverData);
      await this.saveLocalData();
      this.emit('conflictResolved', { strategy: 'server_wins', data: serverData });
      return null;
    }

    let resolvedData: any;

    switch (resolver.strategy) {
      case 'server_wins':
        resolvedData = serverData;
        break;
        
      case 'client_wins':
        resolvedData = clientData;
        break;
        
      case 'merge':
        if (resolver.resolver) {
          resolvedData = {
            ...serverData,
            data: resolver.resolver(clientData.data, serverData.data),
            version: Math.max(serverData.version, clientData.version) + 1
          };
        } else {
          resolvedData = serverData; // 回退到服务器优先
        }
        break;
        
      case 'manual':
        // 触发手动解决事件
        this.emit('manualConflictResolution', { serverData, clientData });
        return null;
    }

    this.localData.set(resolvedData.id, resolvedData);
    await this.saveLocalData();
    this.emit('conflictResolved', { strategy: resolver.strategy, data: resolvedData });
    
    return resolvedData;
  }

  async updateData(id: string, type: string, data: any): Promise<void> {
    const existingData = this.localData.get(id);
    const version = existingData ? existingData.version + 1 : 1;
    
    const syncData: SyncData = {
      id,
      type,
      data,
      timestamp: Date.now(),
      version
    };

    this.localData.set(id, syncData);
    await this.saveLocalData();

    if (this.isConnected) {
      this.sendDataUpdate(syncData);
    } else {
      // 离线时加入待同步队列
      this.pendingSync.set(id, syncData);
      await this.savePendingSync();
    }

    this.emit('localDataUpdated', syncData);
  }

  private sendDataUpdate(data: SyncData): void {
    if (this.ws && this.isConnected) {
      this.ws.send(JSON.stringify({
        type: 'data_update',
        data
      }));
    }
  }

  private requestFullSync(): void {
    if (this.ws && this.isConnected) {
      const localVersions = Array.from(this.localData.values()).map(data => ({
        id: data.id,
        version: data.version
      }));

      this.ws.send(JSON.stringify({
        type: 'sync_request',
        versions: localVersions
      }));
    }
  }

  private async syncPendingData(): Promise<void> {
    for (const [id, data] of this.pendingSync) {
      this.sendDataUpdate(data);
    }
    
    this.pendingSync.clear();
    // 在实际应用中，这里应该使用AsyncStorage
    // await AsyncStorage.removeItem('pendingSync');
  }

  private async loadLocalData(): Promise<void> {
    try {
      // 在实际应用中，这里应该从AsyncStorage加载数据
      // const data = await AsyncStorage.getItem('localSyncData');
      // if (data) {
      //   const parsed = JSON.parse(data);
      //   this.localData = new Map(parsed);
      // }

      // const pending = await AsyncStorage.getItem('pendingSync');
      // if (pending) {
      //   const parsedPending = JSON.parse(pending);
      //   this.pendingSync = new Map(parsedPending);
      // }
    } catch (error) {
      console.error('Failed to load local data:', error);
    }
  }

  private async saveLocalData(): Promise<void> {
    try {
      // 在实际应用中，这里应该保存到AsyncStorage
      // const data = Array.from(this.localData.entries());
      // await AsyncStorage.setItem('localSyncData', JSON.stringify(data));
    } catch (error) {
      console.error('Failed to save local data:', error);
    }
  }

  private async savePendingSync(): Promise<void> {
    try {
      // 在实际应用中，这里应该保存到AsyncStorage
      // const data = Array.from(this.pendingSync.entries());
      // await AsyncStorage.setItem('pendingSync', JSON.stringify(data));
    } catch (error) {
      console.error('Failed to save pending sync:', error);
    }
  }

  getData(id: string): SyncData | undefined {
    return this.localData.get(id);
  }

  getAllData(): SyncData[] {
    return Array.from(this.localData.values());
  }

  getDataByType(type: string): SyncData[] {
    return Array.from(this.localData.values()).filter(data => data.type === type);
  }

  async clearAllData(): Promise<void> {
    this.localData.clear();
    this.pendingSync.clear();
    // 在实际应用中，这里应该清理AsyncStorage
    // await AsyncStorage.multiRemove(['localSyncData', 'pendingSync']);
    this.emit('dataCleared');
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.stopHeartbeat();
    this.stopPeriodicSync();
  }

  getConnectionStatus(): boolean {
    return this.isConnected;
  }

  getPendingSyncCount(): number {
    return this.pendingSync.size;
  }
}

export default RealTimeSync; 