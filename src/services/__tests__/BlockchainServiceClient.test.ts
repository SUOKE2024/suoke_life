import { BlockchainServiceClient } from '../blockchain/BlockchainServiceClient';
import {StoreHealthDataRequest,
  VerifyHealthDataRequest,
  VerifyWithZKPRequest,
  GetHealthDataRecordsRequest,
  AuthorizeAccessRequest,
  RevokeAccessRequest,
  GetBlockchainStatusRequest,
  BlockchainErrorCode
} from '../../types/blockchain';
// Mock fetch
global.fetch = jest.fn();
describe('BlockchainServiceClient', () => {
  let client: BlockchainServiceClient;
  const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
  beforeEach(() => {
    client = new BlockchainServiceClient({ baseUrl: 'http://localhost:8080' });
    mockFetch.mockClear();
  });
  describe('storeHealthData', () => {
    it('should store health data successfully', async () => {
      const request: StoreHealthDataRequest = {
      userId: "user-123",
      dataType: 'blood_pressure',
        dataHash: new Uint8Array([1, 2, 3]),
        encryptedData: new Uint8Array([4, 5, 6]),
        metadata: { device: 'smartwatch' },
        timestamp: 1701432000
      };
      const mockResponse = {
      transaction_id: "tx-123",
      block_hash: '0xblock123',success: true,message: 'Data stored successfully';
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      } as Response);
      const result = await client.storeHealthData(request);
      expect(result.success).toBe(true);
      expect(result.transactionId).toBe('tx-123');
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8080/api/v1/blockchain/health-data',
        expect.objectContaining({
      method: "POST",
      headers: expect.objectContaining({
            'Content-Type': 'application/json'
          });
        })
      );
    });
    it('should handle network errors', async () => {
      const request: StoreHealthDataRequest = {
      userId: "user-123",
      dataType: 'blood_pressure',
        dataHash: new Uint8Array([1, 2, 3]),
        encryptedData: new Uint8Array([4, 5, 6]),
        metadata: { device: 'smartwatch' },
        timestamp: 1701432000
      };
      mockFetch.mockRejectedValueOnce(new Error('Network error'));
      await expect(client.storeHealthData(request)).rejects.toThrow('Network error');
    });
  });
  describe('verifyHealthData', () => {
    it('should verify health data successfully', async () => {
      const request: VerifyHealthDataRequest = {
      transactionId: "tx-123",
      dataHash: new Uint8Array([1, 2, 3]);
      };
      const mockResponse = {valid: true,message: 'Data verified successfully',verification_timestamp: 1701432000;
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      } as Response);
      const result = await client.verifyHealthData(request);
      expect(result.valid).toBe(true);
      expect(result.message).toBe('Data verified successfully');
    });
  });
  describe('verifyWithZKP', () => {
    it('should verify with zero-knowledge proof successfully', async () => {
      const request: VerifyWithZKPRequest = {
      userId: "user-123",
      verifierId: 'verifier-456',
        dataType: 'age_verification',
        proof: new Uint8Array([1, 2, 3]),
        publicInputs: new Uint8Array([4, 5, 6]);
      };
      const mockResponse = {valid: true,message: 'ZKP verification successful',verification_details: { circuit: 'age_verification' };
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      } as Response);
      const result = await client.verifyWithZKP(request);
      expect(result.valid).toBe(true);
      expect(result.message).toBe('ZKP verification successful');
    });
  });
  describe('getHealthDataRecords', () => {
    it('should get health data records successfully', async () => {
      const request: GetHealthDataRecordsRequest = {
      userId: "user-123",
      dataType: 'blood_pressure',
        page: 1,
        pageSize: 10
      };
      const mockResponse = {records: [;
          {
      transaction_id: "tx-123",
      data_type: 'blood_pressure',data_hash: [1, 2, 3],metadata: { device: 'smartwatch' },timestamp: 1701432000,block_hash: '0xblock123';
          };
        ],total_count: 1,page: 1,page_size: 10;
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      } as Response);
      const result = await client.getHealthDataRecords(request);
      expect(result.records).toHaveLength(1);
      expect(result.totalCount).toBe(1);
      expect(result.records[0].transactionId).toBe('tx-123');
    });
  });
  describe('authorizeAccess', () => {
    it('should authorize access successfully', async () => {
      const request: AuthorizeAccessRequest = {
      userId: "user-123",
      authorizedId: 'auth-456',
        dataTypes: ["blood_pressure",heart_rate'],
        expirationTime: 1701432000,
        accessPolicies: {
      read: "true",
      write: 'false' }
      };
      const mockResponse = {
      authorization_id: "auth-789",
      success: true,message: 'Access authorized successfully';
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      } as Response);
      const result = await client.authorizeAccess(request);
      expect(result.success).toBe(true);
      expect(result.authorizationId).toBe('auth-789');
    });
  });
  describe('revokeAccess', () => {
    it('should revoke access successfully', async () => {
      const request: RevokeAccessRequest = {
      authorizationId: "auth-789",
      userId: 'user-123',
        revocationReason: 'User request'
      };
      const mockResponse = {success: true,message: 'Access revoked successfully',revocation_timestamp: 1701432000;
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      } as Response);
      const result = await client.revokeAccess(request);
      expect(result.success).toBe(true);
      expect(result.message).toBe('Access revoked successfully');
    });
  });
  describe('getBlockchainStatus', () => {
    it('should get blockchain status successfully', async () => {
      const request: GetBlockchainStatusRequest = {
        includeNodeInfo: true
      };
      const mockResponse = {current_block_height: 12345,connected_nodes: 5,consensus_status: 'SYNCED',sync_percentage: 100,node_info: { version: '1.0.0' },last_block_timestamp: 1701432000;
      };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      } as Response);
      const result = await client.getBlockchainStatus(request);
      expect(result.currentBlockHeight).toBe(12345);
      expect(result.connectedNodes).toBe(5);
      expect(result.consensusStatus).toBe('SYNCED');
    });
  });
  describe('error handling', () => {
    it('should handle HTTP errors', async () => {
      const request: StoreHealthDataRequest = {
      userId: "user-123",
      dataType: 'blood_pressure',
        dataHash: new Uint8Array([1, 2, 3]),
        encryptedData: new Uint8Array([4, 5, 6]),
        metadata: { device: 'smartwatch' },
        timestamp: 1701432000
      };
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => ({ error: 'Invalid request' })
      } as Response);
      await expect(client.storeHealthData(request)).rejects.toThrow();
    });
    it('should handle timeout errors', async () => {
      const request: StoreHealthDataRequest = {
      userId: "user-123",
      dataType: 'blood_pressure',
        dataHash: new Uint8Array([1, 2, 3]),
        encryptedData: new Uint8Array([4, 5, 6]),
        metadata: { device: 'smartwatch' },
        timestamp: 1701432000
      };
      // Mock timeout
      mockFetch.mockImplementationOnce(() =>
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Timeout')), 100)
        )
      );
      await expect(client.storeHealthData(request)).rejects.toThrow('Timeout');
    });
  });
});