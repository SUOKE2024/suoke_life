// 区块链服务类型定义/;/g/;
// 基于 services/blockchain-service/api/grpc/blockchain.proto;/;,/g/;
export interface StoreHealthDataRequest {userId: string}dataType: string,;
dataHash: Uint8Array,;
encryptedData: Uint8Array,;
metadata: Record<string, string>;
}
}
  const timestamp = number;}
}
export interface StoreHealthDataResponse {transactionId: string}blockHash: string,;
success: boolean,;
}
}
  const message = string;}
}
export interface VerifyHealthDataRequest {transactionId: string,;}}
}
  const dataHash = Uint8Array;}
}
export interface VerifyHealthDataResponse {valid: boolean}message: string,;
}
}
  const verificationTimestamp = number;}
}
export interface VerifyWithZKPRequest {userId: string}verifierId: string,;
dataType: string,;
proof: Uint8Array,;
}
}
  const publicInputs = Uint8Array;}
}
export interface VerifyWithZKPResponse {valid: boolean}message: string,;
}
}
  verificationDetails: Record<string, string>;}
}
export interface GetHealthDataRecordsRequest {;,}const userId = string;
dataType?: string;
startTime?: number;
endTime?: number;
page: number,;
}
}
  const pageSize = number;}
}
export interface HealthDataRecord {transactionId: string}dataType: string,;
dataHash: Uint8Array,;
metadata: Record<string, string>;
timestamp: number,;
}
}
  const blockHash = string;}
}
export interface GetHealthDataRecordsResponse {records: HealthDataRecord[]}totalCount: number,;
page: number,;
}
}
  const pageSize = number;}
}
export interface AuthorizeAccessRequest {userId: string}authorizedId: string,;
dataTypes: string[],;
expirationTime: number,;
}
}
  accessPolicies: Record<string, string>;}
}
export interface AuthorizeAccessResponse {authorizationId: string}success: boolean,;
}
}
  const message = string;}
}
export interface RevokeAccessRequest {authorizationId: string}const userId = string;
}
}
  revocationReason?: string;}
}
export interface RevokeAccessResponse {success: boolean}message: string,;
}
}
  const revocationTimestamp = number;}
}
export interface GetBlockchainStatusRequest {;}}
}
  const includeNodeInfo = boolean;}
}
export interface GetBlockchainStatusResponse {currentBlockHeight: number}connectedNodes: number,;
consensusStatus: string,;
syncPercentage: number,;
nodeInfo: Record<string, string>;
}
}
  const lastBlockTimestamp = number;}
}
// 错误类型定义/;,/g/;
export enum BlockchainErrorCode {UNKNOWN = 'UNKNOWN',';,}INVALID_REQUEST = 'INVALID_REQUEST',';,'';
DATA_NOT_FOUND = 'DATA_NOT_FOUND',';,'';
PERMISSION_DENIED = 'PERMISSION_DENIED',';,'';
BLOCKCHAIN_ERROR = 'BLOCKCHAIN_ERROR',';,'';
NETWORK_ERROR = 'NETWORK_ERROR',';,'';
ENCRYPTION_ERROR = 'ENCRYPTION_ERROR',';'';
}
}
  VERIFICATION_FAILED = 'VERIFICATION_FAILED',}'';'';
}
export class BlockchainError extends Error {constructor(public code: BlockchainErrorCode,);,}const message = string;);
const public = details?: any);
  ) {';,}super(message);';'';
}
    this.name = 'BlockchainError';'}'';'';
  }
}
// 零知识证明相关类型/;,/g/;
export interface ZKProof {proof: Uint8Array}publicInputs: Uint8Array,;
verificationKey: string,;
}
}
  const circuitType = string;}
}
export interface ZKPVerificationResult {valid: boolean}proofHash: string,;
verificationTimestamp: number,;
}
}
  const verifierSignature = string;}
}
// 访问控制类型/;,/g/;
export interface AccessGrant {id: string}userId: string,;
authorizedId: string,;
dataTypes: string[],;
permissions: AccessPermission[],;
expirationTime: number,;
createdAt: number,;
}
}
  const status = AccessGrantStatus;}
}';,'';
export enum AccessPermission {';,}READ = 'READ',';,'';
WRITE = 'WRITE',';,'';
SHARE = 'SHARE',';'';
}
}
  DELETE = 'DELETE',}'';'';
}';,'';
export enum AccessGrantStatus {';,}ACTIVE = 'ACTIVE',';,'';
EXPIRED = 'EXPIRED',';,'';
REVOKED = 'REVOKED',';'';
}
}
  PENDING = 'PENDING',}'';'';
}
// 区块链状态类型/;,/g/;
export interface BlockchainStatus {isConnected: boolean}currentBlockHeight: number,';,'';
networkId: string,';,'';
consensusStatus: 'SYNCING' | 'SYNCED' | 'ERROR';','';
syncPercentage: number,;
lastBlockTimestamp: number,;
nodeCount: number,;
}
}
  const transactionPoolSize = number;}
}
// 健康数据类型扩展/;,/g/;
export interface HealthDataMetadata {source: string}version: string,;
checksum: string,;
const encryptionAlgorithm = string;
compressionType?: string;
}
}
  const tags = string[];}
}
export interface EncryptedHealthData {encryptedData: Uint8Array}encryptionKey: string,;
iv: Uint8Array,;
algorithm: string,;
keyDerivation: {algorithm: string,;
salt: Uint8Array,;
}
}
    const iterations = number;}
  };
}';'';
''';