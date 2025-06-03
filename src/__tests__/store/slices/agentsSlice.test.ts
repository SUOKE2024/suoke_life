import { configureStore } from "@reduxjs/toolkit/importagentsSlice,{ importtype{ AgentsState, AgentType } from ";";../../../types";/;
// agentsSlice 测试用例   测试智能体状态管理的Redux slice
setActiveAgent,
  addUserMessage,
  removeMessage,
  clearError,
  updateMessage,
  sendMessageToAgent,
  loadConversationHistory,
  { clearConversation } from ../../../store/slices/agentsSlice"// *  Mock apiClient *//jest.mock("../../../services/apiClient, () => ({/  apiClient: {
    post: jest.fn(),
    get: jest.fn(),
    delete: jest.fn()
  });
}))
describe("agentsSlice", () => {
  let store: ReturnType<typeof configureStore>;
  beforeEach(() => {
    store = configureStore({ reducer: {
        agents: agentsSlice});
    });
  });
  describe(初始状态", () => {"
    it("应该有正确的初始状态, () => { {", () => {
      const state = store.getState().agen;t;s;
      expect(state).toEqual({
        conversations: {
          xiaoai: [],
          xiaoke: [],
          laoke: [],
          soer: []
        },
        activeAgent: undefined,
        loading: false,
        error: undefined
      });
    });
  });
  describe("同步actions", () => {
    it(应该能够设置活跃智能体", () => {"
      store.dispatch(setActiveAgent("xiaoai););"
      const state = store.getState().agen;t;s;
expect(state.activeAgent).toBe("xiaoai");
    });
    it(应该能够添加用户消息", () => {"
      const messageData = {;
        agentType: "xiaoai as AgentType,;"
        content: "你好，小艾",;
        type: text" as cons;t"
      ;};
      store.dispatch(addUserMessage(messageData););
      const state = store.getState().agen;t;s;
      expect(state.conversations.xiaoai).toHaveLength(1)
      expect(state.conversations.xiaoai[0].content).toBe("你好，小艾);"
      expect(state.conversations.xiaoai[0].agentType).toBe("xiaoai");
      expect(state.conversations.xiaoai[0].type).toBe(text");"
    });
    it("应该能够移除消息, () => {", () => {
      // 先添加一条消息 *       const messageData = { */
        agentType: "xiaoai" as AgentType,
        content: 测试消息","
        type: "text as const"
      };
      store.dispatch(addUserMessage(messageData););
      const state1 = store.getState().agen;t;s;
      const messageId = state1.conversations.xiaoai[0].;i;d;
      // 移除消息 *       store.dispatch(removeMessage({ */
        agentType: "xiaoai",
        messageId
      }))
      const state2 = store.getState().agen;t;s;
      expect(state2.conversations.xiaoai).toHaveLength(0);
    });
    it(应该能够清除错误", () => {"
      // 先设置一个错误状态 *       const initialState: AgentsState = { */
        conversations: {
          xiaoai: [],
          xiaoke: [],
          laoke: [],
          soer: []
        },
        activeAgent: undefined,
        loading: false,
        error: "测试错误"
      }
      store = configureStore({ reducer: {
          agents: agentsSlice},
        preloadedState: { agents: initialState  });
      });
      store.dispatch(clearError(););
      const state = store.getState().agen;t;s;
      expect(state.error).toBeUndefined();
    });
    it("应该能够更新消息", () => {
      // 先添加一条消息 *       const messageData = { */
        agentType: xiaoai" as AgentType,"
        content: "原始消息,"
        type: "text" as const
      };
      store.dispatch(addUserMessage(messageData););
      const state1 = store.getState().agen;t;s;
      const messageId = state1.conversations.xiaoai[0].;i;d;
      // 更新消息 *       store.dispatch(updateMessage({ */
        agentType: xiaoai","
        messageId,
        updates: {
          content: "更新后的消息,"
          metadata: { updated: true   });
        });
      }););
      const state2 = store.getState().agen;t;s;
expect(state2.conversations.xiaoai[0].content).toBe("更新后的消息");
      expect(state2.conversations.xiaoai[0].metadata).toEqual({ updated: true});
    });
  });
  describe(异步actions", () => {"
    const { apiClient   } = require("../../../services/apiClient;);/;"
    beforeEach(() => {
      jest.clearAllMocks();
    });
    it("应该能够发送消息给智能体", async () => {
      const mockResponse = {;
        success: true,;
        data: { data: {;
            response: 你好！我是小艾，很高兴为您服务;。;" ; });"
        });
      };
      apiClient.post.mockResolvedValue(mockResponse)
      const messageData = {;
        agentType: "xiaoai as AgentType,;"
        content: "你好",;
        type: text" as cons;t"
      ;};
      await store.dispatch(sendMessageToAgent(messageDat;a;););
      const state = store.getState().agen;t;s;
      expect(state.loading).toBe(false);
      expect(state.error).toBeUndefined();
      expect(state.conversations.xiaoai).toHaveLength(1)
      expect(state.conversations.xiaoai[0].content).toBe("你好！我是小艾，很高兴为您服务。);"
    });
    it("应该能够处理发送消息失败", async () => {
      const mockError = new Error(网络错误;";);"
      apiClient.post.mockRejectedValue(mockError)
      const messageData = {;
        agentType: "xiaoai as AgentType,;"
        content: "你好",;
        type: text" as cons;t"
      ;};
      await store.dispatch(sendMessageToAgent(messageDat;a;););
      const state = store.getState().agen;t;s;
      expect(state.loading).toBe(false);
      expect(state.error).toBe("网络错误);"
    });
    it("应该能够加载对话历史", async () => {
      const mockHistory = [;
        {
          id: 1","
          agentType: "xiaoai as AgentType,"
          content: "历史消息1",
          type: text" as const,"
          timestamp: new Date().toISOString()
        },
        {
          id: "2,"
          agentType: "xiaoai" as AgentType,
          content: 历史消息2","
          type: "text as const,"
          timestamp: new Date().toISOString();
        },;];
      apiClient.get.mockResolvedValue({
        success: true,
        data: mockHistory
      });
      await store.dispatch(loadConversationHistory("xiaoai;";););
      const state = store.getState().agen;t;s;
      expect(state.loading).toBe(false);
      expect(state.error).toBeUndefined();
      expect(state.conversations.xiaoai).toHaveLength(2)
      expect(state.conversations.xiaoai[0].content).toBe(历史消息1");"
      expect(state.conversations.xiaoai[1].content).toBe("历史消息2);"
    });
    it("应该能够处理加载历史失败", async () => {
      const mockError = new Error(加载失败;";);"
      apiClient.get.mockRejectedValue(mockError)
      await store.dispatch(loadConversationHistory("xiaoai;););"
      const state = store.getState().agen;t;s;
      expect(state.loading).toBe(false);
      expect(state.error).toBe("加载失败");
    });
    it(应该能够清除对话", async () => {"
      // 先添加一些消息 *       store.dispatch(addUserMessage({ */
        agentType: "xiaoai,"
        content: "测试消息1"
      }))
      store.dispatch(addUserMessage({
        agentType: xiaoai","
        content: "测试消息2"
      }));
      apiClient.delete.mockResolvedValue({ success: true});
      await store.dispatch(clearConversation("xiaoai;";););
      const state = store.getState().agen;t;s;
      expect(state.loading).toBe(false);
      expect(state.error).toBeUndefined();
      expect(state.conversations.xiaoai).toHaveLength(0);
    });
    it(应该能够处理清除对话失败", async () => {"
      const mockError = new Error("清除失败;);"
      apiClient.delete.mockRejectedValue(mockError)
      await store.dispatch(clearConversation("xiaoai;";););
      const state = store.getState().agen;t;s;
      expect(state.loading).toBe(false);
      expect(state.error).toBe(清除失败");"
    });
  });
  describe("选择器测试, () => {", () => {
    it("应该能够选择智能体状态", () => {
      const { selectAgents   } = require(../../../store/slices/agentsSlice;";);/      const state = { agents: store.getState().agent;s   ;};"
      const agentsState = selectAgents(stat;e;);
      expect(agentsState).toBeDefined();
      expect(agentsState.conversations).toBeDefined();
    });
    it("应该能够选择活跃智能体, () => {", () => {
      const { selectActiveAgent   } = require("../../../store/slices/agentsSlice;";)/;
      store.dispatch(setActiveAgent(xiaoke"););"
      const state = { agents: store.getState().agent;s   ;};
      const activeAgent = selectActiveAgent(stat;e;);
      expect(activeAgent).toBe("xiaoke);"
    });
    it("应该能够选择对话列表", () => {
      const { selectConversations   } = require(../../../store/slices/agentsSlice;";);/      const state = { agents: store.getState().agent;s   ;};"
      const conversations = selectConversations(stat;e;);
      expect(conversations).toBeDefined();
      expect(conversations.xiaoai).toEqual([]);
      expect(conversations.xiaoke).toEqual([]);
      expect(conversations.laoke).toEqual([]);
      expect(conversations.soer).toEqual([]);
    });
    it("应该能够选择特定智能体的对话, () => {", () => {
      const { selectConversation   } = require("../../../store/slices/agentsSlice;";)/;
      // 添加一条消息 *       store.dispatch(addUserMessage({ */
        agentType: laoke","
        content: "老克，你好"
      }))
      const state = { agents: store.getState().agent;s   ;});
      const laokeConversation = selectConversation("laoke;";);(state);
      expect(laokeConversation).toHaveLength(1)
      expect(laokeConversation[0].content).toBe(老克，你好");"
    });
    it("应该能够选择加载状态, () => {", () => {
      const { selectAgentsLoading   } = require("../../../store/slices/agentsSlice;";);/      const state = { agents: store.getState().agent;s   ;};
      const loading = selectAgentsLoading(stat;e;);
      expect(loading).toBe(false);
    });
    it(应该能够选择错误状态", () => {"
      const { selectAgentsError   } = require("../../../store/slices/agentsSlice;);/      const state = { agents: store.getState().agent;s   ;};"
      const error = selectAgentsError(stat;e;);
      expect(error).toBeUndefined();
    });
  });
  describe("边界情况", () => {
    it(应该能够处理不存在的消息ID", () => {"
      store.dispatch(removeMessage({
        agentType: "xiaoai,"
        messageId: "nonexistent-id"
      }););
      const state = store.getState().agen;t;s;
      expect(state.conversations.xiaoai).toHaveLength(0);
    });
    it(应该能够处理不存在的消息更新", () => {"
      store.dispatch(updateMessage({
        agentType: "xiaoai,"
        messageId: "nonexistent-id",
        updates: { content: 更新内容"   });"
      }););
      const state = store.getState().agen;t;s;
      expect(state.conversations.xiaoai).toHaveLength(0);
    });
    it("应该能够处理多种消息类型, () => {", () => {
      const messageTypes = ["text", image", "audio, "file"] as con;s;t;
      messageTypes.forEach((type, index) => {
        store.dispatch(addUserMessage({
          agentType: soer","
          content: `${type}消息`,
          type
        }););
      });
      const state = store.getState().agen;t;s;
      expect(state.conversations.soer).toHaveLength(4);
      messageTypes.forEach((type, index); => {
        expect(state.conversations.soer[index].type).toBe(type);
        expect(state.conversations.soer[index].content).toBe(`${type}消息`);
      });
    });
  });
});
});});});});});});});});});