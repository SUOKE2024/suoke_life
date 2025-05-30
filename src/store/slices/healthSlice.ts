import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { apiClient } from "../../services/apiClient";


  HealthState,
  HealthData,
  HealthSummary,
  HealthDataType,
  ApiResponse,
} from "../../types";

// 初始状态
const initialState: HealthState = {
  data: [],
  summary: {
    overallScore: 0,
    constitution: "balanced",
    recommendations: [],
    trends: {
      heart_rate: "stable",
      blood_pressure: "stable",
      body_temperature: "stable",
      sleep_quality: "stable",
      stress_level: "stable",
      mood: "stable",
      exercise: "stable",
      nutrition: "stable",
    },
  },
  loading: false,
  error: undefined,
};

// 异步thunk actions
export const fetchHealthSummary = createAsyncThunk<
  HealthSummary,
  void,
  { rejectValue: string }
>("health/fetchSummary", async (_, { rejectWithValue }) => {
  try {
    const response: ApiResponse<HealthSummary> = await apiClient.get(
      "/health/summary"
    );

    if (!response.success) {
      throw new Error(response.error?.message || "获取健康概况失败");
    }

    return response.data!;
  } catch (error: any) {
    return rejectWithValue(error.message || "获取健康概况失败");
  }
});

export const fetchHealthTrends = createAsyncThunk<
  HealthData[],
  { type?: HealthDataType; days?: number },
  { rejectValue: string }
>("health/fetchTrends", async (params, { rejectWithValue }) => {
  try {
    const queryParams = new URLSearchParams();
    if (params.type) {
      queryParams.append('type', params.type);
    }
    if (params.days) {
      queryParams.append('days', params.days.toString());
    }

    const response: ApiResponse<HealthData[]> = await apiClient.get(
      `/health/trends?${queryParams.toString()}`
    );

    if (!response.success) {
      throw new Error(response.error?.message || "获取健康趋势失败");
    }

    return response.data!;
  } catch (error: any) {
    return rejectWithValue(error.message || "获取健康趋势失败");
  }
});

export const syncHealthData = createAsyncThunk<
  HealthData[],
  void,
  { rejectValue: string }
>("health/syncData", async (_, { rejectWithValue }) => {
  try {
    const response: ApiResponse<HealthData[]> = await apiClient.post(
      "/health/sync"
    );

    if (!response.success) {
      throw new Error(response.error?.message || "同步健康数据失败");
    }

    return response.data!;
  } catch (error: any) {
    return rejectWithValue(error.message || "同步健康数据失败");
  }
});

export const analyzeHealthData = createAsyncThunk<
  HealthSummary,
  { dataIds: string[] },
  { rejectValue: string }
>("health/analyzeData", async ({ dataIds }, { rejectWithValue }) => {
  try {
    const response: ApiResponse<HealthSummary> = await apiClient.post(
      "/health/analyze",
      {
        dataIds,
      }
    );

    if (!response.success) {
      throw new Error(response.error?.message || "分析健康数据失败");
    }

    return response.data!;
  } catch (error: any) {
    return rejectWithValue(error.message || "分析健康数据失败");
  }
});

export const generateHealthReport = createAsyncThunk<
  { reportUrl: string; reportData: any },
  { startDate: string; endDate: string },
  { rejectValue: string }
>(
  "health/generateReport",
  async ({ startDate, endDate }, { rejectWithValue }) => {
    try {
      const response: ApiResponse<{ reportUrl: string; reportData: any }> =
        await apiClient.post("/health/report", { startDate, endDate });

      if (!response.success) {
        throw new Error(response.error?.message || "生成健康报告失败");
      }

      return response.data!;
    } catch (error: any) {
      return rejectWithValue(error.message || "生成健康报告失败");
    }
  }
);

// 创建slice
const healthSlice = createSlice({
  name: "health",
  initialState,
  reducers: {
    addHealthDataLocal: (state, action: PayloadAction<HealthData>) => {
      state.data.unshift(action.payload);
    },
    updateHealthDataLocal: (state, action: PayloadAction<HealthData>) => {
      const index = state.data.findIndex(
        (item) => item.id === action.payload.id
      );
      if (index >= 0) {
        state.data[index] = action.payload;
      }
    },
    removeHealthDataLocal: (state, action: PayloadAction<string>) => {
      state.data = state.data.filter((item) => item.id !== action.payload);
    },
    updateSummary: (state, action: PayloadAction<Partial<HealthSummary>>) => {
      state.summary = { ...state.summary, ...action.payload };
    },
    clearError: (state) => {
      state.error = undefined;
    },
    setHealthDataFilter: (
      _state,
      _action: PayloadAction<{
        type?: HealthDataType;
        dateRange?: { start: string; end: string };
      }>
    ) => {
      // 这里可以添加过滤逻辑
      // 暂时只是存储过滤器状态，实际过滤在组件中处理
    },
  },
  extraReducers: (builder) => {
    // 获取健康概况
    builder
      .addCase(fetchHealthSummary.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(fetchHealthSummary.fulfilled, (state, action) => {
        state.loading = false;
        state.summary = action.payload;
        state.error = undefined;
      })
      .addCase(fetchHealthSummary.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    // 获取健康趋势
    builder
      .addCase(fetchHealthTrends.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(fetchHealthTrends.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
        state.error = undefined;
      })
      .addCase(fetchHealthTrends.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    // 同步健康数据
    builder
      .addCase(syncHealthData.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(syncHealthData.fulfilled, (state, action) => {
        state.loading = false;
        // 合并新数据，避免重复
        const existingIds = new Set(state.data.map((item) => item.id));
        const newData = action.payload.filter(
          (item) => !existingIds.has(item.id)
        );
        state.data = [...newData, ...state.data];
        state.error = undefined;
      })
      .addCase(syncHealthData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    // 分析健康数据
    builder
      .addCase(analyzeHealthData.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(analyzeHealthData.fulfilled, (state, action) => {
        state.loading = false;
        state.summary = action.payload;
        state.error = undefined;
      })
      .addCase(analyzeHealthData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    // 生成健康报告
    builder
      .addCase(generateHealthReport.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(generateHealthReport.fulfilled, (state, _action) => {
        state.loading = false;
        state.error = undefined;
      })
      .addCase(generateHealthReport.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

// 导出actions
export const {
  addHealthDataLocal,
  updateHealthDataLocal,
  removeHealthDataLocal,
  updateSummary,
  clearError,
  setHealthDataFilter,
} = healthSlice.actions;

// 选择器
export const selectHealth = (state: { health: HealthState }) => state.health;
export const selectHealthData = (state: { health: HealthState }) =>
  state.health.data;
export const selectHealthSummary = (state: { health: HealthState }) =>
  state.health.summary;
export const selectHealthLoading = (state: { health: HealthState }) =>
  state.health.loading;
export const selectHealthError = (state: { health: HealthState }) =>
  state.health.error;

// 获取特定类型的健康数据
export const selectHealthDataByType =
  (type: HealthDataType) => (state: { health: HealthState }) =>
    state.health.data.filter((item) => item.type === type);

// 获取最近的健康数据
export const selectRecentHealthData =
  (days: number = 7) =>
  (state: { health: HealthState }) => {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    return state.health.data
      .filter((item) => new Date(item.timestamp) >= cutoffDate)
      .sort(
        (a, b) =>
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      );
  };

// 导出reducer
export default healthSlice.reducer;
