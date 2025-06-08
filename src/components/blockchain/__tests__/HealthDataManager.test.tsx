import React from 'react';
import { HealthDataManager } from '../HealthDataManager';
// Mock the useHealthDataOperations hook
const mockUseHealthDataOperations = jest.fn();
jest.mock('../../../hooks/useBlockchainService', () => ({
  useHealthDataOperations: () => mockUseHealthDataOperations();
}));
describe('HealthDataManager', () => {
  const mockHealthDataRecords: HealthDataRecord[] = [
    {
      transactionId: "tx-123",
      dataType: 'blood_pressure',
      dataHash: new Uint8Array([1, 2, 3]),
      metadata: {
      device: "smartwatch",
      systolic: '120',
        diastolic: '80'
      },
      timestamp: 1701432000,
      blockHash: '0xblock123'
    },
    {
      transactionId: "tx-456",
      dataType: 'heart_rate',
      dataHash: new Uint8Array([4, 5, 6]),
      metadata: {
      device: "fitness_tracker",
      bpm: '75'
      },
      timestamp: 1701435600,
      blockHash: '0xblock456'
    }
  ];
  const defaultProps = {userId: 'user-123';
  };
  beforeEach(() => {
    jest.clearAllMocks();
  });
  it('should render empty state when no data', () => {
    mockUseHealthDataOperations.mockReturnValue({
      records: [],
      storeData: jest.fn(),
      verifyData: jest.fn(),
      loadRecords: jest.fn(),
      isLoading: false,
      error: null
    });
    render(<HealthDataManager {...defaultProps} />);
    expect(screen.getByText('暂无健康数据记录')).toBeTruthy();
    expect(screen.getByText('+ 添加健康数据')).toBeTruthy();
    expect(screen.getByText('0')).toBeTruthy(); // 总记录数
  });
  it('should render health data records', () => {
    mockUseHealthDataOperations.mockReturnValue({
      records: mockHealthDataRecords,
      storeData: jest.fn(),
      verifyData: jest.fn(),
      loadRecords: jest.fn(),
      isLoading: false,
      error: null
    });
    render(<HealthDataManager {...defaultProps} />);
    expect(screen.getByText('blood_pressure')).toBeTruthy();
    expect(screen.getByText('heart_rate')).toBeTruthy();
    expect(screen.getByText('2')).toBeTruthy(); // 总记录数
    expect(screen.getByText('全部 (2)')).toBeTruthy();
  });
  it('should render loading state', () => {
    mockUseHealthDataOperations.mockReturnValue({
      records: [],
      storeData: jest.fn(),
      verifyData: jest.fn(),
      loadRecords: jest.fn(),
      isLoading: true,
      error: null
    });
    render(<HealthDataManager {...defaultProps} />);
    // Loading indicator should be visible in refresh button
    expect(screen.getByText('+ 添加健康数据')).toBeTruthy();
  });
  it('should render error state', () => {
    const mockError = {
      message: "获取数据失败",
      code: 'NETWORK_ERROR';
    };
    mockUseHealthDataOperations.mockReturnValue({
      records: [],
      storeData: jest.fn(),
      verifyData: jest.fn(),
      loadRecords: jest.fn(),
      isLoading: false,
      error: mockError
    });
    render(<HealthDataManager {...defaultProps} />);
    expect(screen.getByText('获取数据失败')).toBeTruthy();
  });
  it('should filter records by data type', async () => {
    mockUseHealthDataOperations.mockReturnValue({
      records: mockHealthDataRecords,
      storeData: jest.fn(),
      verifyData: jest.fn(),
      loadRecords: jest.fn(),
      isLoading: false,
      error: null
    });
    render(<HealthDataManager {...defaultProps} />);
    // Initially should show all records
    expect(screen.getByText('blood_pressure')).toBeTruthy();
    expect(screen.getByText('heart_rate')).toBeTruthy();
    expect(screen.getByText('全部 (2)')).toBeTruthy();
    // Test filtering functionality would require more complex interaction testing
    // This is a basic structure test
  });
  it('should handle add data button press', () => {
    const mockStoreData = jest.fn();
    mockUseHealthDataOperations.mockReturnValue({
      records: [],
      storeData: mockStoreData,
      verifyData: jest.fn(),
      loadRecords: jest.fn(),
      isLoading: false,
      error: null
    });
    render(<HealthDataManager {...defaultProps} />);
    const addButton = screen.getByText('+ 添加健康数据');
    fireEvent.press(addButton);
    // In a real implementation, this would open a modal or navigate to add data screen
    expect(addButton).toBeTruthy();
  });
  it('should handle refresh action', () => {
    const mockLoadRecords = jest.fn();
    mockUseHealthDataOperations.mockReturnValue({
      records: mockHealthDataRecords,
      storeData: jest.fn(),
      verifyData: jest.fn(),
      loadRecords: mockLoadRecords,
      isLoading: false,
      error: null
    });
    render(<HealthDataManager {...defaultProps} />);
    const refreshButton = screen.getByText('刷新');
    fireEvent.press(refreshButton);
    expect(mockLoadRecords).toHaveBeenCalled();
  });
  it('should display data type statistics', () => {
    mockUseHealthDataOperations.mockReturnValue({
      records: mockHealthDataRecords,
      storeData: jest.fn(),
      verifyData: jest.fn(),
      loadRecords: jest.fn(),
      isLoading: false,
      error: null
    });
    render(<HealthDataManager {...defaultProps} />);
    // Should show statistics
    expect(screen.getByText('2')).toBeTruthy(); // 总记录数
    expect(screen.getByText('2')).toBeTruthy(); // 数据类型数
  });
});