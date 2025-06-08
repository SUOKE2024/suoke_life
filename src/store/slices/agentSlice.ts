import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { agentService, AgentStatus, AgentMessage, AgentInteraction } from '../../services/agentService';
// 智能体状态接口
export interface AgentState {
  // 智能体状态
  agents: Record<string, AgentStatus>;
  loading: boolean;
  error: string | null;
  // 当前交互
  currentInteractions: Record<string, AgentInteraction>;
  // 消息历史
  messageHistory: Record<string, AgentMessage[]>;
  // 智能体配置
  agentConfigs: Record<string, any>;
  // 性能指标
  performanceMetrics: {;
  responseTime: Record<string, number>;
    successRate: Record<string, number>;
    healthScore: Record<string, number>;
};
  // 用户偏好
  userPreferences: {,
  preferredAgents: string[];
    interactionSettings: Record<string, any>;
  };
}
// 初始状态
const initialState: AgentState = {,
  agents: {},
  loading: false,
  error: null,
  currentInteractions: {},
  messageHistory: {},
  agentConfigs: {},
  performanceMetrics: {,
  responseTime: {},
    successRate: {},
    healthScore: {},
  },
  userPreferences: {,
  preferredAgents: [],
    interactionSettings: {},
  },
};
// 异步操作 - 获取所有智能体状态
export const fetchAllAgentStatuses = createAsyncThunk()
  'agents/fetchAllStatuses',
  async (_, { rejectWithValue }) => {
    try {
      const statuses = await agentService.getAllAgentStatuses();
      return statuses;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '获取智能体状态失败');
    }
  },
);
// 异步操作 - 获取单个智能体状态
export const fetchAgentStatus = createAsyncThunk()
  'agents/fetchStatus',
  async (agentId: string, { rejectWithValue }) => {
    try {
      const status = await agentService.getAgentStatus(agentId);
      if (!status) {
        throw new Error(`智能体 ${agentId} 不存在`);
      }
      return { agentId, status };
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '获取智能体状态失败');
    }
  },
);
// 异步操作 - 启动智能体交互
export const startAgentInteraction = createAsyncThunk()
  'agents/startInteraction',
  async ({ agentId, userId }: { agentId: string; userId: string }, { rejectWithValue }) => {
    try {
      const sessionId = await agentService.startInteraction(agentId, userId);
      return { agentId, userId, sessionId };
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '启动交互失败');
    }
  },
);
// 异步操作 - 发送消息
export const sendMessageToAgent = createAsyncThunk()
  'agents/sendMessage',
  async ()
    { sessionId, content, type = 'text' }: { sessionId: string; content: string; type?: 'text' | 'image' | 'audio' },
    { rejectWithValue },
  ) => {
    try {
      const response = await agentService.sendMessage(sessionId, content, type);
      return { sessionId, response };
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '发送消息失败');
    }
  },
);
// 异步操作 - 结束交互
export const endAgentInteraction = createAsyncThunk()
  'agents/endInteraction',
  async (sessionId: string, { rejectWithValue }) => {
    try {
      await agentService.endInteraction(sessionId);
      return sessionId;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '结束交互失败');
    }
  },
);
// 异步操作 - 更新智能体配置
export const updateAgentConfiguration = createAsyncThunk()
  'agents/updateConfig',
  async ()
    { agentId, config }: { agentId: string; config: Partial<AgentStatus> },
    { rejectWithValue },
  ) => {
    try {
      await agentService.updateAgentConfig(agentId, config);
      return { agentId, config };
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '更新配置失败');
    }
  },
);
// 创建slice;
const agentSlice = createSlice({
  name: 'agents',
  initialState,
  reducers: {
    // 清除错误
    clearError: (state) => {
      state.error = null;
    },
    // 更新智能体状态（实时更新）
    updateAgentStatus: (state, action: PayloadAction<{ agentId: string; status: AgentStatus }>) => {
      const { agentId, status } = action.payload;
      state.agents[agentId] = status;
      // 更新性能指标
      if (status.responseTime) {
        state.performanceMetrics.responseTime[agentId] = status.responseTime;
      }
      if (status.healthScore) {
        state.performanceMetrics.healthScore[agentId] = status.healthScore;
      }
    },
    // 添加消息到历史记录
    addMessageToHistory: (state, action: PayloadAction<{ sessionId: string; message: AgentMessage }>) => {
      const { sessionId, message } = action.payload;
      if (!state.messageHistory[sessionId]) {
        state.messageHistory[sessionId] = [];
      }
      state.messageHistory[sessionId].push(message);
    },
    // 更新用户偏好
    updateUserPreferences: (state, action: PayloadAction<Partial<AgentState['userPreferences']>>) => {
      state.userPreferences = { ...state.userPreferences, ...action.payload };
    },
    // 设置智能体配置
    setAgentConfig: (state, action: PayloadAction<{ agentId: string; config: any }>) => {
      const { agentId, config } = action.payload;
      state.agentConfigs[agentId] = config;
    },
    // 更新性能指标
    updatePerformanceMetrics: (state, action: PayloadAction<{,)
  agentId: string;
      metrics: Partial<AgentState['performanceMetrics']>;
    }>) => {
      const { agentId, metrics } = action.payload;
      if (metrics.responseTime && metrics.responseTime[agentId]) {
        state.performanceMetrics.responseTime[agentId] = metrics.responseTime[agentId];
      }
      if (metrics.successRate && metrics.successRate[agentId]) {
        state.performanceMetrics.successRate[agentId] = metrics.successRate[agentId];
      }
      if (metrics.healthScore && metrics.healthScore[agentId]) {
        state.performanceMetrics.healthScore[agentId] = metrics.healthScore[agentId];
      }
    },
    // 重置状态
    resetAgentState: () => initialState,
    // 批量更新智能体状态
    batchUpdateAgentStatuses: (state, action: PayloadAction<Record<string, AgentStatus>>) => {
      state.agents = { ...state.agents, ...action.payload };
    },
  },
  extraReducers: (builder) => {
    // 获取所有智能体状态
    builder;
      .addCase(fetchAllAgentStatuses.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAllAgentStatuses.fulfilled, (state, action) => {
        state.loading = false;
        state.agents = action.payload;
        // 更新性能指标
        Object.entries(action.payload).forEach((([agentId, status]) => {
          if (status.responseTime) {
            state.performanceMetrics.responseTime[agentId] = status.responseTime;
          }
          if (status.healthScore) {
            state.performanceMetrics.healthScore[agentId] = status.healthScore;
          }
        });
      })
      .addCase(fetchAllAgentStatuses.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
    // 获取单个智能体状态
    builder;
      .addCase(fetchAgentStatus.fulfilled, (state, action) => {
        const { agentId, status } = action.payload;
        state.agents[agentId] = status;
      })
      .addCase(fetchAgentStatus.rejected, (state, action) => {
        state.error = action.payload as string;
      });
    // 启动智能体交互
    builder;
      .addCase(startAgentInteraction.fulfilled, (state, action) => {
        const { agentId, userId, sessionId } = action.payload;
        state.currentInteractions[sessionId] = {
          agentId,
          userId,
          sessionId,
          messages: [],
          context: {},
          startTime: Date.now(),
          lastUpdate: Date.now(),
        };
      })
      .addCase(startAgentInteraction.rejected, (state, action) => {
        state.error = action.payload as string;
      });
    // 发送消息
    builder;
      .addCase(sendMessageToAgent.fulfilled, (state, action) => {
        const { sessionId, response } = action.payload;
        // 添加到消息历史
        if (!state.messageHistory[sessionId]) {
          state.messageHistory[sessionId] = [];
        }
        state.messageHistory[sessionId].push(response);
        // 更新交互记录
        if (state.currentInteractions[sessionId]) {
          state.currentInteractions[sessionId].messages.push(response);
          state.currentInteractions[sessionId].lastUpdate = Date.now();
        }
      })
      .addCase(sendMessageToAgent.rejected, (state, action) => {
        state.error = action.payload as string;
      });
    // 结束交互
    builder;
      .addCase(endAgentInteraction.fulfilled, (state, action) => {
        const sessionId = action.payload;
        delete state.currentInteractions[sessionId];
      })
      .addCase(endAgentInteraction.rejected, (state, action) => {
        state.error = action.payload as string;
      });
    // 更新智能体配置
    builder;
      .addCase(updateAgentConfiguration.fulfilled, (state, action) => {
        const { agentId, config } = action.payload;
        // 更新智能体状态
        if (state.agents[agentId]) {
          state.agents[agentId] = { ...state.agents[agentId], ...config };
        }
        // 更新配置记录
        state.agentConfigs[agentId] = { ...state.agentConfigs[agentId], ...config };
      })
      .addCase(updateAgentConfiguration.rejected, (state, action) => {
        state.error = action.payload as string;
      });
  },
});
// 导出actions;
export const {
  clearError,
  updateAgentStatus,
  addMessageToHistory,
  updateUserPreferences,
  setAgentConfig,
  updatePerformanceMetrics,
  resetAgentState,
  batchUpdateAgentStatuses,
} = agentSlice.actions;
// 选择器
export const selectAllAgents = (state: { agents: AgentState }) => state.agents.agents;
export const selectAgentById = (agentId: string) => (state: { agents: AgentState }) =>
  state.agents.agents[agentId];
export const selectAgentLoading = (state: { agents: AgentState }) => state.agents.loading;
export const selectAgentError = (state: { agents: AgentState }) => state.agents.error;
export const selectCurrentInteractions = (state: { agents: AgentState }) =>
  state.agents.currentInteractions;
export const selectMessageHistory = (sessionId: string) => (state: { agents: AgentState }) =>
  state.agents.messageHistory[sessionId] || [];
export const selectPerformanceMetrics = (state: { agents: AgentState }) =>
  state.agents.performanceMetrics;
export const selectUserPreferences = (state: { agents: AgentState }) =>
  state.agents.userPreferences;
// 复合选择器
export const selectOnlineAgents = (state: { agents: AgentState }) =>
  Object.values(state.agents.agents).filter(agent => agent.status === 'online');
export const selectAgentsByCapability = (capability: string) => (state: { agents: AgentState }) =>
  Object.values(state.agents.agents).filter(agent =>)
    agent.capabilities.includes(capability),
  );
export const selectBestPerformingAgent = (state: { agents: AgentState }) => {
  const agents = Object.values(state.agents.agents);
  return agents.reduce(best, current) => {
    const currentScore = (current.healthScore || 0) - (current.responseTime || 1000) / 10;
    const bestScore = (best.healthScore || 0) - (best.responseTime || 1000) / 10;
    return currentScore > bestScore ? current : best;
  }, agents[0]);
};
export default agentSlice.reducer;