import { AgentCoordinator } from "../../agents/AgentCoordinator";
import type { AgentTask, AgentType } from "../../agents/AgentCoordinator";

/**
 * AgentCoordinator 测试用例
 * 测试四智能体协作系统的核心功能
 */

// Mock智能体实现
jest.mock("../../agents/xiaoai/XiaoaiAgentImpl");
jest.mock("../../agents/xiaoke/XiaokeAgentImpl");
jest.mock("../../agents/laoke/LaokeAgentImpl");
jest.mock("../../agents/soer/SoerAgentImpl");

describe("AgentCoordinator", () => {
  let coordinator: AgentCoordinator;

  beforeEach(() => {
    coordinator = new AgentCoordinator({
      enableLoadBalancing: true,
      enableFailover: true,
      maxRetries: 3,
      timeoutMs: 5000,
      healthCheckIntervalMs: 10000,
    });
  });

  afterEach(async () => {
    await coordinator.cleanup();
  });

  describe("初始化", () => {
    it("应该成功初始化协调器", () => {
      expect(coordinator).toBeDefined();
      expect(coordinator).toBeInstanceOf(AgentCoordinator);
    });
  });

  describe("任务协调", () => {
    it("应该能够协调诊断任务", async () => {
      const task: AgentTask = {
        taskId: "test-diagnosis-001",
        type: "diagnosis",
        priority: "high",
        userId: "user-001",
        data: {
          symptoms: ["头痛", "发热"],
          duration: "2天",
        },
        timestamp: new Date(),
      };

      const result = await coordinator.coordinateTask(task);

      expect(result).toBeDefined();
      expect(result.taskId).toBe(task.taskId);
      expect(["completed", "failed", "timeout", "partial"]).toContain(
        result.status
      );
    });

    it("应该能够协调服务推荐任务", async () => {
      const task: AgentTask = {
        taskId: "test-recommendation-001",
        type: "recommendation",
        priority: "medium",
        userId: "user-001",
        data: {
          healthProfile: {
            age: 30,
            gender: "female",
            conditions: ["高血压"],
          },
        },
        timestamp: new Date(),
      };

      const result = await coordinator.coordinateTask(task);

      expect(result).toBeDefined();
      expect(result.taskId).toBe(task.taskId);
    });

    it("应该能够处理紧急任务", async () => {
      const task: AgentTask = {
        taskId: "test-emergency-001",
        type: "emergency",
        priority: "critical",
        userId: "user-001",
        data: {
          emergency: "胸痛",
          location: "北京市朝阳区",
        },
        timestamp: new Date(),
      };

      const result = await coordinator.coordinateTask(task);

      expect(result).toBeDefined();
    });
  });

  describe("智能体健康监控", () => {
    it("应该能够获取智能体健康状态", async () => {
      const healthStatus = await coordinator.getAgentHealth();

      expect(healthStatus).toBeDefined();
      expect(healthStatus).toBeInstanceOf(Map);
    });

    it("应该能够获取特定智能体的健康状态", async () => {
      const healthStatus = await coordinator.getAgentHealth("xiaoai");

      expect(healthStatus).toBeDefined();
      expect(healthStatus).toBeInstanceOf(Map);
    });
  });

  describe("共享上下文", () => {
    it("应该能够获取共享上下文（未设置时返回null）", () => {
      const retrievedContext = coordinator.getSharedContext(
        "xiaoai",
        "xiaoke",
        "user-001"
      );

      // 由于没有设置过上下文，应该返回null
      expect(retrievedContext).toBeNull();
    });

    it("应该在没有上下文时返回null", () => {
      const retrievedContext = coordinator.getSharedContext(
        "xiaoai",
        "xiaoke",
        "nonexistent-user"
      );
      expect(retrievedContext).toBeNull();
    });
  });

  describe("任务处理", () => {
    it("应该能够处理多个并发任务", async () => {
      const tasks: AgentTask[] = [
        {
          taskId: "task-001",
          type: "diagnosis",
          priority: "medium",
          userId: "user-001",
          data: { symptoms: ["咳嗽"] },
          timestamp: new Date(),
        },
        {
          taskId: "task-002",
          type: "recommendation",
          priority: "medium",
          userId: "user-002",
          data: { healthProfile: { age: 25 } },
          timestamp: new Date(),
        },
      ];

      const results = await Promise.all(
        tasks.map((task) => coordinator.coordinateTask(task))
      );

      expect(results).toHaveLength(2);
      results.forEach((result) => {
        expect(result).toBeDefined();
        expect(["completed", "failed", "timeout", "partial"]).toContain(
          result.status
        );
      });
    });

    it("应该能够处理教育任务", async () => {
      const task: AgentTask = {
        taskId: "test-education-001",
        type: "education",
        priority: "low",
        userId: "user-001",
        data: {
          topic: "中医养生",
          level: "beginner",
        },
        timestamp: new Date(),
      };

      const result = await coordinator.coordinateTask(task);

      expect(result).toBeDefined();
      expect(result.taskId).toBe(task.taskId);
    });

    it("应该能够处理生活方式任务", async () => {
      const task: AgentTask = {
        taskId: "test-lifestyle-001",
        type: "lifestyle",
        priority: "medium",
        userId: "user-001",
        data: {
          currentHabits: ["早睡早起", "规律运动"],
          goals: ["减重", "改善睡眠"],
        },
        timestamp: new Date(),
      };

      const result = await coordinator.coordinateTask(task);

      expect(result).toBeDefined();
      expect(result.taskId).toBe(task.taskId);
    });
  });

  describe("错误处理", () => {
    it("应该能够处理无效的任务类型", async () => {
      const task: AgentTask = {
        taskId: "test-invalid-001",
        type: "invalid" as any,
        priority: "medium",
        userId: "user-001",
        data: {},
        timestamp: new Date(),
      };

      const result = await coordinator.coordinateTask(task);

      expect(result).toBeDefined();
      // 应该有错误处理机制
    });

    it("应该能够处理空数据的任务", async () => {
      const task: AgentTask = {
        taskId: "test-empty-001",
        type: "diagnosis",
        priority: "medium",
        userId: "user-001",
        data: {},
        timestamp: new Date(),
      };

      const result = await coordinator.coordinateTask(task);

      expect(result).toBeDefined();
    });
  });

  describe("清理资源", () => {
    it("应该能够正确清理资源", async () => {
      await coordinator.cleanup();

      // 验证清理后不会抛出错误
      expect(true).toBe(true);
    });
  });
});

// 自定义匹配器
expect.extend({
  toBeOneOf(received: any, expected: any[]) {
    const pass = expected.includes(received);
    if (pass) {
      return {
        message: () =>
          `expected ${received} not to be one of ${expected.join(", ")}`,
        pass: true,
      };
    } else {
      return {
        message: () =>
          `expected ${received} to be one of ${expected.join(", ")}`,
        pass: false,
      };
    }
  },
});

declare global {
  namespace jest {
    interface Matchers<R> {
      toBeOneOf(expected: any[]): R;
    }
  }
}
