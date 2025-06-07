import { renderHook, act } from '@testing-library/react-native';
import { getBlockchainServiceClient } from '../../services/blockchain/BlockchainServiceClient';
// Mock the entire BlockchainServiceClient module
jest.mock('../../services/blockchain/BlockchainServiceClient', () => {
  const mockClient = {storeHealthData: jest.fn(),verifyHealthData: jest.fn(),verifyWithZKP: jest.fn(),getHealthDataRecords: jest.fn(),authorizeAccess: jest.fn(),revokeAccess: jest.fn(),getBlockchainStatus: jest.fn(),generateZKProof: jest.fn(),getAccessGrants: jest.fn(),getNetworkStats: jest.fn(),batchStoreHealthData: jest.fn();
  };
  return {getBlockchainServiceClient: () => mockClient,createBlockchainServiceClient: () => mockClient,BlockchainServiceClient: jest.fn().mockImplementation(() => mockClient);
  };
});
// Import after mocking
describe('useBlockchainService', () => {
  let mockClient: any;
  beforeEach(() => {
    mockClient = getBlockchainServiceClient();
    jest.clearAllMocks();
  });
  describe('initialization', () => {
    it('should initialize with default state', () => {
      const { result } = renderHook(() => useBlockchainService());
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.blockchainStatus).toBeNull();
      expect(result.current.healthDataRecords).toEqual([]);
      expect(result.current.accessGrants).toEqual([]);
      expect(result.current.lastOperation).toBeNull();
    });
  });
  describe('storeHealthData', () => {
    it('should store health data successfully', async () => {
      const mockResponse = {
      transactionId: "tx-123",
      blockHash: '0xblock123',success: true,message: 'Data stored successfully';
      };
      mockClient.storeHealthData.mockResolvedValueOnce(mockResponse);
      const { result } = renderHook(() => useBlockchainService());
      await act(async () => {
        const response = await result.current.storeHealthData({
      userId: "user-123",
      dataType: 'blood_pressure',dataHash: new Uint8Array([1, 2, 3]),encryptedData: new Uint8Array([4, 5, 6]),metadata: { device: 'smartwatch' },timestamp: 1701432000;
        });
        expect(response).toEqual(mockResponse);
      });
      expect(mockClient.storeHealthData).toHaveBeenCalledWith({
      userId: "user-123",
      dataType: 'blood_pressure',
        dataHash: new Uint8Array([1, 2, 3]),
        encryptedData: new Uint8Array([4, 5, 6]),
        metadata: { device: 'smartwatch' },
        timestamp: 1701432000
      });
    });
    it('should handle errors when storing health data', async () => {
      const error = new Error('Storage failed');
      mockClient.storeHealthData.mockRejectedValueOnce(error);
      const { result } = renderHook(() => useBlockchainService());
      await act(async () => {
        try {
          await result.current.storeHealthData({
      userId: "user-123",
      dataType: 'blood_pressure',
            dataHash: new Uint8Array([1, 2, 3]),
            encryptedData: new Uint8Array([4, 5, 6]),
            metadata: { device: 'smartwatch' },
            timestamp: 1701432000
          });
        } catch (e) {
          expect(e).toBeDefined();
        }
      });
      expect(result.current.error).toBeDefined();
    });
  });
  describe('basic functionality', () => {
    it('should verify health data successfully', async () => {
      const mockResponse = {valid: true,message: 'Data verified successfully',verificationTimestamp: 1701432000;
      };
      mockClient.verifyHealthData.mockResolvedValueOnce(mockResponse);
      const { result } = renderHook(() => useBlockchainService());
      await act(async () => {
        const response = await result.current.verifyHealthData({
      transactionId: "tx-123",
      dataHash: new Uint8Array([1, 2, 3]);
        });
        expect(response).toEqual(mockResponse);
      });
    });
    it('should handle loading states', () => {
      const { result } = renderHook(() => useBlockchainService());
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });
    it('should clear errors when clearError is called', () => {
      const { result } = renderHook(() => useBlockchainService());
      act(() => {
        result.current.clearError();
      });
      expect(result.current.error).toBeNull();
    });
    it('should get blockchain status successfully', async () => {
      const mockResponse = {currentBlockHeight: 12345,connectedNodes: 5,consensusStatus: 'SYNCED',syncPercentage: 100,nodeInfo: { version: '1.0.0' },lastBlockTimestamp: 1701432000;
      };
      mockClient.getBlockchainStatus.mockResolvedValueOnce(mockResponse);
      const { result } = renderHook(() => useBlockchainService());
      await act(async () => {
        const response = await result.current.getBlockchainStatus({includeNodeInfo: true;
        });
        expect(response).toEqual(mockResponse);
      });
      expect(result.current.blockchainStatus).toEqual({
        isConnected: true,
        currentBlockHeight: 12345,
        networkId: 'suoke-network',
        consensusStatus: 'SYNCED',
        syncPercentage: 100,
        lastBlockTimestamp: 1701432000,
        nodeCount: 5,
        transactionPoolSize: 0
      });
    });
  });
});
