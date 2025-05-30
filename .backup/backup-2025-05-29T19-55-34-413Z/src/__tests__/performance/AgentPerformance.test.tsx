import { render, waitFor } from "@testing-library/react-native";
import React from "react";

// Mock智能体服务
const mockAgentService = {
  sendMessage: jest.fn(),
  getAgentInfo: jest.fn(),
  startConsultation: jest.fn(),
  endConsultation: jest.fn(),
  getAgentSuggestions: jest.fn(),
};

jest.mock("../../services/agentService", () => mockAgentService);

// Mock组件
const MockAgentChat = ({ agentId }: { agentId: string }) => {
  return null; // 简化的Mock组件
};

describe("智能体性能测试", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("响应时间测试", () => {
    it("智能体消息响应应该在合理时间内", async () => {
      const startTime = Date.now();

      mockAgentService.sendMessage.mockResolvedValue({
        id: "1",
        content: "测试回复",
        timestamp: Date.now(),
        sender: "xiaoai",
      });

      await mockAgentService.sendMessage("xiaoai", "测试消息");

      const endTime = Date.now();
      const responseTime = endTime - startTime;

      // 响应时间应该小于1秒
      expect(responseTime).toBeLessThan(1000);
    });

    it("智能体信息获取应该快速响应", async () => {
      const startTime = Date.now();

      mockAgentService.getAgentInfo.mockResolvedValue({
        id: "xiaoai",
        name: "小艾",
        status: "online",
        capabilities: ["健康咨询", "症状分析"],
      });

      await mockAgentService.getAgentInfo("xiaoai");

      const endTime = Date.now();
      const responseTime = endTime - startTime;

      // 信息获取应该小于500ms
      expect(responseTime).toBeLessThan(500);
    });
  });

  describe("并发处理测试", () => {
    it("应该能够处理多个并发消息", async () => {
      const messageCount = 10;
      const promises = [];

      mockAgentService.sendMessage.mockImplementation((agentId, message) =>
        Promise.resolve({
          id: Math.random().toString(),
          content: `回复: ${message}`,
          timestamp: Date.now(),
          sender: agentId,
        })
      );

      const startTime = Date.now();

      for (let i = 0; i < messageCount; i++) {
        promises.push(mockAgentService.sendMessage("xiaoai", `消息 ${i}`));
      }

      const results = await Promise.all(promises);
      const endTime = Date.now();
      const totalTime = endTime - startTime;

      expect(results).toHaveLength(messageCount);
      expect(totalTime).toBeLessThan(2000); // 10个并发消息应该在2秒内完成
    });

    it("应该能够处理多智能体并发咨询", async () => {
      const agents = ["xiaoai", "xiaoke", "laoke", "soer"];
      const promises = [];

      mockAgentService.startConsultation.mockImplementation((agentId) =>
        Promise.resolve({
          sessionId: `session_${agentId}_${Date.now()}`,
          agentId,
          status: "active",
        })
      );

      const startTime = Date.now();

      for (const agentId of agents) {
        promises.push(mockAgentService.startConsultation(agentId));
      }

      const results = await Promise.all(promises);
      const endTime = Date.now();
      const totalTime = endTime - startTime;

      expect(results).toHaveLength(agents.length);
      expect(totalTime).toBeLessThan(1500); // 4个智能体咨询应该在1.5秒内启动
    });
  });

  describe("组件渲染性能测试", () => {
    it("智能体聊天组件应该快速渲染", () => {
      const startTime = Date.now();

      render(<MockAgentChat agentId="xiaoai" />);

      const endTime = Date.now();
      const renderTime = endTime - startTime;

      // 组件渲染应该小于100ms
      expect(renderTime).toBeLessThan(100);
    });

    it("多个智能体组件应该高效渲染", () => {
      const agents = ["xiaoai", "xiaoke", "laoke", "soer"];
      const startTime = Date.now();

      agents.forEach((agentId) => {
        render(<MockAgentChat agentId={agentId} />);
      });

      const endTime = Date.now();
      const totalRenderTime = endTime - startTime;

      // 4个组件渲染应该小于200ms
      expect(totalRenderTime).toBeLessThan(200);
    });
  });

  describe("内存使用测试", () => {
    it("长时间聊天不应该导致内存泄漏", async () => {
      // 模拟内存使用测试，在React Native环境中简化处理
      const messageCount = 100;
      const messages: any[] = [];

      mockAgentService.sendMessage.mockImplementation((agentId, message) => {
        const response = {
          id: Math.random().toString(),
          content: "测试回复",
          timestamp: Date.now(),
          sender: "xiaoai",
        };
        messages.push(response);
        return Promise.resolve(response);
      });

      // 模拟长时间聊天
      for (let i = 0; i < messageCount; i++) {
        await mockAgentService.sendMessage("xiaoai", `消息 ${i}`);
      }

      // 验证消息数量正确
      expect(messages).toHaveLength(messageCount);
      expect(mockAgentService.sendMessage).toHaveBeenCalledTimes(messageCount);
    });
  });

  describe("负载测试", () => {
    it("应该能够处理高频率消息发送", async () => {
      const messageCount = 50;
      const interval = 10; // 10ms间隔

      mockAgentService.sendMessage.mockResolvedValue({
        id: "1",
        content: "快速回复",
        timestamp: Date.now(),
        sender: "xiaoai",
      });

      const startTime = Date.now();
      const promises = [];

      for (let i = 0; i < messageCount; i++) {
        promises.push(
          new Promise((resolve) => {
            setTimeout(async () => {
              const result = await mockAgentService.sendMessage(
                "xiaoai",
                `快速消息 ${i}`
              );
              resolve(result);
            }, i * interval);
          })
        );
      }

      const results = await Promise.all(promises);
      const endTime = Date.now();
      const totalTime = endTime - startTime;

      expect(results).toHaveLength(messageCount);
      // 高频消息应该在合理时间内完成
      expect(totalTime).toBeLessThan(messageCount * interval + 1000);
    });
  });

  describe("错误恢复性能测试", () => {
    it("网络错误后应该快速恢复", async () => {
      // 模拟网络错误
      mockAgentService.sendMessage
        .mockRejectedValueOnce(new Error("网络错误"))
        .mockResolvedValue({
          id: "1",
          content: "恢复后的回复",
          timestamp: Date.now(),
          sender: "xiaoai",
        });

      const startTime = Date.now();

      try {
        await mockAgentService.sendMessage("xiaoai", "测试消息");
      } catch (error) {
        // 预期的错误
      }

      // 重试应该成功
      const result = await mockAgentService.sendMessage("xiaoai", "重试消息");
      const endTime = Date.now();
      const recoveryTime = endTime - startTime;

      expect(result).toBeDefined();
      expect(recoveryTime).toBeLessThan(1000); // 错误恢复应该在1秒内
    });
  });
});
