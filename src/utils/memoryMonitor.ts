import { DeviceEventEmitter } from 'react-native';

interface MemoryWarning {
  level: 'low' | 'medium' | 'high';
  timestamp: number;
  heapUsed: number;
  heapTotal: number;
}

class MemoryMonitor {
  private listeners: ((warning: MemoryWarning) => void)[] = [];
  private monitoring = false;
  private interval: NodeJS.Timeout | null = null;
  
  startMonitoring(intervalMs = 5000) {
    if (this.monitoring) return;
    
    this.monitoring = true;
    this.interval = setInterval(() => {
      this.checkMemoryUsage();
    }, intervalMs);
    
    console.log('🔍 内存监控已启动');
  }
  
  stopMonitoring() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
    this.monitoring = false;
    console.log('⏹️ 内存监控已停止');
  }
  
  private checkMemoryUsage() {
    if (typeof global.gc === 'function') {
      global.gc();
    }
    
    const memUsage = process.memoryUsage();
    const heapUsedMB = memUsage.heapUsed / 1024 / 1024;
    const heapTotalMB = memUsage.heapTotal / 1024 / 1024;
    const usagePercent = (heapUsedMB / heapTotalMB) * 100;
    
    let level: 'low' | 'medium' | 'high' = 'low';
    
    if (usagePercent > 80) {
      level = 'high';
    } else if (usagePercent > 60) {
      level = 'medium';
    }
    
    if (level !== 'low') {
      const warning: MemoryWarning = {
        level,
        timestamp: Date.now(),
        heapUsed: heapUsedMB,
        heapTotal: heapTotalMB
      };
      
      this.notifyListeners(warning);
      DeviceEventEmitter.emit('memoryWarning', warning);
    }
  }
  
  addListener(callback: (warning: MemoryWarning) => void) {
    this.listeners.push(callback);
  }
  
  removeListener(callback: (warning: MemoryWarning) => void) {
    const index = this.listeners.indexOf(callback);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }
  
  private notifyListeners(warning: MemoryWarning) {
    this.listeners.forEach(listener => {
      try {
        listener(warning);
      } catch (error) {
        console.error('内存监控回调错误:', error);
      }
    });
  }
  
  getCurrentUsage() {
    const memUsage = process.memoryUsage();
    return {
      heapUsed: memUsage.heapUsed / 1024 / 1024,
      heapTotal: memUsage.heapTotal / 1024 / 1024,
      external: memUsage.external / 1024 / 1024,
      rss: memUsage.rss / 1024 / 1024
    };
  }
}

export const memoryMonitor = new MemoryMonitor();
export default memoryMonitor;