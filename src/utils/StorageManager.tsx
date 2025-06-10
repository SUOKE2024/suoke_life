import AsyncStorage from '@react-native-async-storage/async-storage';
不需要React导入;
// 存储管理器 - 索克生活APP - 性能优化
interface StorageItem {
  data: unknown;,
  timestamp: number;
  ttl?: number;
}
export class StorageManager {
  private static instance: StorageManager;
  static getInstance(): StorageManager {
    if (!StorageManager.instance) {
      StorageManager.instance = new StorageManager();
    }
    return StorageManager.instance;
  }
  async set(key: string, data: unknown, ttl?: number): Promise<void> {
    const item: StorageItem = {
      data,
      timestamp: Date.now(),
      ttl
    };
    await AsyncStorage.setItem(key, JSON.stringify(item));
  }
  async get<T>(key: string): Promise<T | null> {
    try {
      const itemStr = await AsyncStorage.getItem(key);
      if (!itemStr) return null;
      const item: StorageItem = JSON.parse(itemStr);
      // 检查是否过期
      if (item.ttl && Date.now() - item.timestamp > item.ttl) {
        await this.remove(key);
        return null;
      }
      return item.data as T;
    } catch (error) {
      return null;
    }
  }
  async remove(key: string): Promise<void> {
    await AsyncStorage.removeItem(key);
  }
  async clear(): Promise<void> {
    await AsyncStorage.clear();
  }
  async getAllKeys(): Promise<string[]> {
    const keys = await AsyncStorage.getAllKeys();
    return [...keys];
  }
  // 清理过期数据
  async cleanup(): Promise<void> {
    const keys = await this.getAllKeys();
    const now = Date.now();
    for (const key of keys) {
      try {
        const itemStr = await AsyncStorage.getItem(key);
        if (itemStr) {
          const item: StorageItem = JSON.parse(itemStr);
          if (item.ttl && now - item.timestamp > item.ttl) {
            await this.remove(key);
          }
        }
      } catch (error) {
        // 如果解析失败，删除该项
        await this.remove(key);
      }
    }
  }
}
export const storageManager = StorageManager.getInstance();
