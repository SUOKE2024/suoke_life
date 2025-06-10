import {;
    AccessGrant,
    AuthorizeAccessRequest,
    AuthorizeAccessResponse,
    BlockchainError,
    BlockchainErrorCode,
    BlockchainStatus,
    GetBlockchainStatusRequest,
    GetBlockchainStatusResponse,
    GetHealthDataRecordsRequest,
    GetHealthDataRecordsResponse,
    RevokeAccessRequest,
    RevokeAccessResponse,
    StoreHealthDataRequest,
    StoreHealthDataResponse,
    VerifyHealthDataRequest,
    VerifyHealthDataResponse,
    VerifyWithZKPRequest,
    VerifyWithZKPResponse,
    ZKProof;
} from '../../types/blockchain';

export class BlockchainServiceClient {
  private baseUrl: string;
  private timeout: number;
  private retries: number;

  constructor(config?: {
    baseUrl?: string;
    timeout?: number;
    retries?: number;
  }) {
    this.baseUrl = config?.baseUrl || process.env.BLOCKCHAIN_SERVICE_URL || 'http://localhost:8092';
    this.timeout = config?.timeout || 30000;
    this.retries = config?.retries || 3;
  }

  /**
   * 存储健康数据到区块链
   */
  async storeHealthData(request: StoreHealthDataRequest): Promise<StoreHealthDataResponse> {
    try {
      const response = await this.makeRequest('/api/v1/blockchain/health-data', {
        method: "POST",
        body: {,
  user_id: request.userId,
          data_type: request.dataType,
          data_hash: Array.from(request.dataHash),
          encrypted_data: Array.from(request.encryptedData),
          metadata: request.metadata,
          timestamp: request.timestamp;
        }
      });

      return {
        transactionId: response.transaction_id,
        blockHash: response.block_hash,
        success: response.success,
        message: response.message;
      };
    } catch (error) {
      throw this.handleError(error, '存储健康数据失败');
    }
  }

  /**
   * 验证健康数据完整性
   */
  async verifyHealthData(request: VerifyHealthDataRequest): Promise<VerifyHealthDataResponse> {
    try {
      const response = await this.makeRequest('/api/v1/blockchain/verify', {
        method: "POST",
        body: {,
  transaction_id: request.transactionId,
          data_hash: Array.from(request.dataHash)
        }
      });

      return {
        valid: response.valid,
        message: response.message,
        verificationTimestamp: response.verification_timestamp;
      };
    } catch (error) {
      throw this.handleError(error, '验证健康数据失败');
    }
  }

  /**
   * 使用零知识证明验证健康数据属性
   */
  async verifyWithZKP(request: VerifyWithZKPRequest): Promise<VerifyWithZKPResponse> {
    try {
      const response = await this.makeRequest('/api/v1/blockchain/verify-zkp', {
        method: "POST",
        body: {,
  user_id: request.userId,
          verifier_id: request.verifierId,
          data_type: request.dataType,
          proof: Array.from(request.proof),
          public_inputs: Array.from(request.publicInputs)
        }
      });

      return {
        valid: response.valid,
        message: response.message,
        verificationDetails: response.verification_details;
      };
    } catch (error) {
      throw this.handleError(error, '零知识证明验证失败');
    }
  }

  /**
   * 获取用户健康数据记录
   */
  async getHealthDataRecords(request: GetHealthDataRecordsRequest): Promise<GetHealthDataRecordsResponse> {
    try {
      const params = new URLSearchParams({
        user_id: request.userId,
        page: request.page.toString(),
        page_size: request.pageSize.toString()
      });

      if (request.dataType) params.append('data_type', request.dataType);
      if (request.startTime) params.append('start_time', request.startTime.toString());
      if (request.endTime) params.append('end_time', request.endTime.toString());

      const response = await this.makeRequest(`/api/v1/blockchain/health-records?${params}`, {
        method: 'GET'
      });

      return {
        records: response.records.map(record: any) => ({,
  transactionId: record.transaction_id,
          dataType: record.data_type,
          dataHash: new Uint8Array(record.data_hash),
          metadata: record.metadata,
          timestamp: record.timestamp,
          blockHash: record.block_hash;
        })),
        totalCount: response.total_count,
        page: response.page,
        pageSize: response.page_size;
      };
    } catch (error) {
      throw this.handleError(error, '获取健康数据记录失败');
    }
  }

  /**
   * 授权访问健康数据
   */
  async authorizeAccess(request: AuthorizeAccessRequest): Promise<AuthorizeAccessResponse> {
    try {
      const response = await this.makeRequest('/api/v1/blockchain/authorize', {
        method: "POST",
        body: {,
  user_id: request.userId,
          authorized_id: request.authorizedId,
          data_types: request.dataTypes,
          expiration_time: request.expirationTime,
          access_policies: request.accessPolicies;
        }
      });

      return {
        authorizationId: response.authorization_id,
        success: response.success,
        message: response.message;
      };
    } catch (error) {
      throw this.handleError(error, '授权访问失败');
    }
  }

  /**
   * 撤销访问授权
   */
  async revokeAccess(request: RevokeAccessRequest): Promise<RevokeAccessResponse> {
    try {
      const response = await this.makeRequest('/api/v1/blockchain/revoke', {
        method: "POST",
        body: {,
  authorization_id: request.authorizationId,
          user_id: request.userId,
          revocation_reason: request.revocationReason;
        }
      });

      return {
        success: response.success,
        message: response.message,
        revocationTimestamp: response.revocation_timestamp;
      };
    } catch (error) {
      throw this.handleError(error, '撤销访问授权失败');
    }
  }

  /**
   * 获取区块链状态
   */
  async getBlockchainStatus(request: GetBlockchainStatusRequest): Promise<GetBlockchainStatusResponse> {
    try {
      const params = new URLSearchParams({
        include_node_info: request.includeNodeInfo.toString()
      });

      const response = await this.makeRequest(`/api/v1/blockchain/status?${params}`, {
        method: 'GET'
      });

      return {
        currentBlockHeight: response.current_block_height,
        connectedNodes: response.connected_nodes,
        consensusStatus: response.consensus_status,
        syncPercentage: response.sync_percentage,
        nodeInfo: response.node_info,
        lastBlockTimestamp: response.last_block_timestamp;
      };
    } catch (error) {
      throw this.handleError(error, '获取区块链状态失败');
    }
  }

  /**
   * 生成零知识证明
   */
  async generateZKProof(
    userId: string,
    dataType: string,
    privateInputs: Record<string, any>,
    circuitType: string;
  ): Promise<ZKProof> {
    try {
      const response = await this.makeRequest('/api/v1/blockchain/generate-proof', {
        method: "POST",
        body: {,
  user_id: userId,
          data_type: dataType,
          private_inputs: privateInputs,
          circuit_type: circuitType;
        }
      });

      return {
        proof: new Uint8Array(response.proof),
        publicInputs: new Uint8Array(response.public_inputs),
        verificationKey: response.verification_key,
        circuitType: response.circuit_type;
      };
    } catch (error) {
      throw this.handleError(error, '生成零知识证明失败');
    }
  }

  /**
   * 获取用户的访问授权列表
   */
  async getAccessGrants(userId: string): Promise<AccessGrant[]> {
    try {
      const response = await this.makeRequest(`/api/v1/blockchain/access-grants/${userId}`, {
        method: 'GET'
      });

      return response.grants.map(grant: any) => ({,
  id: grant.id,
        userId: grant.user_id,
        authorizedId: grant.authorized_id,
        dataTypes: grant.data_types,
        permissions: grant.permissions,
        expirationTime: grant.expiration_time,
        createdAt: grant.created_at,
        status: grant.status;
      }));
    } catch (error) {
      throw this.handleError(error, '获取访问授权列表失败');
    }
  }

  /**
   * 获取区块链网络统计信息
   */
  async getNetworkStats(): Promise<BlockchainStatus> {
    try {
      const response = await this.makeRequest('/api/v1/blockchain/network-stats', {
        method: 'GET'
      });

      return {
        isConnected: response.is_connected,
        currentBlockHeight: response.current_block_height,
        networkId: response.network_id,
        consensusStatus: response.consensus_status,
        syncPercentage: response.sync_percentage,
        lastBlockTimestamp: response.last_block_timestamp,
        nodeCount: response.node_count,
        transactionPoolSize: response.transaction_pool_size;
      };
    } catch (error) {
      throw this.handleError(error, '获取网络统计信息失败');
    }
  }

  /**
   * 批量存储健康数据
   */
  async batchStoreHealthData(requests: StoreHealthDataRequest[]): Promise<StoreHealthDataResponse[]> {
    try {
      const response = await this.makeRequest('/api/v1/blockchain/batch-store', {
        method: "POST",
        body: {,
  requests: requests.map(req => ({,
  user_id: req.userId,
            data_type: req.dataType,
            data_hash: Array.from(req.dataHash),
            encrypted_data: Array.from(req.encryptedData),
            metadata: req.metadata,
            timestamp: req.timestamp;
          }))
        }
      });

      return response.results.map(result: any) => ({,
  transactionId: result.transaction_id,
        blockHash: result.block_hash,
        success: result.success,
        message: result.message;
      }));
    } catch (error) {
      throw this.handleError(error, '批量存储健康数据失败');
    }
  }

  /**
   * 发起HTTP请求的通用方法
   */
  private async makeRequest(endpoint: string, options: {,
  method: string;
    body?: any;
    headers?: Record<string, string>;
  }): Promise<any> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers;
    };

    for (let attempt = 0; attempt < this.retries; attempt++) {
      try {
        const response = await fetch(url, {
          method: options.method,
          headers,
          body: options.body ? JSON.stringify(options.body) : undefined,
          signal: AbortSignal.timeout(this.timeout)
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
      } catch (error) {
        if (attempt === this.retries - 1) {
          throw error;
        }
        
        // 等待后重试
        await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
      }
    }
  }

  /**
   * 错误处理方法
   */
  private handleError(error: any, context: string): BlockchainError {
    console.error(`${context}:`, error);

    if (error instanceof BlockchainError) {
      return error;
    }

    let errorCode: BlockchainErrorCode = BlockchainErrorCode.UNKNOWN;
    let message = error.message || '未知错误';

    if (error.name === 'TimeoutError') {
      errorCode = BlockchainErrorCode.NETWORK_ERROR;
      message = '网络请求超时';
    } else if (error.message?.includes('HTTP 4')) {
      errorCode = BlockchainErrorCode.INVALID_REQUEST;
      message = '请求参数无效';
    } else if (error.message?.includes('HTTP 5')) {
      errorCode = BlockchainErrorCode.BLOCKCHAIN_ERROR;
      message = '服务器内部错误';
    }

    return new BlockchainError(errorCode, `${context}: ${message}`, error);
  }
}

// 单例实例
let blockchainServiceClient: BlockchainServiceClient | null = null;

export function getBlockchainServiceClient(): BlockchainServiceClient {
  if (!blockchainServiceClient) {
    blockchainServiceClient = new BlockchainServiceClient();
  }
  return blockchainServiceClient;
}

export function createBlockchainServiceClient(config?: {
  baseUrl?: string;
  timeout?: number;
  retries?: number;
}): BlockchainServiceClient {
  return new BlockchainServiceClient(config);
}