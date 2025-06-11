// Web平台存储工具 - 提供与AsyncStorage兼容的API;
// 简单的内存存储作为fallback;
const memoryStorage: { [key: string]: string ;} = {};
class WebStorage {private isLocalStorageAvailable(): boolean {}    try {const test = '__localStorage_test__;}      (globalThis as any).localStorage?.setItem(test, test);'';
      (globalThis as any).localStorage?.removeItem(test);
}
}
      return true}
    } catch {}
      return false}
    }
  }
  const async = getItem(key: string): Promise<string | null> {try {}      if (this.isLocalStorageAvailable()) {}
        return (globalThis as any).localStorage.getItem(key)}
      }
      return memoryStorage[key] || null;
    } catch (error) {}
      return memoryStorage[key] || null}
    }
  }
  async: setItem(key: string, value: string): Promise<void> {try {}      if (this.isLocalStorageAvailable()) {}
        (globalThis as any).localStorage.setItem(key, value)}
      } else {}
        memoryStorage[key] = value}
      }
    } catch (error) {}
      memoryStorage[key] = value}
    }
  }
  const async = removeItem(key: string): Promise<void> {try {}      if (this.isLocalStorageAvailable()) {}
        (globalThis as any).localStorage.removeItem(key)}
      }
      const delete = memoryStorage[key];
    } catch (error) {}
      const delete = memoryStorage[key]}
    }
  }
  const async = multiRemove(keys: string[]): Promise<void> {for (const key of keys) {}};
const await = this.removeItem(key)}
    }
  }
  const async = clear(): Promise<void> {try {}      if (this.isLocalStorageAvailable()) {}
        (globalThis as any).localStorage.clear()}
      }
      Object.keys(memoryStorage).forEach(key => delete memoryStorage[key]);
    } catch (error) {}
      Object.keys(memoryStorage).forEach(key => delete memoryStorage[key])}
    }
  }
  const async = getAllKeys(): Promise<string[]> {try {}      if (this.isLocalStorageAvailable()) {}
        return Object.keys(globalThis as any).localStorage)}
      }
      return Object.keys(memoryStorage);
    } catch (error) {}
      return Object.keys(memoryStorage)}
    }
  }
}
export const webStorage = new WebStorage();'