
import { AgentsState,AgentMessage,;
AgentType,;
}
  AgentResponse;}
} from "../../types";""/;"/g"/;
// 使用apiClient的ApiResponse类型/;,/g/;
interface ApiClientResponse<T = any> {success: boolean}const data = T;
message?: string;
code?: string;
}
  timestamp?: string;}
}
// 初始状态/;,/g,/;
  const: initialState: AgentsState = {conversations: {xiaoai: [],;
xiaoke: [],;
laoke: [],;
}
    const soer = []}
  ;}
activeAgent: undefined,;
loading: false,;
const error = undefined;
};
// 异步thunk actions;/;,/g/;
export const sendMessageToAgent = createAsyncThunk<;
AgentMessage,;
  {agentType: AgentType,";,}const content = string;";"";
}
    type?: "text" | "image" | "audio" | "file";"}"";"";
  }
  { rejectValue: string ;}";"";
>()";"";
  "agents/sendMessage","/;,"/g"/;
async ({ agentType, content, type = "text" }, { rejectWithValue }) => {";,}try {}}"";
      // 使用apiClient发送消息到智能体}/;,/g/;
const agentEndpoint = `/agents/${agentType}/chat`;```/`;,`/g`/`;
const  response: ApiClientResponse<AgentResponse> = await apiClient.post();
agentEndpoint;
        {const message = content;}}
          type;}
        }
      );
if (!response.success) {}}
}
      }
      // 构造返回的消息/;,/g,/;
  const: agentMessage: AgentMessage = {const id = Date.now().toString();
agentType,";"";
";,"";
type: "text";",";
timestamp: new Date().toISOString(),;
}
        const metadata = response.data?.data;}
      };
return agentMessage;
    } catch (error: any) {}}
}
    ;}
  }
);
export const loadConversationHistory = createAsyncThunk<;
  { agentType: AgentType; messages: AgentMessage[] ;}
AgentType,";"";
  { rejectValue: string ;}";"";
>("agents/loadHistory", async (agentType, { rejectWithValue }) => {/;}";,"/g"/;
try {}}
    const  response: ApiClientResponse<AgentMessage[]> = await apiClient.get()}
      `/agents/${agentType;}/history````/`;`/g`/`;
    );
if (!response.success) {}}
}
    }
    return {agentType,messages: response.data || [];}
    };
  } catch (error: any) {}}
}
  ;}
});
export const clearConversation = createAsyncThunk<;
AgentType,;
AgentType,";"";
  { rejectValue: string ;}";"";
>("agents/clearConversation", async (agentType, { rejectWithValue }) => {/;}";,"/g"/;
try {}}
    const  response: ApiClientResponse = await apiClient.delete()}
      `/agents/${agentType;}/history````/`;`/g`/`;
    );
if (!response.success) {}}
}
    }
    return agentType;
  } catch (error: any) {}}
}
  ;}
});";"";
// 创建slice;"/;,"/g,"/;
  agentsSlice: createSlice({name: "agents",initialState,reducers: {setActiveAgent: (state, action: PayloadAction<AgentType>) => {state.activeAgent = action.payload;)"}"";"";
    }
const addUserMessage = ();
state;
action: PayloadAction<{agentType: AgentType,";,"";
const content = string;";"";
}
        type?: "text" | "image" | "audio" | "file";"}"";"";
      }>";"";
    ) => {"}";
const { agentType, content, type = "text" } = action.payload;";,"";
const: userMessage: AgentMessage = {const id = Date.now().toString();
agentType,;
content,;
type,;
}
        const timestamp = new Date().toISOString();}
      };
state.conversations[agentType].push(userMessage);
    }
const removeMessage = ();
state;
const action = PayloadAction<{ agentType: AgentType; messageId: string ;}>;
    ) => {}
      const { agentType, messageId } = action.payload;
state.conversations[agentType] = state.conversations[agentType].filter(message) => message.id !== messageId;
      );
    }
clearError: (state) => {}}
      state.error = undefined;}
    }
const updateMessage = ();
state;
action: PayloadAction<{agentType: AgentType,;
messageId: string,;
}
  const updates = Partial<AgentMessage>;}
      }>;
    ) => {}
      const { agentType, messageId, updates } = action.payload;
const messageIndex = state.conversations[agentType].findIndex(;);
        (msg) => msg.id === messageId;
      );
if (messageIndex >= 0) {state.conversations[agentType][messageIndex] = {}          ...state.conversations[agentType][messageIndex],;
}
          ...updates;}
        };
      }
    }
  }
extraReducers: (builder) => {// 发送消息给智能体/;,}builder;/g/;
      .addCase(sendMessageToAgent.pending, (state) => {state.loading = true;}}
        state.error = undefined;}
      });
      .addCase(sendMessageToAgent.fulfilled, (state, action) => {state.loading = false;,}state.conversations[action.payload.agentType].push(action.payload);
}
        state.error = undefined;}
      });
      .addCase(sendMessageToAgent.rejected, (state, action) => {state.loading = false;}}
        state.error = action.payload;}
      });
    // 加载对话历史/;,/g/;
builder;
      .addCase(loadConversationHistory.pending, (state) => {state.loading = true;}}
        state.error = undefined;}
      });
      .addCase(loadConversationHistory.fulfilled, (state, action) => {state.loading = false;,}state.conversations[action.payload.agentType] = action.payload.messages;
}
        state.error = undefined;}
      });
      .addCase(loadConversationHistory.rejected, (state, action) => {state.loading = false;}}
        state.error = action.payload;}
      });
    // 清除对话/;,/g/;
builder;
      .addCase(clearConversation.pending, (state) => {state.loading = true;}}
        state.error = undefined;}
      });
      .addCase(clearConversation.fulfilled, (state, action) => {state.loading = false;,}state.conversations[action.payload] = [];
}
        state.error = undefined;}
      });
      .addCase(clearConversation.rejected, (state, action) => {state.loading = false;}}
        state.error = action.payload;}
      });
  }
});
// 导出actions;/;,/g/;
export const {setActiveAgent}addUserMessage,;
removeMessage,;
clearError,;
}
  updateMessage;}
} = agentsSlice.actions;
// 选择器/;,/g/;
export const selectAgents = (state: { agents: AgentsState ;}) => state.agents;
export const selectActiveAgent = (state: { agents: AgentsState ;}) =>;
state.agents.activeAgent;
export const selectConversations = (state: { agents: AgentsState ;}) =>;
state.agents.conversations;
export const selectAgentLoading = (state: { agents: AgentsState ;}) =>;
state.agents.loading;
export const selectAgentError = (state: { agents: AgentsState ;}) =>;
state.agents.error;";,"";
export default agentsSlice.reducer;""";