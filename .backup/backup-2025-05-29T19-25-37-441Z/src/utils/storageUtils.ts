/**
 * 本地存储工具
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * 存储数据
 */
export const setStorageItem = async <T>(
  key: string,
  value: T
): Promise<void> => {
  try {
    const jsonValue = JSON.stringify(value);
    await AsyncStorage.setItem(key, jsonValue);
  } catch (error) {
    console.error('存储数据失败:', error);
    throw error;
  }
};

/**
 * 获取数据
 */
export const getStorageItem = async <T>(key: string): Promise<T | null> => {
  try {
    const jsonValue = await AsyncStorage.getItem(key);
    return jsonValue != null ? JSON.parse(jsonValue) : null;
  } catch (error) {
    console.error('获取数据失败:', error);
    return null;
  }
};

/**
 * 删除数据
 */
export const removeStorageItem = async (key: string): Promise<void> => {
  try {
    await AsyncStorage.removeItem(key);
  } catch (error) {
    console.error('删除数据失败:', error);
    throw error;
  }
};

/**
 * 清空所有数据
 */
export const clearStorage = async (): Promise<void> => {
  try {
    await AsyncStorage.clear();
  } catch (error) {
    console.error('清空数据失败:', error);
    throw error;
  }
};

/**
 * 获取所有keys
 */
export const getAllKeys = async (): Promise<string[]> => {
  try {
    const keys = await AsyncStorage.getAllKeys();
    return [...keys];
  } catch (error) {
    console.error('获取所有keys失败:', error);
    return [];
  }
};

/**
 * 批量存储
 */
export const multiSet = async (
  keyValuePairs: [string, any][]
): Promise<void> => {
  try {
    const stringPairs: [string, string][] = keyValuePairs.map(
      ([key, value]) => [key, JSON.stringify(value)]
    );
    await AsyncStorage.multiSet(stringPairs);
  } catch (error) {
    console.error('批量存储失败:', error);
    throw error;
  }
};

/**
 * 批量获取
 */
export const multiGet = async (
  keys: string[]
): Promise<{ [key: string]: any }> => {
  try {
    const keyValuePairs = await AsyncStorage.multiGet(keys);
    const result: { [key: string]: any } = {};

    keyValuePairs.forEach(([key, value]) => {
      try {
        result[key] = value ? JSON.parse(value) : null;
      } catch {
        result[key] = value;
      }
    });

    return result;
  } catch (error) {
    console.error('批量获取失败:', error);
    return {};
  }
};

/**
 * 批量删除
 */
export const multiRemove = async (keys: string[]): Promise<void> => {
  try {
    await AsyncStorage.multiRemove(keys);
  } catch (error) {
    console.error('批量删除失败:', error);
    throw error;
  }
};

/**
 * 检查key是否存在
 */
export const hasStorageItem = async (key: string): Promise<boolean> => {
  try {
    const value = await AsyncStorage.getItem(key);
    return value !== null;
  } catch (error) {
    console.error('检查key存在性失败:', error);
    return false;
  }
};

/**
 * 存储工具类
 */
export class StorageManager {
  private prefix: string;

  constructor(prefix: string = '') {
    this.prefix = prefix;
  }

  private getKey(key: string): string {
    return this.prefix ? `${this.prefix}_${key}` : key;
  }

  async set<T>(key: string, value: T): Promise<void> {
    return setStorageItem(this.getKey(key), value);
  }

  async get<T>(key: string): Promise<T | null> {
    return getStorageItem<T>(this.getKey(key));
  }

  async remove(key: string): Promise<void> {
    return removeStorageItem(this.getKey(key));
  }

  async has(key: string): Promise<boolean> {
    return hasStorageItem(this.getKey(key));
  }

  async clear(): Promise<void> {
    if (!this.prefix) {
      return clearStorage();
    }

    const allKeys = await getAllKeys();
    const prefixedKeys = allKeys.filter((key) => key.startsWith(this.prefix));
    return multiRemove(prefixedKeys);
  }
}
