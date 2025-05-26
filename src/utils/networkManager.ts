import NetInfo from '@react-native-community/netinfo';
import { DeviceEventEmitter } from 'react-native';

interface NetworkState {
  isConnected: boolean;
  type: string;
  isInternetReachable: boolean;
  strength?: number;
}

class NetworkManager {
  private currentState: NetworkState = {
    isConnected: false,
    type: 'unknown',
    isInternetReachable: false,
  };
  
  private listeners: ((state: NetworkState) => void)[] = [];
  
  /**
   * 初始化网络监控
   */
  initialize() {
    NetInfo.addEventListener(state => {
      this.currentState = {
        isConnected: state.isConnected || false,
        type: state.type,
        isInternetReachable: state.isInternetReachable || false,
        strength: state.details?.strength,
      };
      
      this.notifyListeners();
      DeviceEventEmitter.emit('networkStateChange', this.currentState);
    });
    
    console.log('🌐 网络状态监控已初始化');
  }
  
  /**
   * 获取当前网络状态
   */
  getCurrentState(): NetworkState {
    return this.currentState;
  }
  
  /**
   * 检查是否在线
   */
  isOnline(): boolean {
    return this.currentState.isConnected && this.currentState.isInternetReachable;
  }
  
  /**
   * 检查是否为WiFi连接
   */
  isWiFi(): boolean {
    return this.currentState.type === 'wifi';
  }
  
  /**
   * 检查是否为移动网络
   */
  isCellular(): boolean {
    return this.currentState.type === 'cellular';
  }
  
  /**
   * 添加网络状态监听器
   */
  addListener(callback: (state: NetworkState) => void) {
    this.listeners.push(callback);
  }
  
  /**
   * 移除网络状态监听器
   */
  removeListener(callback: (state: NetworkState) => void) {
    const index = this.listeners.indexOf(callback);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }
  
  private notifyListeners() {
    this.listeners.forEach(listener => {
      try {
        listener(this.currentState);
      } catch (error) {
        console.error('网络状态监听器错误:', error);
      }
    });
  }
  
  /**
   * 网络质量评估
   */
  getNetworkQuality(): 'poor' | 'fair' | 'good' | 'excellent' {
    if (!this.isOnline()) return 'poor';
    
    if (this.isWiFi()) return 'excellent';
    
    if (this.currentState.strength) {
      if (this.currentState.strength > 80) return 'excellent';
      if (this.currentState.strength > 60) return 'good';
      if (this.currentState.strength > 40) return 'fair';
    }
    
    return 'poor';
  }
}

export const networkManager = new NetworkManager();
export default networkManager;