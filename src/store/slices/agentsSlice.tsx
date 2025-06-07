import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { apiClient } from "../../services/apiClient";
import {AgentsState,
  AgentMessage,
  AgentType,
  AgentResponse;
} from "../../types";
// 使用apiClient的ApiResponse类型
interface ApiClientResponse<T = any> {
  success: boolean,
  data: T;
  message?: string;
  code?: string;
  timestamp?: string;
}
// 初始状态
const initialState: AgentsState = {,
  conversations: {
    xiaoai: [],
    xiaoke: [],
    laoke: [],
    soer: []
  },
  activeAgent: undefined,
  loading: false,
  error: undefined;
};
// 异步thunk actions;
export const sendMessageToAgent = createAsyncThunk<;
  AgentMessage,
  {
    agentType: AgentType,
  content: string;
    type?: "text" | "image" | "audio" | "file";
  },
  { rejectValue: string }
>(
  "agents/sendMessage",
  async ({ agentType, content, type = "text" }, { rejectWithValue }) => {
    try {
      // 使用apiClient发送消息到智能体
      const agentEndpoint = `/agents/${agentType}/chat`;
      const response: ApiClientResponse<AgentResponse> = await apiClient.post(
        agentEndpoint,
        {
          message: content,
          type;
        }
      );
      if (!response.success) {
        throw new Error(response.message || "发送消息失败");
      }
      // 构造返回的消息
      const agentMessage: AgentMessage = {,
  id: Date.now().toString(),
        agentType,
        content: response.data?.data?.response || "抱歉，我现在无法回复。",
        type: "text",
        timestamp: new Date().toISOString(),
        metadata: response.data?.data;
      };
      return agentMessage;
    } catch (error: any) {
      return rejectWithValue(error.message || "发送消息失败");
    }
  }
);
export const loadConversationHistory = createAsyncThunk<;
  { agentType: AgentType; messages: AgentMessage[] },
  AgentType,
  { rejectValue: string }
>("agents/loadHistory", async (agentType, { rejectWithValue }) => {
  try {
    const response: ApiClientResponse<AgentMessage[]> = await apiClient.get(
      `/agents/${agentType}/history`
    );
    if (!response.success) {
      throw new Error(response.message || "加载对话历史失败");
    }
    return {agentType,messages: response.data || [];
    };
  } catch (error: any) {
    return rejectWithValue(error.message || "加载对话历史失败");
  }
});
export const clearConversation = createAsyncThunk<;
  AgentType,
  AgentType,
  { rejectValue: string }
>("agents/clearConversation", async (agentType, { rejectWithValue }) => {
  try {
    const response: ApiClientResponse = await apiClient.delete(
      `/agents/${agentType}/history`
    );
    if (!response.success) {
      throw new Error(response.message || "清除对话历史失败");
    }
    return agentType;
  } catch (error: any) {
    return rejectWithValue(error.message || "清除对话历史失败");
  }
});
// 创建slice;
const agentsSlice = createSlice({name: "agents",initialState,reducers: {setActiveAgent: (state, action: PayloadAction<AgentType>) => {state.activeAgent = action.payload;
    },
    addUserMessage: (
      state,
      action: PayloadAction<{,
  agentType: AgentType;
        content: string;
        type?: "text" | "image" | "audio" | "file";
      }>
    ) => {
      const { agentType, content, type = "text" } = action.payload;
      const userMessage: AgentMessage = {,
  id: Date.now().toString(),
        agentType,
        content,
        type,
        timestamp: new Date().toISOString();
      };
      state.conversations[agentType].push(userMessage);
    },
    removeMessage: (
      state,
      action: PayloadAction<{ agentType: AgentType; messageId: string }>
    ) => {
      const { agentType, messageId } = action.payload;
      state.conversations[agentType] = state.conversations[agentType].filter(message) => message.id !== messageId;
      );
    },
    clearError: (state) => {
      state.error = undefined;
    },
    updateMessage: (
      state,
      action: PayloadAction<{,
  agentType: AgentType;
        messageId: string,
  updates: Partial<AgentMessage>;
      }>
    ) => {
      const { agentType, messageId, updates } = action.payload;
      const messageIndex = state.conversations[agentType].findIndex(;
        (msg) => msg.id === messageId;
      );
      if (messageIndex >= 0) {
        state.conversations[agentType][messageIndex] = {
          ...state.conversations[agentType][messageIndex],
          ...updates;
        };
      }
    }
  },
  extraReducers: (builder) => {
    // 发送消息给智能体
    builder;
      .addCase(sendMessageToAgent.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(sendMessageToAgent.fulfilled, (state, action) => {
        state.loading = false;
        state.conversations[action.payload.agentType].push(action.payload);
        state.error = undefined;
      })
      .addCase(sendMessageToAgent.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
    // 加载对话历史
    builder;
      .addCase(loadConversationHistory.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(loadConversationHistory.fulfilled, (state, action) => {
        state.loading = false;
        state.conversations[action.payload.agentType] = action.payload.messages;
        state.error = undefined;
      })
      .addCase(loadConversationHistory.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
    // 清除对话
    builder;
      .addCase(clearConversation.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(clearConversation.fulfilled, (state, action) => {
        state.loading = false;
        state.conversations[action.payload] = [];
        state.error = undefined;
      })
      .addCase(clearConversation.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});
// 导出actions;
export const {
  setActiveAgent,
  addUserMessage,
  removeMessage,
  clearError,
  updateMessage;
} = agentsSlice.actions;
// 选择器
export const selectAgents = (state: { agents: AgentsState }) => state.agents;
export const selectActiveAgent = (state: { agents: AgentsState }) =>;
  state.agents.activeAgent;
export const selectConversations = (state: { agents: AgentsState }) =>;
  state.agents.conversations;
export const selectAgentLoading = (state: { agents: AgentsState }) =>;
  state.agents.loading;
export const selectAgentError = (state: { agents: AgentsState }) =>;
  state.agents.error;
export default agentsSlice.reducer;
