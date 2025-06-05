import { useState, useEffect, useCallback, useRef } from 'react';
import {
  StoreHealthDataRequest,
  StoreHealthDataResponse,
  VerifyHealthDataRequest,
  VerifyHealthDataResponse,
  VerifyWithZKPRequest,
  VerifyWithZKPResponse,
  GetHealthDataRecordsRequest,
  GetHealthDataRecordsResponse,
  AuthorizeAccessRequest,
  AuthorizeAccessResponse,
  RevokeAccessRequest,
  RevokeAccessResponse,
  GetBlockchainStatusRequest,
  GetBlockchainStatusResponse,
  BlockchainError,
  BlockchainErrorCode,
  ZKProof,
  AccessGrant,
  BlockchainStatus,
  HealthDataRecord
} from '../types/blockchain';
import { getBlockchainServiceClient } from '../services/blockchain/BlockchainServiceClient';

interface UseBlockchainServiceState {
  isLoading: boolean;
  error: BlockchainError | null;
  blockchainStatus: BlockchainStatus | null;
  healthDataRecords: HealthDataRecord[];
  accessGrants: AccessGrant[];
  lastOperation: string | null;
}

interface UseBlockchainServiceActions {
  storeHealthData: (request: StoreHealthDataRequest) => Promise<StoreHealthDataResponse>;
  verifyHealthData: (request: VerifyHealthDataRequest) => Promise<VerifyHealthDataResponse>;
  verifyWithZKP: (request: VerifyWithZKPRequest) => Promise<VerifyWithZKPResponse>;
  getHealthDataRecords: (request: GetHealthDataRecordsRequest) => Promise<GetHealthDataRecordsResponse>;
  authorizeAccess: (request: AuthorizeAccessRequest) => Promise<AuthorizeAccessResponse>;
  revokeAccess: (request: RevokeAccessRequest) => Promise<RevokeAccessResponse>;
  getBlockchainStatus: (request: GetBlockchainStatusRequest) => Promise<GetBlockchainStatusResponse>;
  generateZKProof: (userId: string, dataType: string, privateInputs: Record<string, any>, circuitType: string) => Promise<ZKProof>;
  refreshBlockchainStatus: () => Promise<void>;
  refreshHealthDataRecords: (userId: string) => Promise<void>;
  refreshAccessGrants: (userId: string) => Promise<void>;
  clearError: () => void;
  batchStoreHealthData: (requests: StoreHealthDataRequest[]) => Promise<StoreHealthDataResponse[]>;
}

export function useBlockchainService(): UseBlockchainServiceState & UseBlockchainServiceActions {
  const [state, setState] = useState<UseBlockchainServiceState>({
    isLoading: false,
    error: null,
    blockchainStatus: null,
    healthDataRecords: [],
    accessGrants: [],
    lastOperation: null
  });

  const clientRef = useRef(getBlockchainServiceClient());
  const abortControllerRef = useRef<AbortController | null>(null);

  // 清理函数
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  // 通用的异步操作包装器
  const withAsyncOperation = useCallback(async <T>(
    operation: () => Promise<T>,
    operationName: string
  ): Promise<T> => {
    // 取消之前的操作
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    setState(prev => ({
      ...prev,
      isLoading: true,
      error: null,
      lastOperation: operationName
    }));

    try {
      const result = await operation();
      
      setState(prev => ({
        ...prev,
        isLoading: false,
        lastOperation: null
      }));

      return result;
    } catch (error) {
      const blockchainError = error instanceof BlockchainError 
        ? error 
        : new BlockchainError(
            `${operationName}失败: ${error instanceof Error ? error.message : '未知错误'}`,
            BlockchainErrorCode.UNKNOWN,
            error
          );

      setState(prev => ({
        ...prev,
        isLoading: false,
        error: blockchainError,
        lastOperation: null
      }));

      throw blockchainError;
    }
  }, []);

  // 存储健康数据
  const storeHealthData = useCallback(async (request: StoreHealthDataRequest): Promise<StoreHealthDataResponse> => {
    return withAsyncOperation(
      () => clientRef.current.storeHealthData(request),
      '存储健康数据'
    );
  }, [withAsyncOperation]);

  // 验证健康数据
  const verifyHealthData = useCallback(async (request: VerifyHealthDataRequest): Promise<VerifyHealthDataResponse> => {
    return withAsyncOperation(
      () => clientRef.current.verifyHealthData(request),
      '验证健康数据'
    );
  }, [withAsyncOperation]);

  // 零知识证明验证
  const verifyWithZKP = useCallback(async (request: VerifyWithZKPRequest): Promise<VerifyWithZKPResponse> => {
    return withAsyncOperation(
      () => clientRef.current.verifyWithZKP(request),
      '零知识证明验证'
    );
  }, [withAsyncOperation]);

  // 获取健康数据记录
  const getHealthDataRecords = useCallback(async (request: GetHealthDataRecordsRequest): Promise<GetHealthDataRecordsResponse> => {
    const response = await withAsyncOperation(
      () => clientRef.current.getHealthDataRecords(request),
      '获取健康数据记录'
    );

    setState(prev => ({
      ...prev,
      healthDataRecords: response.records
    }));

    return response;
  }, [withAsyncOperation]);

  // 授权访问
  const authorizeAccess = useCallback(async (request: AuthorizeAccessRequest): Promise<AuthorizeAccessResponse> => {
    return withAsyncOperation(
      () => clientRef.current.authorizeAccess(request),
      '授权访问'
    );
  }, [withAsyncOperation]);

  // 撤销访问
  const revokeAccess = useCallback(async (request: RevokeAccessRequest): Promise<RevokeAccessResponse> => {
    return withAsyncOperation(
      () => clientRef.current.revokeAccess(request),
      '撤销访问'
    );
  }, [withAsyncOperation]);

  // 获取区块链状态
  const getBlockchainStatus = useCallback(async (request: GetBlockchainStatusRequest): Promise<GetBlockchainStatusResponse> => {
    const response = await withAsyncOperation(
      () => clientRef.current.getBlockchainStatus(request),
      '获取区块链状态'
    );

    setState(prev => ({
      ...prev,
      blockchainStatus: {
        isConnected: true,
        currentBlockHeight: response.currentBlockHeight,
        networkId: 'suoke-network',
        consensusStatus: response.consensusStatus as any,
        syncPercentage: response.syncPercentage,
        lastBlockTimestamp: response.lastBlockTimestamp,
        nodeCount: response.connectedNodes,
        transactionPoolSize: 0
      }
    }));

    return response;
  }, [withAsyncOperation]);

  // 生成零知识证明
  const generateZKProof = useCallback(async (
    userId: string,
    dataType: string,
    privateInputs: Record<string, any>,
    circuitType: string
  ): Promise<ZKProof> => {
    return withAsyncOperation(
      () => clientRef.current.generateZKProof(userId, dataType, privateInputs, circuitType),
      '生成零知识证明'
    );
  }, [withAsyncOperation]);

  // 批量存储健康数据
  const batchStoreHealthData = useCallback(async (requests: StoreHealthDataRequest[]): Promise<StoreHealthDataResponse[]> => {
    return withAsyncOperation(
      () => clientRef.current.batchStoreHealthData(requests),
      '批量存储健康数据'
    );
  }, [withAsyncOperation]);

  // 刷新区块链状态
  const refreshBlockchainStatus = useCallback(async (): Promise<void> => {
    try {
      const status = await clientRef.current.getNetworkStats();
      setState(prev => ({
        ...prev,
        blockchainStatus: status
      }));
    } catch (error) {
      console.warn('刷新区块链状态失败:', error);
    }
  }, []);

  // 刷新健康数据记录
  const refreshHealthDataRecords = useCallback(async (userId: string): Promise<void> => {
    try {
      const response = await clientRef.current.getHealthDataRecords({
        userId,
        page: 1,
        pageSize: 50
      });
      setState(prev => ({
        ...prev,
        healthDataRecords: response.records
      }));
    } catch (error) {
      console.warn('刷新健康数据记录失败:', error);
    }
  }, []);

  // 刷新访问授权列表
  const refreshAccessGrants = useCallback(async (userId: string): Promise<void> => {
    try {
      const grants = await clientRef.current.getAccessGrants(userId);
      setState(prev => ({
        ...prev,
        accessGrants: grants
      }));
    } catch (error) {
      console.warn('刷新访问授权列表失败:', error);
    }
  }, []);

  // 清除错误
  const clearError = useCallback(() => {
    setState(prev => ({
      ...prev,
      error: null
    }));
  }, []);

  // 自动刷新区块链状态
  useEffect(() => {
    const interval = setInterval(() => {
      refreshBlockchainStatus();
    }, 30000); // 每30秒刷新一次

    // 初始加载
    refreshBlockchainStatus();

    return () => clearInterval(interval);
  }, [refreshBlockchainStatus]);

  return {
    // 状态
    ...state,
    
    // 操作
    storeHealthData,
    verifyHealthData,
    verifyWithZKP,
    getHealthDataRecords,
    authorizeAccess,
    revokeAccess,
    getBlockchainStatus,
    generateZKProof,
    batchStoreHealthData,
    refreshBlockchainStatus,
    refreshHealthDataRecords,
    refreshAccessGrants,
    clearError
  };
}

// 专门用于区块链状态监控的Hook
export function useBlockchainStatusMonitor() {
  const [status, setStatus] = useState<BlockchainStatus | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const clientRef = useRef(getBlockchainServiceClient());

  const checkStatus = useCallback(async () => {
    try {
      const networkStats = await clientRef.current.getNetworkStats();
      setStatus(networkStats);
      setIsConnected(networkStats.isConnected);
      setLastUpdate(new Date());
    } catch (error) {
      setIsConnected(false);
      console.warn('区块链状态检查失败:', error);
    }
  }, []);

  useEffect(() => {
    // 立即检查一次
    checkStatus();

    // 设置定期检查
    const interval = setInterval(checkStatus, 10000); // 每10秒检查一次

    return () => clearInterval(interval);
  }, [checkStatus]);

  return {
    status,
    isConnected,
    lastUpdate,
    refresh: checkStatus
  };
}

// 专门用于健康数据操作的Hook
export function useHealthDataOperations(userId: string) {
  const {
    storeHealthData,
    verifyHealthData,
    getHealthDataRecords,
    batchStoreHealthData,
    isLoading,
    error,
    healthDataRecords
  } = useBlockchainService();

  const [localRecords, setLocalRecords] = useState<HealthDataRecord[]>([]);

  // 存储单个健康数据
  const storeData = useCallback(async (
    dataType: string,
    data: any,
    metadata?: Record<string, string>
  ) => {
    const dataString = JSON.stringify(data);
    const encoder = new TextEncoder();
    const dataBytes = encoder.encode(dataString);
    
    // 计算数据哈希
    const hashBuffer = await crypto.subtle.digest('SHA-256', dataBytes);
    const dataHash = new Uint8Array(hashBuffer);

    // 简单加密（实际应用中应使用更强的加密）
    const encryptedData = dataBytes; // 这里应该实现真正的加密

    const request: StoreHealthDataRequest = {
      userId,
      dataType,
      dataHash,
      encryptedData,
      metadata: metadata || {},
      timestamp: Date.now()
    };

    const response = await storeHealthData(request);
    
    // 更新本地记录
    const newRecord: HealthDataRecord = {
      transactionId: response.transactionId,
      dataType,
      dataHash,
      metadata: request.metadata,
      timestamp: request.timestamp,
      blockHash: response.blockHash
    };

    setLocalRecords(prev => [newRecord, ...prev]);
    
    return response;
  }, [userId, storeHealthData]);

  // 批量存储健康数据
  const storeBatchData = useCallback(async (
    dataItems: Array<{
      dataType: string;
      data: any;
      metadata?: Record<string, string>;
    }>
  ) => {
    const requests: StoreHealthDataRequest[] = [];
    
    for (const item of dataItems) {
      const dataString = JSON.stringify(item.data);
      const encoder = new TextEncoder();
      const dataBytes = encoder.encode(dataString);
      
      const hashBuffer = await crypto.subtle.digest('SHA-256', dataBytes);
      const dataHash = new Uint8Array(hashBuffer);
      const encryptedData = dataBytes;

      requests.push({
        userId,
        dataType: item.dataType,
        dataHash,
        encryptedData,
        metadata: item.metadata || {},
        timestamp: Date.now()
      });
    }

    const responses = await batchStoreHealthData(requests);
    
    // 更新本地记录
    const newRecords: HealthDataRecord[] = responses.map((response, index) => ({
      transactionId: response.transactionId,
      dataType: requests[index].dataType,
      dataHash: requests[index].dataHash,
      metadata: requests[index].metadata,
      timestamp: requests[index].timestamp,
      blockHash: response.blockHash
    }));

    setLocalRecords(prev => [...newRecords, ...prev]);
    
    return responses;
  }, [userId, batchStoreHealthData]);

  // 验证数据完整性
  const verifyData = useCallback(async (transactionId: string, originalData: any) => {
    const dataString = JSON.stringify(originalData);
    const encoder = new TextEncoder();
    const dataBytes = encoder.encode(dataString);
    const hashBuffer = await crypto.subtle.digest('SHA-256', dataBytes);
    const dataHash = new Uint8Array(hashBuffer);

    return verifyHealthData({ transactionId, dataHash });
  }, [verifyHealthData]);

  // 获取用户的所有健康数据记录
  const loadRecords = useCallback(async (options?: {
    dataType?: string;
    startTime?: number;
    endTime?: number;
    page?: number;
    pageSize?: number;
  }) => {
    const response = await getHealthDataRecords({
      userId,
      dataType: options?.dataType,
      startTime: options?.startTime,
      endTime: options?.endTime,
      page: options?.page || 1,
      pageSize: options?.pageSize || 20
    });

    setLocalRecords(response.records);
    return response;
  }, [userId, getHealthDataRecords]);

  // 初始加载
  useEffect(() => {
    loadRecords();
  }, [loadRecords]);

  return {
    records: localRecords.length > 0 ? localRecords : healthDataRecords,
    storeData,
    storeBatchData,
    verifyData,
    loadRecords,
    isLoading,
    error
  };
} 