import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { API_URL } from '../../config/constants';
import axios from 'axios';

// 智能体相关接口定义
export interface Agent {
  id: string;
  name: string;
  type: string;
  description: string;
  avatar: string;
  capabilities: string[];
  isActive: boolean;
}

export interface Conversation {
  id: string;
  agentId: string;
  title: string;
  lastMessage: string;
  unreadCount: number;
  createdAt: number;
  updatedAt: number;
}

export interface AgentState {
  agents: Agent[];
  selectedAgent: Agent | null;
  conversations: Conversation[];
  currentConversation: Conversation | null;
  isLoading: boolean;
  error: string | null;
}

// 初始状态
const initialState: AgentState = {
  agents: [],
  selectedAgent: null,
  conversations: [],
  currentConversation: null,
  isLoading: false,
  error: null
};

// 获取所有智能体
export const fetchAgents = createAsyncThunk('agent/fetchAgents', async (_, { rejectWithValue }) => {
  try {
    // 实际项目中这里应该从API获取数据
    // 现在使用模拟数据
    const mockAgents: Agent[] = [
      {
        id: 'xiaoai',
        name: '小艾',
        type: 'medical',
        description: '医疗问诊智能体，专注于四诊合参、疾病分析和健康指导',
        avatar: 'https://www.suoke.life/images/agents/xiaoai.png',
        capabilities: ['问诊', '健康分析', '体质评估'],
        isActive: true
      },
      {
        id: 'xiaoke',
        name: '小克',
        type: 'nutrition',
        description: '营养饮食智能体，提供个性化饮食建议和食疗指导',
        avatar: 'https://www.suoke.life/images/agents/xiaoke.png',
        capabilities: ['食疗', '食谱推荐', '营养分析'],
        isActive: true
      },
      {
        id: 'laoke',
        name: '老克',
        type: 'knowledge',
        description: '中医知识智能体，精通中医理论和经典著作',
        avatar: 'https://www.suoke.life/images/agents/laoke.png',
        capabilities: ['中医知识', '经方解析', '养生理论'],
        isActive: true
      },
      {
        id: 'soer',
        name: '索儿',
        type: 'lifestyle',
        description: '生活养生智能体，指导日常生活习惯和养生实践',
        avatar: 'https://www.suoke.life/images/agents/soer.png',
        capabilities: ['习惯培养', '生活指导', '养生实践'],
        isActive: true
      }
    ];
    
    // 模拟API延迟
    await new Promise(resolve => setTimeout(resolve, 500));
    
    return mockAgents;
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.message || '无法获取智能体数据');
  }
});

// Agent状态切片
const agentSlice = createSlice({
  name: 'agent',
  initialState,
  reducers: {
    selectAgent: (state, action: PayloadAction<string>) => {
      state.selectedAgent = state.agents.find(agent => agent.id === action.payload) || null;
    },
    clearSelectedAgent: (state) => {
      state.selectedAgent = null;
    },
    clearError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // 获取所有智能体
      .addCase(fetchAgents.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchAgents.fulfilled, (state, action) => {
        state.isLoading = false;
        state.agents = action.payload;
      })
      .addCase(fetchAgents.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  }
});

export const { selectAgent, clearSelectedAgent, clearError } = agentSlice.actions;

export default agentSlice.reducer; 