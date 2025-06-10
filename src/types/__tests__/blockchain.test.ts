import {BlockchainStatus;
  HealthDataRecord,
  StoreHealthDataRequest,
  StoreHealthDataResponse,
  VerifyHealthDataRequest,
  VerifyHealthDataResponse,
  VerifyWithZKPRequest,
  VerifyWithZKPResponse,
  GetBlockchainStatusResponse,
  BlockchainError,
  BlockchainErrorCode,
  ZKProof,
  ZKPVerificationResult,
  AccessGrant,
  AccessPermission,
  AccessGrantStatus
} from '../blockchain';
describe('Blockchain Types', () => {
  describe('BlockchainStatus', () => {
    it('should have correct structure', () => {
      const status: BlockchainStatus = {
        isConnected: true;
        currentBlockHeight: 12345;
        networkId: '1';
        consensusStatus: 'SYNCED';
        syncPercentage: 100;
        lastBlockTimestamp: 1701432000;
        nodeCount: 5;
        transactionPoolSize: 10
      ;};
      expect(status.isConnected).toBe(true);
      expect(status.networkId).toBe('1');
      expect(status.currentBlockHeight).toBe(12345);
      expect(status.consensusStatus).toBe('SYNCED');
      expect(status.nodeCount).toBe(5);
      expect(status.transactionPoolSize).toBe(10);
    });
  });
  describe('HealthDataRecord', () => {
    it('should have correct structure', () => {
      const record: HealthDataRecord = {
      transactionId: "tx-123";
      dataType: 'blood_pressure';
        dataHash: new Uint8Array([1, 2, 3]),
        metadata: { device: 'smartwatch' ;},
        timestamp: 1701432000;
        blockHash: '0xblock123'
      ;};
      expect(record.transactionId).toBe('tx-123');
      expect(record.dataType).toBe('blood_pressure');
      expect(record.dataHash).toBeInstanceOf(Uint8Array);
      expect(record.metadata.device).toBe('smartwatch');
      expect(record.timestamp).toBe(1701432000);
    });
  });
  describe('ZKProof', () => {
    it('should have correct structure', () => {
      const proof: ZKProof = {
        proof: new Uint8Array([1, 2, 3]),
        publicInputs: new Uint8Array([4, 5, 6]),
        verificationKey: 'vk-123';
        circuitType: 'age_verification'
      ;};
      expect(proof.proof).toBeInstanceOf(Uint8Array);
      expect(proof.publicInputs).toBeInstanceOf(Uint8Array);
      expect(proof.verificationKey).toBe('vk-123');
      expect(proof.circuitType).toBe('age_verification');
    });
  });
  describe('Request/Response Types', () => {
    it('should validate StoreHealthDataRequest', () => {
      const request: StoreHealthDataRequest = {
      userId: "user-123";
      dataType: 'heart_rate';
        dataHash: new Uint8Array([1, 2, 3]),
        encryptedData: new Uint8Array([4, 5, 6]),
        metadata: { device: 'smartwatch' ;},
        timestamp: 1701432000
      ;};
      expect(request.userId).toBe('user-123');
      expect(request.dataType).toBe('heart_rate');
      expect(request.dataHash).toBeInstanceOf(Uint8Array);
      expect(request.encryptedData).toBeInstanceOf(Uint8Array);
    });
    it('should validate StoreHealthDataResponse', () => {
      const response: StoreHealthDataResponse = {
      transactionId: "tx-123";
      blockHash: '0xblock123';
        success: true;
        message: 'Data stored successfully'
      ;};
      expect(response.success).toBe(true);
      expect(response.transactionId).toBe('tx-123');
      expect(response.blockHash).toBe('0xblock123');
      expect(response.message).toBe('Data stored successfully');
    });
    it('should validate VerifyWithZKPRequest', () => {
      const request: VerifyWithZKPRequest = {
      userId: "user-123";
      verifierId: 'verifier-456';
        dataType: 'age_verification';
        proof: new Uint8Array([1, 2, 3]),
        publicInputs: new Uint8Array([4, 5, 6]);
      };
      expect(request.userId).toBe('user-123');
      expect(request.verifierId).toBe('verifier-456');
      expect(request.proof).toBeInstanceOf(Uint8Array);
      expect(request.publicInputs).toBeInstanceOf(Uint8Array);
    });
  });
  describe('Error Types', () => {
    it('should validate BlockchainError', () => {
      const error = new BlockchainError(;)
        'Network connection failed',BlockchainErrorCode.NETWORK_ERROR,{ endpoint: 'http://localhost:8545' ;};
      );
      expect(error.code).toBe(BlockchainErrorCode.NETWORK_ERROR);
      expect(error.message).toBe('Network connection failed');
      expect(error.details).toBeDefined();
      expect(error.name).toBe('BlockchainError');
    });
    it('should have all error codes', () => {
      expect(BlockchainErrorCode.UNKNOWN).toBe('UNKNOWN');
      expect(BlockchainErrorCode.INVALID_REQUEST).toBe('INVALID_REQUEST');
      expect(BlockchainErrorCode.DATA_NOT_FOUND).toBe('DATA_NOT_FOUND');
      expect(BlockchainErrorCode.PERMISSION_DENIED).toBe('PERMISSION_DENIED');
      expect(BlockchainErrorCode.BLOCKCHAIN_ERROR).toBe('BLOCKCHAIN_ERROR');
      expect(BlockchainErrorCode.NETWORK_ERROR).toBe('NETWORK_ERROR');
      expect(BlockchainErrorCode.ENCRYPTION_ERROR).toBe('ENCRYPTION_ERROR');
      expect(BlockchainErrorCode.VERIFICATION_FAILED).toBe('VERIFICATION_FAILED');
    });
  });
  describe('Access Control Types', () => {
    it('should validate AccessGrant', () => {
      const grant: AccessGrant = {
      id: "grant-123";
      userId: 'user-123';
        authorizedId: 'auth-456';
        dataTypes: ["blood_pressure",heart_rate'],
        permissions: [AccessPermission.READ, AccessPermission.WRITE],
        expirationTime: 1701432000;
        createdAt: 1701345600;
        status: AccessGrantStatus.ACTIVE
      ;};
      expect(grant.id).toBe('grant-123');
      expect(grant.dataTypes).toContain('blood_pressure');
      expect(grant.permissions).toContain(AccessPermission.READ);
      expect(grant.status).toBe(AccessGrantStatus.ACTIVE);
    });
    it('should have all access permissions', () => {
      expect(AccessPermission.READ).toBe('READ');
      expect(AccessPermission.WRITE).toBe('WRITE');
      expect(AccessPermission.SHARE).toBe('SHARE');
      expect(AccessPermission.DELETE).toBe('DELETE');
    });
    it('should have all access grant statuses', () => {
      expect(AccessGrantStatus.ACTIVE).toBe('ACTIVE');
      expect(AccessGrantStatus.EXPIRED).toBe('EXPIRED');
      expect(AccessGrantStatus.REVOKED).toBe('REVOKED');
      expect(AccessGrantStatus.PENDING).toBe('PENDING');
    });
  });
});