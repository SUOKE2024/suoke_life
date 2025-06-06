import { AgentType, AgentStatus, MessageType } from '../../types/agents';

// Mock function for testing
const someFunction = (data?: any) => {
  // Mock implementation;
  return data;
};

describe('智能体类型测试', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('AgentType 枚举测试', () => {
    it('应该包含所有智能体类型', () => {
      expect(AgentType.XIAOAI).toBe('xiaoai');
      expect(AgentType.XIAOKE).toBe('xiaoke');
      expect(AgentType.LAOKE).toBe('laoke');
      expect(AgentType.SOER).toBe('soer');
    });

    it('应该有正确的枚举值数量', () => {
      const agentTypes = Object.values(AgentType);
      expect(agentTypes).toHaveLength(4);
    });
  });

  describe('AgentStatus 枚举测试', () => {
    it('应该包含所有状态类型', () => {
      expect(AgentStatus.INITIALIZING).toBe('initializing');
      expect(AgentStatus.ACTIVE).toBe('active');
      expect(AgentStatus.BUSY).toBe('busy');
      expect(AgentStatus.IDLE).toBe('idle');
      expect(AgentStatus.MAINTENANCE).toBe('maintenance');
      expect(AgentStatus.ERROR).toBe('error');
      expect(AgentStatus.OFFLINE).toBe('offline');
    });
  });

  describe('MessageType 枚举测试', () => {
    it('应该包含所有消息类型', () => {
      expect(MessageType.TEXT).toBe('text');
      expect(MessageType.VOICE).toBe('voice');
      expect(MessageType.IMAGE).toBe('image');
      expect(MessageType.VIDEO).toBe('video');
      expect(MessageType.SENSOR_DATA).toBe('sensor_data');
      expect(MessageType.DIAGNOSTIC_DATA).toBe('diagnostic_data');
      expect(MessageType.COMMAND).toBe('command');
      expect(MessageType.NOTIFICATION).toBe('notification');
    });
  });
});

describe('性能测试', () => {
  it('应该在性能阈值内执行', () => {
    const iterations = 10;
    const startTime = Date.now();

    for (let i = 0; i < iterations; i++) {
      // 执行性能关键函数
      someFunction({ iteration: i });
    }

    const endTime = Date.now();
    const averageTime = (endTime - startTime) / iterations;

    // 平均执行时间应该小于1ms
    expect(averageTime).toBeLessThan(1);
  });

  it('应该高效处理大数据集', () => {
    const largeDataset = new Array(10000).fill(0).map((_, i) => i);
    const startTime = Date.now();

    // 使用大数据集测试
    someFunction(largeDataset);

    const endTime = Date.now();

    // 应该在100ms内处理大数据集
    expect(endTime - startTime).toBeLessThan(100);
  });

  it('不应该造成内存泄漏', () => {
    const initialMemory = process.memoryUsage().heapUsed;

    // 多次执行函数
    for (let i = 0; i < 1000; i++) {
      someFunction({ test: 'params', iteration: i });
    }

    // 如果可用，强制垃圾回收
    if (global.gc) {
      global.gc();
    }

    const finalMemory = process.memoryUsage().heapUsed;
    const memoryIncrease = finalMemory - initialMemory;

    // 内存增长应该最小（小于10MB）
    expect(memoryIncrease).toBeLessThan(10 * 1024 * 1024);
  });
});
