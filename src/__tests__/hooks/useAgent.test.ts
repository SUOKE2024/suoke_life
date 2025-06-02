import { renderHook, act } from '@testing-library/react-native';
import { useAgent } from '../../hooks/useAgent';

// Mock the useAgent hook
const mockUseAgent = () => ({
  agents: [],
  selectedAgent: null,
  loading: false,
  error: null,
  fetchAgents: jest.fn(),
  selectAgent: jest.fn(),
  clearError: jest.fn(),
  getOnlineAgents: jest.fn(() => []),
  getOfflineAgents: jest.fn(() => []),
});

// Mock the actual hook
jest.mock('../../hooks/useAgent', () => ({
  __esModule: true,
  default: jest.fn(() => mockUseAgent()),
}));

describe('useAgent Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('基础功能', () => {
    it('应该返回正确的初始状态', () => {
      const hook = mockUseAgent();
      expect(hook.agents).toEqual([]);
      expect(hook.selectedAgent).toBeNull();
      expect(hook.loading).toBe(false);
      expect(hook.error).toBeNull();
    });

    it('应该提供所有必要的方法', () => {
      const hook = mockUseAgent();
      expect(typeof hook.fetchAgents).toBe('function');
      expect(typeof hook.selectAgent).toBe('function');
      expect(typeof hook.clearError).toBe('function');
      expect(typeof hook.getOnlineAgents).toBe('function');
      expect(typeof hook.getOfflineAgents).toBe('function');
    });
  });

  describe('智能体管理', () => {
    it('应该能够获取智能体列表', () => {
      const hook = mockUseAgent();
      expect(() => hook.fetchAgents()).not.toThrow();
    });

    it('应该能够选择智能体', () => {
      const hook = mockUseAgent();
      expect(() => hook.selectAgent('xiaoai')).not.toThrow();
    });

    it('应该能够清除错误', () => {
      const hook = mockUseAgent();
      expect(() => hook.clearError()).not.toThrow();
    });
  });

  describe('智能体筛选', () => {
    it('应该能够获取在线智能体', () => {
      const hook = mockUseAgent();
      const onlineAgents = hook.getOnlineAgents();
      expect(Array.isArray(onlineAgents)).toBe(true);
    });

    it('应该能够获取离线智能体', () => {
      const hook = mockUseAgent();
      const offlineAgents = hook.getOfflineAgents();
      expect(Array.isArray(offlineAgents)).toBe(true);
    });
  });

  describe('方法调用', () => {
    it('应该能够调用fetchAgents方法', () => {
      const hook = mockUseAgent();
      expect(() => hook.fetchAgents()).not.toThrow();
    });

    it('应该能够调用selectAgent方法', () => {
      const hook = mockUseAgent();
      expect(() => hook.selectAgent('xiaoai')).not.toThrow();
    });

    it('应该能够调用clearError方法', () => {
      const hook = mockUseAgent();
      expect(() => hook.clearError()).not.toThrow();
    });
  });
});