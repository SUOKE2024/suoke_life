// React Native 全局变量声明
declare var __DEV__: boolean;

// 模块声明
declare module '*.png' {
  const value: any;
  export default value;
}

declare module '*.jpg' {
  const value: any;
  export default value;
}

declare module '*.jpeg' {
  const value: any;
  export default value;
}

declare module '*.gif' {
  const value: any;
  export default value;
}

declare module '*.svg' {
  const value: any;
  export default value;
}

declare module '*.json' {
  const value: any;
  export default value;
}

// 扩展全局命名空间
declare global {
  var __DEV__: boolean;

  // React Native 全局接口
  interface Window {
    __DEV__: boolean;
  }

  // 错误处理类型
  interface Error {
    code?: string;
    details?: any;
  }
}

// 第三方库类型扩展
declare module 'react-native-sqlite-storage' {
  export interface SQLiteDatabase {
    transaction: (fn: (tx: SQLTransaction) => void) => Promise<void>;
    executeSql: (sql: string, params?: any[]) => Promise<any>;
    close: () => Promise<void>;
  }

  export interface SQLTransaction {
    executeSql: (
      sql: string,
      params?: any[],
      success?: (tx: SQLTransaction, result: SQLResultSet) => void,
      error?: (tx: SQLTransaction, error: SQLError) => void
    ) => void;
  }

  export interface SQLResultSet {
    rows: SQLResultSetRowList;
    insertId?: number;
    rowsAffected: number;
  }

  export interface SQLResultSetRowList {
    length: number;
    item: (index: number) => any;
  }

  export interface SQLError {
    code: number;
    message: string;
  }

  export const openDatabase: (
    name: string,
    version: string,
    displayName: string,
    size: number
  ) => Promise<SQLiteDatabase>;
}

declare module 'react-native-voice' {
  export interface SpeechRecognizedEvent {
    value: string[];
  }

  export interface SpeechResultsEvent {
    value: string[];
  }

  export interface SpeechErrorEvent {
    error: {
      code: string;
      message: string;
    };
  }

  export interface VoiceModule {
    onSpeechStart: (e: any) => void;
    onSpeechRecognized: (e: SpeechRecognizedEvent) => void;
    onSpeechEnd: (e: any) => void;
    onSpeechError: (e: SpeechErrorEvent) => void;
    onSpeechResults: (e: SpeechResultsEvent) => void;
    onSpeechPartialResults: (e: SpeechResultsEvent) => void;
    onSpeechVolumeChanged: (e: any) => void;

    start: (locale?: string) => Promise<void>;
    stop: () => Promise<void>;
    cancel: () => Promise<void>;
    destroy: () => Promise<void>;
    removeAllListeners: () => void;
    isAvailable: () => Promise<boolean>;
    isRecognizing: () => Promise<boolean>;
    getSpeechRecognitionServices: () => Promise<string[]>;
  }

  const Voice: VoiceModule;
  export default Voice;
}

declare module 'react-native-mmkv' {
  export interface MMKVConfiguration {
    id: string;
    path?: string;
    encryptionKey?: string;
  }

  export class MMKV {
    constructor(configuration?: MMKVConfiguration);

    set(key: string, value: string | number | boolean): void;
    getString(key: string): string | undefined;
    getNumber(key: string): number | undefined;
    getBoolean(key: string): boolean | undefined;
    contains(key: string): boolean;
    delete(key: string): void;
    getAllKeys(): string[];
    clearAll(): void;

    // Listeners
    addOnValueChangedListener(
      listener: (changedKey: string) => void
    ): () => void;
  }

  export const MMKVLoader: {
    new (): MMKV;
    withInstanceID(instanceID: string): MMKVLoader;
    withEncryption(): MMKVLoader;
    initialize(): MMKV;
  };
}

// 扩展 React Navigation 类型
declare module '@react-navigation/native' {
  export interface NavigationState {
    key: string;
    index: number;
    routeNames: string[];
    history?: any[];
    routes: any[];
    type: string;
    stale: false;
  }
}

export {};
