// 区块链服务类型定义
// 基于 services/blockchain-service/api/grpc/blockchain.proto
export interface StoreHealthDataRequest {
  userId: string;
  dataType: string;
  data: string;
  metadata?: Record<string, any>;
}
export interface StoreHealthDataResponse {
  success: boolean;
  transactionHash: string;
  blockNumber?: number;
  error?: string;
}
export interface VerifyDataRequest {
  userId: string;
  dataHash: string;
  signature: string;
}
export interface VerifyDataResponse {
  isValid: boolean;
  timestamp?: number;
  error?: string;
}
export interface HealthDataRecord {
  id: string;
  userId: string;
  dataType: string;
  dataHash: string;
  timestamp: number;
  transactionHash: string;
  blockNumber: number;
  metadata?: Record<string, any>;
}
export interface BlockchainConfig {
  networkUrl: string;
  contractAddress: string;
  privateKey?: string;
  gasLimit: number;
  gasPrice: string;
}
export interface TransactionStatus {
  hash: string;
  status: 'pending' | 'confirmed' | 'failed';
  blockNumber?: number;
  gasUsed?: number;
  error?: string;
}
// 错误类型定义
export enum BlockchainErrorCode {
  UNKNOWN = 'UNKNOWN',
  INVALID_REQUEST = 'INVALID_REQUEST',
  DATA_NOT_FOUND = 'DATA_NOT_FOUND',
  PERMISSION_DENIED = 'PERMISSION_DENIED',
  BLOCKCHAIN_ERROR = 'BLOCKCHAIN_ERROR',
  NETWORK_ERROR = 'NETWORK_ERROR',
  ENCRYPTION_ERROR = 'ENCRYPTION_ERROR',
  VERIFICATION_FAILED = 'VERIFICATION_FAILED'
}
export class BlockchainError extends Error {
  constructor(public code: BlockchainErrorCode, public message: string, public details?: any) {
    super(message);
    this.name = 'BlockchainError';
  }
}
// 零知识证明相关类型
export interface ZKProof {
  proof: Uint8Array;
  publicInputs: Uint8Array;
  verificationKey: string;
  circuitType: string;
}
export interface ZKPVerificationResult {
  valid: boolean;
  proofHash: string;
  verificationTimestamp: number;
  verifierSignature: string;
}
// 访问控制类型
export interface AccessGrant {
  id: string;
  userId: string;
  authorizedId: string;
  dataTypes: string[];
  permissions: AccessPermission[];
  expirationTime: number;
  createdAt: number;
  status: AccessGrantStatus;
}
export enum AccessPermission {
  READ = 'READ',
  WRITE = 'WRITE',
  SHARE = 'SHARE',
  DELETE = 'DELETE'
}
export enum AccessGrantStatus {
  ACTIVE = 'ACTIVE',
  EXPIRED = 'EXPIRED',
  REVOKED = 'REVOKED',
  PENDING = 'PENDING'
}
// 区块链状态类型
export interface BlockchainStatus {
  isConnected: boolean;
  currentBlockHeight: number;
  networkId: string;
  consensusStatus: 'SYNCING' | 'SYNCED' | 'ERROR';
  syncPercentage: number;
  lastBlockTimestamp: number;
  nodeCount: number;
  transactionPoolSize: number;
}
// 健康数据类型扩展
export interface HealthDataMetadata {
  source: string;
  version: string;
  checksum: string;
  encryptionAlgorithm: string;
  compressionType?: string;
  tags: string[];
}
export interface EncryptedHealthData {
  encryptedData: Uint8Array;
  encryptionKey: string;
  iv: Uint8Array;
  algorithm: string;
  keyDerivation: {
    algorithm: string;
    salt: Uint8Array;
    iterations: number;
  };
}
