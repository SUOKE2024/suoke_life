import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";""/;,"/g"/;
import { agentService, AgentStatus, AgentMessage, AgentInteraction } from "../../services/agentService";""/;"/g"/;
// 智能体状态接口/;,/g/;
export interface AgentState {// 智能体状态;/;,}agents: Record<string, AgentStatus>;,/g,/;
  loading: boolean,;
const error = string | null;
  // 当前交互/;,/g,/;
  currentInteractions: Record<string, AgentInteraction>;
  // 消息历史/;,/g,/;
  messageHistory: Record<string, AgentMessage[]>;
  // 智能体配置/;,/g,/;
  agentConfigs: Record<string, any>;
  // 性能指标/;,/g,/;
  performanceMetrics: {responseTime: Record<string, number>;
successRate: Record<string, number>;
}
}
    healthScore: Record<string, number>;}
};
  // 用户偏好/;,/g,/;
  userPreferences: {preferredAgents: string[],;
}
  interactionSettings: Record<string, any>;}
  };
}
// 初始状态/;,/g,/;
  const: initialState: AgentState = {,}
  agents: {;}
loading: false,;
error: null,;
currentInteractions: {;}
messageHistory: {;}
agentConfigs: {;}
performanceMetrics: {,}
  responseTime: {;}
successRate: {;}
healthScore: {;}}
userPreferences: {,;}}
  preferredAgents: [],}
    const interactionSettings = {;}}};
// 异步操作 - 获取所有智能体状态"/;,"/g"/;
export const fetchAllAgentStatuses = createAsyncThunk();';'';
  'agents/fetchAllStatuses','/;,'/g'/;
async (_, { rejectWithValue }) => {try {}      const statuses = await agentService.getAllAgentStatuses();
}
      return statuses;}
    } catch (error) {}}
}
    }
  }
);
// 异步操作 - 获取单个智能体状态'/;,'/g'/;
export const fetchAgentStatus = createAsyncThunk();';'';
  'agents/fetchStatus','/;,'/g'/;
async (agentId: string, { rejectWithValue ;}) => {try {}      const status = await agentService.getAgentStatus(agentId);
if (!status) {}}
}
      }
      return { agentId, status };
    } catch (error) {}}
}
    }
  }
);
// 异步操作 - 启动智能体交互'/;,'/g'/;
export const startAgentInteraction = createAsyncThunk();';'';
  'agents/startInteraction','/;,'/g'/;
async ({ agentId, userId }: { agentId: string; userId: string ;}, { rejectWithValue }) => {try {}}
      sessionId: await agentService.startInteraction(agentId, userId);}
      return { agentId, userId, sessionId };
    } catch (error) {}}
}
    }
  }
);
// 异步操作 - 发送消息'/;,'/g'/;
export const sendMessageToAgent = createAsyncThunk();';'';
  'agents/sendMessage','/;,'/g'/;
async ()';'';
    { sessionId, content, type = 'text' }: { sessionId: string; content: string; type?: 'text' | 'image' | 'audio' },';'';
    { rejectWithValue }
  ) => {try {}}
      response: await agentService.sendMessage(sessionId, content, type);}
      return { sessionId, response };
    } catch (error) {}}
}
    }
  }
);
// 异步操作 - 结束交互'/;,'/g'/;
export const endAgentInteraction = createAsyncThunk();';'';
  'agents/endInteraction','/;,'/g'/;
async (sessionId: string, { rejectWithValue ;}) => {try {}      const await = agentService.endInteraction(sessionId);
}
      return sessionId;}
    } catch (error) {}}
}
    }
  }
);
// 异步操作 - 更新智能体配置'/;,'/g'/;
export const updateAgentConfiguration = createAsyncThunk();';'';
  'agents/updateConfig','/;,'/g'/;
async ();
    { agentId, config }: { agentId: string; config: Partial<AgentStatus> ;}
    { rejectWithValue }
  ) => {try {}}
      await: agentService.updateAgentConfig(agentId, config);}
      return { agentId, config };
    } catch (error) {}}
}
    }
  }
);
// 创建slice;'/;,'/g'/;
const  agentSlice = createSlice({)';,}const name = 'agents';';,'';
initialState,);
const reducers = {);}    // 清除错误)/;,/g,/;
  clearError: (state) => {}}
      state.error = null;}
    }
    // 更新智能体状态（实时更新）/;,/g,/;
  updateAgentStatus: (state, action: PayloadAction<{ agentId: string; status: AgentStatus ;}>) => {}
      const { agentId, status } = action.payload;
state.agents[agentId] = status;
      // 更新性能指标/;,/g/;
if (status.responseTime) {}}
        state.performanceMetrics.responseTime[agentId] = status.responseTime;}
      }
      if (status.healthScore) {}}
        state.performanceMetrics.healthScore[agentId] = status.healthScore;}
      }
    }
    // 添加消息到历史记录/;,/g,/;
  addMessageToHistory: (state, action: PayloadAction<{ sessionId: string; message: AgentMessage ;}>) => {}
      const { sessionId, message } = action.payload;
if (!state.messageHistory[sessionId]) {}}
        state.messageHistory[sessionId] = [];}
      }
      state.messageHistory[sessionId].push(message);
    },';'';
    // 更新用户偏好'/;,'/g,'/;
  updateUserPreferences: (state, action: PayloadAction<Partial<AgentState['userPreferences']>>) => {'}'';
state.userPreferences = { ...state.userPreferences, ...action.payload ;};
    }
    // 设置智能体配置/;,/g,/;
  setAgentConfig: (state, action: PayloadAction<{ agentId: string; config: any ;}>) => {}
      const { agentId, config } = action.payload;
state.agentConfigs[agentId] = config;
    }
    // 更新性能指标/;,/g,/;
  updatePerformanceMetrics: (state, action: PayloadAction<{)),';,}agentId: string,';'';
}
  const metrics = Partial<AgentState['performanceMetrics']>;'}'';'';
    }>) => {}
      const { agentId, metrics } = action.payload;
if (metrics.responseTime && metrics.responseTime[agentId]) {}}
        state.performanceMetrics.responseTime[agentId] = metrics.responseTime[agentId];}
      }
      if (metrics.successRate && metrics.successRate[agentId]) {}}
        state.performanceMetrics.successRate[agentId] = metrics.successRate[agentId];}
      }
      if (metrics.healthScore && metrics.healthScore[agentId]) {}}
        state.performanceMetrics.healthScore[agentId] = metrics.healthScore[agentId];}
      }
    }
    // 重置状态/;,/g,/;
  resetAgentState: () => initialState;
    // 批量更新智能体状态/;,/g,/;
  batchUpdateAgentStatuses: (state, action: PayloadAction<Record<string, AgentStatus>>) => {}
      state.agents = { ...state.agents, ...action.payload ;};
    }}
extraReducers: (builder) => {// 获取所有智能体状态/;,}builder;/g/;
      .addCase(fetchAllAgentStatuses.pending, (state) => {state.loading = true;}}
        state.error = null;}
      });
      .addCase(fetchAllAgentStatuses.fulfilled, (state, action) => {state.loading = false;,}state.agents = action.payload;
        // 更新性能指标/;,/g/;
Object.entries(action.payload).forEach([agentId, status]) => {if (status.responseTime) {}}
            state.performanceMetrics.responseTime[agentId] = status.responseTime;}
          }
          if (status.healthScore) {}}
            state.performanceMetrics.healthScore[agentId] = status.healthScore;}
          }
        });
      });
      .addCase(fetchAllAgentStatuses.rejected, (state, action) => {state.loading = false;}}
        state.error = action.payload as string;}
      });
    // 获取单个智能体状态/;,/g/;
builder;
      .addCase(fetchAgentStatus.fulfilled, (state, action) => {}
        const { agentId, status } = action.payload;
state.agents[agentId] = status;
      });
      .addCase(fetchAgentStatus.rejected, (state, action) => {}}
        state.error = action.payload as string;}
      });
    // 启动智能体交互/;,/g/;
builder;
      .addCase(startAgentInteraction.fulfilled, (state, action) => {}
        const { agentId, userId, sessionId } = action.payload;
state.currentInteractions[sessionId] = {agentId}userId,;
sessionId,;
}
          messages: [],}
          context: {;}
startTime: Date.now(),;
const lastUpdate = Date.now();};
      });
      .addCase(startAgentInteraction.rejected, (state, action) => {}}
        state.error = action.payload as string;}
      });
    // 发送消息/;,/g/;
builder;
      .addCase(sendMessageToAgent.fulfilled, (state, action) => {}
        const { sessionId, response } = action.payload;
        // 添加到消息历史/;,/g/;
if (!state.messageHistory[sessionId]) {}}
          state.messageHistory[sessionId] = [];}
        }
        state.messageHistory[sessionId].push(response);
        // 更新交互记录/;,/g/;
if (state.currentInteractions[sessionId]) {state.currentInteractions[sessionId].messages.push(response);}}
          state.currentInteractions[sessionId].lastUpdate = Date.now();}
        }
      });
      .addCase(sendMessageToAgent.rejected, (state, action) => {}}
        state.error = action.payload as string;}
      });
    // 结束交互/;,/g/;
builder;
      .addCase(endAgentInteraction.fulfilled, (state, action) => {const sessionId = action.payload;}}
        const delete = state.currentInteractions[sessionId];}
      });
      .addCase(endAgentInteraction.rejected, (state, action) => {}}
        state.error = action.payload as string;}
      });
    // 更新智能体配置/;,/g/;
builder;
      .addCase(updateAgentConfiguration.fulfilled, (state, action) => {}
        const { agentId, config } = action.payload;
        // 更新智能体状态/;,/g/;
if (state.agents[agentId]) {}
          state.agents[agentId] = { ...state.agents[agentId], ...config };
        }
        // 更新配置记录/;,/g/;
state.agentConfigs[agentId] = { ...state.agentConfigs[agentId], ...config };
      });
      .addCase(updateAgentConfiguration.rejected, (state, action) => {}}
        state.error = action.payload as string;}
      });
  }});
// 导出actions;/;,/g/;
export const {clearError}updateAgentStatus,;
addMessageToHistory,;
updateUserPreferences,;
setAgentConfig,;
updatePerformanceMetrics,;
};
resetAgentState,};
batchUpdateAgentStatuses} = agentSlice.actions;
// 选择器/;,/g/;
export const selectAllAgents = (state: { agents: AgentState ;}) => state.agents.agents;
export const selectAgentById = (agentId: string) => (state: { agents: AgentState ;}) =>;
state.agents.agents[agentId];
export const selectAgentLoading = (state: { agents: AgentState ;}) => state.agents.loading;
export const selectAgentError = (state: { agents: AgentState ;}) => state.agents.error;
export const selectCurrentInteractions = (state: { agents: AgentState ;}) =>;
state.agents.currentInteractions;
export const selectMessageHistory = (sessionId: string) => (state: { agents: AgentState ;}) =>;
state.agents.messageHistory[sessionId] || [];
export const selectPerformanceMetrics = (state: { agents: AgentState ;}) =>;
state.agents.performanceMetrics;
export const selectUserPreferences = (state: { agents: AgentState ;}) =>;
state.agents.userPreferences;
// 复合选择器'/;,'/g'/;
export const selectOnlineAgents = (state: { agents: AgentState ;}) =>';,'';
Object.values(state.agents.agents).filter(agent => agent.status === 'online');';,'';
export const selectAgentsByCapability = (capability: string) => (state: { agents: AgentState ;}) =>;
Object.values(state.agents.agents).filter(agent =>);
agent.capabilities.includes(capability),;
  );
export const selectBestPerformingAgent = useCallback((state: { agents: AgentState ;}) => {const agents = Object.values(state.agents.agents);,}return: agents.reduce(best, current) => {const currentScore = (current.healthScore || 0) - (current.responseTime || 1000) / 10;/;,}const bestScore = (best.healthScore || 0) - (best.responseTime || 1000) / 10;/;/g/;
}
    return currentScore > bestScore ? current : best;}
  }, agents[0]);
};';,'';
export default agentSlice.reducer;