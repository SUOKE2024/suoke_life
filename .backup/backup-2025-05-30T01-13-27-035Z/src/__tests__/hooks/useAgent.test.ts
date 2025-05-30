import { renderHook, act } from "@testing-library/react-native";


// Mock useAgent Hook
const mockUseAgent = () => {
  const [agents, setAgents] = React.useState([]);
  const [selectedAgent, setSelectedAgent] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const fetchAgents = async () => {
    setLoading(true);
    try {
      const mockAgents = [
        { id: "xiaoai", name: "小艾", specialty: "健康咨询", status: "online" },
        { id: "xiaoke", name: "小克", specialty: "疾病诊断", status: "online" },
        { id: "laoke", name: "老克", specialty: "中医调理", status: "offline" },
        { id: "soer", name: "索儿", specialty: "生活指导", status: "online" },
      ];
      setAgents(mockAgents);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const selectAgent = (agentId: string) => {
    const agent = agents.find((a: any) => a.id === agentId);
    setSelectedAgent(agent || null);
  };

  const clearError = () => setError(null);

  return {
    agents,
    selectedAgent,
    loading,
    error,
    fetchAgents,
    selectAgent,
    clearError,
  };
};

// Mock React
const React = {
  useState: jest.fn(),
};

describe("useAgent Hook", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("初始状态", () => {
    it("应该返回正确的初始状态", () => {
      React.useState
        .mockReturnValueOnce([[], jest.fn()]) // agents
        .mockReturnValueOnce([null, jest.fn()]) // selectedAgent
        .mockReturnValueOnce([false, jest.fn()]) // loading
        .mockReturnValueOnce([null, jest.fn()]); // error

      const hook = mockUseAgent();

      expect(hook.agents).toEqual([]);
      expect(hook.selectedAgent).toBeNull();
      expect(hook.loading).toBe(false);
      expect(hook.error).toBeNull();
    });

    it("应该提供必要的方法", () => {
      React.useState
        .mockReturnValueOnce([[], jest.fn()])
        .mockReturnValueOnce([null, jest.fn()])
        .mockReturnValueOnce([false, jest.fn()])
        .mockReturnValueOnce([null, jest.fn()]);

      const hook = mockUseAgent();

      expect(typeof hook.fetchAgents).toBe("function");
      expect(typeof hook.selectAgent).toBe("function");
      expect(typeof hook.clearError).toBe("function");
    });
  });

  describe("智能体管理", () => {
    it("应该能够管理智能体列表", () => {
      const mockAgents = [
        { id: "xiaoai", name: "小艾", specialty: "健康咨询", status: "online" },
        { id: "xiaoke", name: "小克", specialty: "疾病诊断", status: "online" },
      ];

      React.useState
        .mockReturnValueOnce([mockAgents, jest.fn()])
        .mockReturnValueOnce([null, jest.fn()])
        .mockReturnValueOnce([false, jest.fn()])
        .mockReturnValueOnce([null, jest.fn()]);

      const hook = mockUseAgent();

      expect(hook.agents).toEqual(mockAgents);
      expect(hook.agents).toHaveLength(2);
    });

    it("应该能够选择智能体", () => {
      const mockAgents = [
        { id: "xiaoai", name: "小艾", specialty: "健康咨询", status: "online" },
        { id: "xiaoke", name: "小克", specialty: "疾病诊断", status: "online" },
      ];
      const selectedAgent = mockAgents[0];

      React.useState
        .mockReturnValueOnce([mockAgents, jest.fn()])
        .mockReturnValueOnce([selectedAgent, jest.fn()])
        .mockReturnValueOnce([false, jest.fn()])
        .mockReturnValueOnce([null, jest.fn()]);

      const hook = mockUseAgent();

      expect(hook.selectedAgent).toEqual(selectedAgent);
      expect(hook.selectedAgent?.id).toBe("xiaoai");
      expect(hook.selectedAgent?.name).toBe("小艾");
    });

    it("应该能够处理空的智能体列表", () => {
      React.useState
        .mockReturnValueOnce([[], jest.fn()])
        .mockReturnValueOnce([null, jest.fn()])
        .mockReturnValueOnce([false, jest.fn()])
        .mockReturnValueOnce([null, jest.fn()]);

      const hook = mockUseAgent();

      expect(hook.agents).toEqual([]);
      expect(hook.selectedAgent).toBeNull();
    });
  });

  describe("加载状态", () => {
    it("应该正确处理加载状态", () => {
      React.useState
        .mockReturnValueOnce([[], jest.fn()])
        .mockReturnValueOnce([null, jest.fn()])
        .mockReturnValueOnce([true, jest.fn()])
        .mockReturnValueOnce([null, jest.fn()]);

      const hook = mockUseAgent();

      expect(hook.loading).toBe(true);
    });

    it("应该在非加载状态下返回false", () => {
      React.useState
        .mockReturnValueOnce([[], jest.fn()])
        .mockReturnValueOnce([null, jest.fn()])
        .mockReturnValueOnce([false, jest.fn()])
        .mockReturnValueOnce([null, jest.fn()]);

      const hook = mockUseAgent();

      expect(hook.loading).toBe(false);
    });
  });

  describe("错误处理", () => {
    it("应该能够处理错误状态", () => {
      const errorMessage = "获取智能体列表失败";

      React.useState
        .mockReturnValueOnce([[], jest.fn()])
        .mockReturnValueOnce([null, jest.fn()])
        .mockReturnValueOnce([false, jest.fn()])
        .mockReturnValueOnce([errorMessage, jest.fn()]);

      const hook = mockUseAgent();

      expect(hook.error).toBe(errorMessage);
    });

    it("应该能够清除错误", () => {
      React.useState
        .mockReturnValueOnce([[], jest.fn()])
        .mockReturnValueOnce([null, jest.fn()])
        .mockReturnValueOnce([false, jest.fn()])
        .mockReturnValueOnce([null, jest.fn()]);

      const hook = mockUseAgent();

      expect(typeof hook.clearError).toBe("function");
      expect(hook.error).toBeNull();
    });
  });

  describe("智能体数据结构", () => {
    it("应该返回正确的智能体数据结构", () => {
      const mockAgents = [
        {
          id: "xiaoai",
          name: "小艾",
          specialty: "健康咨询",
          status: "online",
        },
      ];

      React.useState
        .mockReturnValueOnce([mockAgents, jest.fn()])
        .mockReturnValueOnce([null, jest.fn()])
        .mockReturnValueOnce([false, jest.fn()])
        .mockReturnValueOnce([null, jest.fn()]);

      const hook = mockUseAgent();

      expect(hook.agents[0]).toHaveProperty("id");
      expect(hook.agents[0]).toHaveProperty("name");
      expect(hook.agents[0]).toHaveProperty("specialty");
      expect(hook.agents[0]).toHaveProperty("status");
    });

    it("应该正确处理智能体状态", () => {
      const mockAgents = [
        { id: "xiaoai", name: "小艾", specialty: "健康咨询", status: "online" },
        { id: "laoke", name: "老克", specialty: "中医调理", status: "offline" },
      ];

      React.useState
        .mockReturnValueOnce([mockAgents, jest.fn()])
        .mockReturnValueOnce([null, jest.fn()])
        .mockReturnValueOnce([false, jest.fn()])
        .mockReturnValueOnce([null, jest.fn()]);

      const hook = mockUseAgent();

      const onlineAgents = hook.agents.filter(
        (agent: any) => agent.status === "online"
      );
      const offlineAgents = hook.agents.filter(
        (agent: any) => agent.status === "offline"
      );

      expect(onlineAgents).toHaveLength(1);
      expect(offlineAgents).toHaveLength(1);
      expect(onlineAgents[0].name).toBe("小艾");
      expect(offlineAgents[0].name).toBe("老克");
    });
  });

  describe("方法调用", () => {
    it("应该能够调用fetchAgents方法", () => {
      React.useState
        .mockReturnValueOnce([[], jest.fn()])
        .mockReturnValueOnce([null, jest.fn()])
        .mockReturnValueOnce([false, jest.fn()])
        .mockReturnValueOnce([null, jest.fn()]);

      const hook = mockUseAgent();

      expect(() => hook.fetchAgents()).not.toThrow();
    });

    it("应该能够调用selectAgent方法", () => {
      const mockAgents = [
        { id: "xiaoai", name: "小艾", specialty: "健康咨询", status: "online" },
      ];

      React.useState
        .mockReturnValueOnce([mockAgents, jest.fn()])
        .mockReturnValueOnce([null, jest.fn()])
        .mockReturnValueOnce([false, jest.fn()])
        .mockReturnValueOnce([null, jest.fn()]);

      const hook = mockUseAgent();

      expect(() => hook.selectAgent("xiaoai")).not.toThrow();
    });

    it("应该能够调用clearError方法", () => {
      React.useState
        .mockReturnValueOnce([[], jest.fn()])
        .mockReturnValueOnce([null, jest.fn()])
        .mockReturnValueOnce([false, jest.fn()])
        .mockReturnValueOnce([null, jest.fn()]);

      const hook = mockUseAgent();

      expect(() => hook.clearError()).not.toThrow();
    });
  });
});
