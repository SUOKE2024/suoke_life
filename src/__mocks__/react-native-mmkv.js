// Mock storage object
const mockStorage = new Map();

export class MMKV {
  constructor(options = {}) {
    this.id = options.id || 'default';
    this.storage = mockStorage;
  }

  set(key, value) {
    this.storage.set(`${this.id}:${key}`, value);
  }

  getString(key) {
    return this.storage.get(`${this.id}:${key}`);
  }

  getNumber(key) {
    const value = this.storage.get(`${this.id}:${key}`);
    return typeof value === 'number' ? value : undefined;
  }

  getBoolean(key) {
    const value = this.storage.get(`${this.id}:${key}`);
    return typeof value === 'boolean' ? value : undefined;
  }

  getBuffer(key) {
    const value = this.storage.get(`${this.id}:${key}`);
    return value instanceof ArrayBuffer ? value : undefined;
  }

  contains(key) {
    return this.storage.has(`${this.id}:${key}`);
  }

  delete(key) {
    return this.storage.delete(`${this.id}:${key}`);
  }

  getAllKeys() {
    const prefix = `${this.id}:`;
    return Array.from(this.storage.keys())
      .filter(key => key.startsWith(prefix))
      .map(key => key.substring(prefix.length));
  }

  clearAll() {
    const prefix = `${this.id}:`;
    const keysToDelete = Array.from(this.storage.keys())
      .filter(key => key.startsWith(prefix));
    
    keysToDelete.forEach(key => this.storage.delete(key));
  }

  recrypt(cryptKey) {
    // Mock implementation - do nothing
  }

  // Static methods
  static getAllInstanceIDs() {
    return ['default'];
  }

  static getCurrentMMKVInstanceIDs() {
    return ['default'];
  }
}

// Default instance
export const defaultMMKV = new MMKV();

// Export for backward compatibility
export default MMKV; 