import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import {medKnowledgeService,
  Constitution,
  Symptom,
  Acupoint,
  Herb,
  Syndrome,
  KnowledgeQuery,
  KnowledgeResult,
  GraphData,
  HealthRecommendation,
  RecommendationRequest;
} from '../../services/medKnowledgeService';
// 状态接口定义
export interface MedKnowledgeState {
  // 数据状态
  constitutions: Constitution[];
  symptoms: Symptom[];
  acupoints: Acupoint[];
  herbs: Herb[];
  syndromes: Syndrome[];
  searchResults: KnowledgeResult[];
  knowledgeGraph: GraphData | null;
  recommendations: HealthRecommendation[];
  // 当前选中项
  selectedConstitution: Constitution | null;
  selectedSymptom: Symptom | null;
  selectedAcupoint: Acupoint | null;
  selectedHerb: Herb | null;
  selectedSyndrome: Syndrome | null;
  // 加载状态
  loading: {;
  constitutions: boolean;
    symptoms: boolean;
  acupoints: boolean;
    herbs: boolean;
  syndromes: boolean;
    search: boolean;
  graph: boolean;
    recommendations: boolean;
};
  // 错误状态
  error: {,
  constitutions: string | null;
    symptoms: string | null,
  acupoints: string | null;
    herbs: string | null,
  syndromes: string | null;
    search: string | null,
  graph: string | null;
    recommendations: string | null;
  };
  // 搜索状态
  searchQuery: KnowledgeQuery | null,
  searchHistory: string[];
  // 缓存状态
  lastUpdated: {,
  constitutions: number | null;
    symptoms: number | null,
  acupoints: number | null;
    herbs: number | null,
  syndromes: number | null;
  };
  // 服务状态
  serviceHealth: {,
  status: 'unknown' | 'healthy' | 'unhealthy';
    lastCheck: number | null;
  };
}
// 初始状态
const initialState: MedKnowledgeState = {,
  constitutions: [],
  symptoms: [],
  acupoints: [],
  herbs: [],
  syndromes: [],
  searchResults: [],
  knowledgeGraph: null,
  recommendations: [],
  selectedConstitution: null,
  selectedSymptom: null,
  selectedAcupoint: null,
  selectedHerb: null,
  selectedSyndrome: null,
  loading: {,
  constitutions: false,
    symptoms: false,
    acupoints: false,
    herbs: false,
    syndromes: false,
    search: false,
    graph: false,
    recommendations: false;
  },
  error: {,
  constitutions: null,
    symptoms: null,
    acupoints: null,
    herbs: null,
    syndromes: null,
    search: null,
    graph: null,
    recommendations: null;
  },
  searchQuery: null,
  searchHistory: [],
  lastUpdated: {,
  constitutions: null,
    symptoms: null,
    acupoints: null,
    herbs: null,
    syndromes: null;
  },
  serviceHealth: {,
  status: 'unknown',
    lastCheck: null;
  }
};
// 异步操作
export const fetchConstitutions = createAsyncThunk(;
  'medKnowledge/fetchConstitutions',
  async (_, { rejectWithValue }) => {
    try {
      return await medKnowledgeService.getConstitutions();
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '获取体质信息失败');
    }
  }
);
export const fetchConstitutionById = createAsyncThunk(;
  'medKnowledge/fetchConstitutionById',
  async (id: string, { rejectWithValue }) => {
    try {
      return await medKnowledgeService.getConstitutionById(id);
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '获取体质详情失败');
    }
  }
);
export const fetchSymptoms = createAsyncThunk(;
  'medKnowledge/fetchSymptoms',
  async (_, { rejectWithValue }) => {
    try {
      return await medKnowledgeService.getSymptoms();
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '获取症状信息失败');
    }
  }
);
export const searchSymptoms = createAsyncThunk(;
  'medKnowledge/searchSymptoms',
  async (query: string, { rejectWithValue }) => {
    try {
      return await medKnowledgeService.searchSymptoms(query);
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '搜索症状失败');
    }
  }
);
export const fetchAcupoints = createAsyncThunk(;
  'medKnowledge/fetchAcupoints',
  async (_, { rejectWithValue }) => {
    try {
      return await medKnowledgeService.getAcupoints();
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '获取穴位信息失败');
    }
  }
);
export const fetchAcupointsByConstitution = createAsyncThunk(;
  'medKnowledge/fetchAcupointsByConstitution',
  async (constitutionId: string, { rejectWithValue }) => {
    try {
      return await medKnowledgeService.getAcupointsByConstitution(constitutionId);
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '获取体质相关穴位失败');
    }
  }
);
export const fetchHerbs = createAsyncThunk(;
  'medKnowledge/fetchHerbs',
  async (_, { rejectWithValue }) => {
    try {
      return await medKnowledgeService.getHerbs();
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '获取中药信息失败');
    }
  }
);
export const fetchHerbsBySymptom = createAsyncThunk(;
  'medKnowledge/fetchHerbsBySymptom',
  async (symptomId: string, { rejectWithValue }) => {
    try {
      return await medKnowledgeService.getHerbsBySymptom(symptomId);
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '获取症状相关中药失败');
    }
  }
);
export const fetchSyndromes = createAsyncThunk(;
  'medKnowledge/fetchSyndromes',
  async (_, { rejectWithValue }) => {
    try {
      return await medKnowledgeService.getSyndromes();
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '获取证型信息失败');
    }
  }
);
export const searchKnowledge = createAsyncThunk(;
  'medKnowledge/searchKnowledge',
  async (query: KnowledgeQuery, { rejectWithValue }) => {
    try {
      return await medKnowledgeService.searchKnowledge(query);
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '知识搜索失败');
    }
  }
);
export const fetchKnowledgeGraph = createAsyncThunk(;
  'medKnowledge/fetchKnowledgeGraph',
  async (_, { rejectWithValue }) => {
    try {
      return await medKnowledgeService.getKnowledgeGraph();
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '获取知识图谱失败');
    }
  }
);
export const fetchPersonalizedRecommendations = createAsyncThunk(;
  'medKnowledge/fetchPersonalizedRecommendations',
  async (request: RecommendationRequest, { rejectWithValue }) => {
    try {
      return await medKnowledgeService.getPersonalizedRecommendations(request);
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '获取个性化推荐失败');
    }
  }
);
export const checkServiceHealth = createAsyncThunk(;
  'medKnowledge/checkServiceHealth',
  async (_, { rejectWithValue }) => {
    try {
      const result = await medKnowledgeService.healthCheck();
      return result;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '服务健康检查失败');
    }
  }
);
// 创建切片
const medKnowledgeSlice = createSlice({name: 'medKnowledge',initialState,reducers: {// 选择操作,
  selectConstitution: (state, action: PayloadAction<Constitution | null>) => {state.selectedConstitution = action.payload;
    },
    selectSymptom: (state, action: PayloadAction<Symptom | null>) => {
      state.selectedSymptom = action.payload;
    },
    selectAcupoint: (state, action: PayloadAction<Acupoint | null>) => {
      state.selectedAcupoint = action.payload;
    },
    selectHerb: (state, action: PayloadAction<Herb | null>) => {
      state.selectedHerb = action.payload;
    },
    selectSyndrome: (state, action: PayloadAction<Syndrome | null>) => {
      state.selectedSyndrome = action.payload;
    },
    // 搜索历史管理
    addToSearchHistory: (state, action: PayloadAction<string>) => {
      const query = action.payload.trim();
      if (query && !state.searchHistory.includes(query)) {
        state.searchHistory.unshift(query);
        // 保持最多10条历史记录
        if (state.searchHistory.length > 10) {
          state.searchHistory = state.searchHistory.slice(0, 10);
        }
      }
    },
    clearSearchHistory: (state) => {
      state.searchHistory = [];
    },
    // 清除错误
    clearError: (state, action: PayloadAction<keyof MedKnowledgeState['error']>) => {
      state.error[action.payload] = null;
    },
    clearAllErrors: (state) => {
      Object.keys(state.error).forEach(key => {
        state.error[key as keyof MedKnowledgeState['error']] = null;
      });
    },
    // 清除搜索结果
    clearSearchResults: (state) => {
      state.searchResults = [];
      state.searchQuery = null;
    },
    // 重置状态
    resetState: () => initialState;
  },
  extraReducers: (builder) => {
    // 体质相关
    builder;
      .addCase(fetchConstitutions.pending, (state) => {
        state.loading.constitutions = true;
        state.error.constitutions = null;
      })
      .addCase(fetchConstitutions.fulfilled, (state, action) => {
        state.loading.constitutions = false;
        state.constitutions = action.payload;
        state.lastUpdated.constitutions = Date.now();
      })
      .addCase(fetchConstitutions.rejected, (state, action) => {
        state.loading.constitutions = false;
        state.error.constitutions = action.payload as string;
      })
      .addCase(fetchConstitutionById.fulfilled, (state, action) => {
        state.selectedConstitution = action.payload;
        // 更新列表中的对应项
        const index = state.constitutions.findIndex(c => c.id === action.payload.id);
        if (index !== -1) {
          state.constitutions[index] = action.payload;
        }
      })
      // 症状相关
      .addCase(fetchSymptoms.pending, (state) => {
        state.loading.symptoms = true;
        state.error.symptoms = null;
      })
      .addCase(fetchSymptoms.fulfilled, (state, action) => {
        state.loading.symptoms = false;
        state.symptoms = action.payload;
        state.lastUpdated.symptoms = Date.now();
      })
      .addCase(fetchSymptoms.rejected, (state, action) => {
        state.loading.symptoms = false;
        state.error.symptoms = action.payload as string;
      })
      .addCase(searchSymptoms.fulfilled, (state, action) => {
        state.symptoms = action.payload;
      })
      // 穴位相关
      .addCase(fetchAcupoints.pending, (state) => {
        state.loading.acupoints = true;
        state.error.acupoints = null;
      })
      .addCase(fetchAcupoints.fulfilled, (state, action) => {
        state.loading.acupoints = false;
        state.acupoints = action.payload;
        state.lastUpdated.acupoints = Date.now();
      })
      .addCase(fetchAcupoints.rejected, (state, action) => {
        state.loading.acupoints = false;
        state.error.acupoints = action.payload as string;
      })
      .addCase(fetchAcupointsByConstitution.fulfilled, (state, action) => {
        state.acupoints = action.payload;
      })
      // 中药相关
      .addCase(fetchHerbs.pending, (state) => {
        state.loading.herbs = true;
        state.error.herbs = null;
      })
      .addCase(fetchHerbs.fulfilled, (state, action) => {
        state.loading.herbs = false;
        state.herbs = action.payload;
        state.lastUpdated.herbs = Date.now();
      })
      .addCase(fetchHerbs.rejected, (state, action) => {
        state.loading.herbs = false;
        state.error.herbs = action.payload as string;
      })
      .addCase(fetchHerbsBySymptom.fulfilled, (state, action) => {
        state.herbs = action.payload;
      })
      // 证型相关
      .addCase(fetchSyndromes.pending, (state) => {
        state.loading.syndromes = true;
        state.error.syndromes = null;
      })
      .addCase(fetchSyndromes.fulfilled, (state, action) => {
        state.loading.syndromes = false;
        state.syndromes = action.payload;
        state.lastUpdated.syndromes = Date.now();
      })
      .addCase(fetchSyndromes.rejected, (state, action) => {
        state.loading.syndromes = false;
        state.error.syndromes = action.payload as string;
      })
      // 知识搜索
      .addCase(searchKnowledge.pending, (state) => {
        state.loading.search = true;
        state.error.search = null;
      })
      .addCase(searchKnowledge.fulfilled, (state, action) => {
        state.loading.search = false;
        state.searchResults = action.payload;
        state.searchQuery = action.meta.arg;
      })
      .addCase(searchKnowledge.rejected, (state, action) => {
        state.loading.search = false;
        state.error.search = action.payload as string;
      })
      // 知识图谱
      .addCase(fetchKnowledgeGraph.pending, (state) => {
        state.loading.graph = true;
        state.error.graph = null;
      })
      .addCase(fetchKnowledgeGraph.fulfilled, (state, action) => {
        state.loading.graph = false;
        state.knowledgeGraph = action.payload;
      })
      .addCase(fetchKnowledgeGraph.rejected, (state, action) => {
        state.loading.graph = false;
        state.error.graph = action.payload as string;
      })
      // 个性化推荐
      .addCase(fetchPersonalizedRecommendations.pending, (state) => {
        state.loading.recommendations = true;
        state.error.recommendations = null;
      })
      .addCase(fetchPersonalizedRecommendations.fulfilled, (state, action) => {
        state.loading.recommendations = false;
        state.recommendations = action.payload;
      })
      .addCase(fetchPersonalizedRecommendations.rejected, (state, action) => {
        state.loading.recommendations = false;
        state.error.recommendations = action.payload as string;
      })
      // 服务健康检查
      .addCase(checkServiceHealth.fulfilled, (state) => {
        state.serviceHealth.status = 'healthy';
        state.serviceHealth.lastCheck = Date.now();
      })
      .addCase(checkServiceHealth.rejected, (state) => {
        state.serviceHealth.status = 'unhealthy';
        state.serviceHealth.lastCheck = Date.now();
      });
  }
});
// 导出actions;
export const {
  selectConstitution,
  selectSymptom,
  selectAcupoint,
  selectHerb,
  selectSyndrome,
  addToSearchHistory,
  clearSearchHistory,
  clearError,
  clearAllErrors,
  clearSearchResults,
  resetState;
} = medKnowledgeSlice.actions;
// 选择器
export const selectMedKnowledgeState = (state: { medKnowledge: MedKnowledgeState }) => state.medKnowledge;
export const selectConstitutions = (state: { medKnowledge: MedKnowledgeState }) => state.medKnowledge.constitutions;
export const selectSymptoms = (state: { medKnowledge: MedKnowledgeState }) => state.medKnowledge.symptoms;
export const selectAcupoints = (state: { medKnowledge: MedKnowledgeState }) => state.medKnowledge.acupoints;
export const selectHerbs = (state: { medKnowledge: MedKnowledgeState }) => state.medKnowledge.herbs;
export const selectSyndromes = (state: { medKnowledge: MedKnowledgeState }) => state.medKnowledge.syndromes;
export const selectSearchResults = (state: { medKnowledge: MedKnowledgeState }) => state.medKnowledge.searchResults;
export const selectKnowledgeGraph = (state: { medKnowledge: MedKnowledgeState }) => state.medKnowledge.knowledgeGraph;
export const selectRecommendations = (state: { medKnowledge: MedKnowledgeState }) => state.medKnowledge.recommendations;
export const selectSelectedConstitution = (state: { medKnowledge: MedKnowledgeState }) => state.medKnowledge.selectedConstitution;
export const selectLoading = (state: { medKnowledge: MedKnowledgeState }) => state.medKnowledge.loading;
export const selectErrors = (state: { medKnowledge: MedKnowledgeState }) => state.medKnowledge.error;
export const selectSearchHistory = (state: { medKnowledge: MedKnowledgeState }) => state.medKnowledge.searchHistory;
export const selectServiceHealth = (state: { medKnowledge: MedKnowledgeState }) => state.medKnowledge.serviceHealth;
export default medKnowledgeSlice.reducer;
