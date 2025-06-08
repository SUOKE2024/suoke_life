import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { benchmarkService } from '../../services';
  BenchmarkTask,
  BenchmarkResult,
  BenchmarkConfig,
  HealthStatus,
  Plugin;
} from '../../services';
// 状态接口
interface BenchmarkState {
  // 任务相关
  tasks: BenchmarkTask[];
  currentTask: BenchmarkTask | null;
  currentResult: BenchmarkResult | null;
  // 服务状态
  healthStatus: HealthStatus | null;
  plugins: Plugin[];
  // UI状态
  loading: {;
  tasks: boolean;
    result: boolean;
  health: boolean;
    plugins: boolean;
  submit: boolean;
};
  // 错误状态
  error: {,
  tasks: string | null;
    result: string | null,
  health: string | null;
    plugins: string | null,
  submit: string | null;
  };
  // 过滤和排序
  filters: {,
  status: string | null;
    modelId: string | null,
  benchmarkId: string | null;
  };
  // 实时状态
  streaming: {,
  isConnected: boolean;
    connectionState: string,
  lastEvent: any | null;
  };
}
// 初始状态
const initialState: BenchmarkState = {,
  tasks: [],
  currentTask: null,
  currentResult: null,
  healthStatus: null,
  plugins: [],
  loading: {,
  tasks: false,
    result: false,
    health: false,
    plugins: false,
    submit: false;
  },
  error: {,
  tasks: null,
    result: null,
    health: null,
    plugins: null,
    submit: null;
  },
  filters: {,
  status: null,
    modelId: null,
    benchmarkId: null;
  },
  streaming: {,
  isConnected: false,
    connectionState: 'CLOSED',
    lastEvent: null;
  }
};
// 异步操作
export const fetchBenchmarkTasks = createAsyncThunk(;
  'benchmark/fetchTasks',
  async (status?: string) => {
    const tasks = await benchmarkService.listBenchmarks(status);
    return tasks;
  }
);
export const fetchBenchmarkResult = createAsyncThunk(;
  'benchmark/fetchResult',
  async (taskId: string) => {
    const result = await benchmarkService.getBenchmarkResult(taskId);
    return result;
  }
);
export const fetchHealthStatus = createAsyncThunk(;
  'benchmark/fetchHealth',
  async () => {
    const status = await benchmarkService.getHealthStatus();
    return status;
  }
);
export const fetchPlugins = createAsyncThunk(;
  'benchmark/fetchPlugins',
  async () => {
    const plugins = await benchmarkService.listPlugins();
    return plugins;
  }
);
export const submitBenchmark = createAsyncThunk(;
  'benchmark/submit',
  async (config: BenchmarkConfig) => {
    const taskId = await benchmarkService.submitBenchmark(config);
    return taskId;
  }
);
export const submitPluginBenchmark = createAsyncThunk(;
  'benchmark/submitPlugin',
  async ({ pluginName, config }: { pluginName: string; config: any }) => {
    const taskId = await benchmarkService.runPluginBenchmark(pluginName, config);
    return taskId;
  }
);
export const cancelBenchmark = createAsyncThunk(;
  'benchmark/cancel',
  async (taskId: string) => {
    await benchmarkService.cancelBenchmark(taskId);
    return taskId;
  }
);
export const generateReport = createAsyncThunk(;
  'benchmark/generateReport',
  async ({ taskId, format }: { taskId: string; format: 'html' | 'json' }) => {
    const reportUrl = await benchmarkService.generateReport(taskId, format);
    return { taskId, reportUrl };
  }
);
// Slice定义
const benchmarkSlice = createSlice({name: 'benchmark',initialState,reducers: {// 设置当前任务,
  setCurrentTask: (state, action: PayloadAction<BenchmarkTask | null>) => {state.currentTask = action.payload;
    },
    // 设置当前结果
    setCurrentResult: (state, action: PayloadAction<BenchmarkResult | null>) => {
      state.currentResult = action.payload;
    },
    // 更新任务状态
    updateTaskStatus: (state, action: PayloadAction<{ taskId: string; status: string; progress?: number }>) => {
      const { taskId, status, progress } = action.payload;
      const taskIndex = state.tasks.findIndex(task => task.task_id === taskId);
      if (taskIndex !== -1) {
        state.tasks[taskIndex].status = status as any;
        if (progress !== undefined) {
          state.tasks[taskIndex].progress = progress;
        }
      }
      // 更新当前任务
      if (state.currentTask && state.currentTask.task_id === taskId) {
        state.currentTask.status = status as any;
        if (progress !== undefined) {
          state.currentTask.progress = progress;
        }
      }
    },
    // 添加新任务
    addTask: (state, action: PayloadAction<BenchmarkTask>) => {
      state.tasks.unshift(action.payload);
    },
    // 移除任务
    removeTask: (state, action: PayloadAction<string>) => {
      state.tasks = state.tasks.filter(task => task.task_id !== action.payload);
      if (state.currentTask && state.currentTask.task_id === action.payload) {
        state.currentTask = null;
      }
    },
    // 设置过滤器
    setFilters: (state, action: PayloadAction<Partial<BenchmarkState['filters']>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    // 清除过滤器
    clearFilters: (state) => {
      state.filters = {
        status: null,
        modelId: null,
        benchmarkId: null;
      };
    },
    // 更新流式状态
    updateStreamingStatus: (state, action: PayloadAction<{
      isConnected?: boolean;
      connectionState?: string;
      lastEvent?: any;
    }>) => {
      state.streaming = { ...state.streaming, ...action.payload };
    },
    // 清除错误
    clearError: (state, action: PayloadAction<keyof BenchmarkState['error']>) => {
      state.error[action.payload] = null;
    },
    // 清除所有错误
    clearAllErrors: (state) => {
      Object.keys(state.error).forEach(key => {
        state.error[key as keyof BenchmarkState['error']] = null;
      });
    },
    // 重置状态
    resetState: () => initialState;
  },
  extraReducers: (builder) => {
    // 获取任务列表
    builder;
      .addCase(fetchBenchmarkTasks.pending, (state) => {
        state.loading.tasks = true;
        state.error.tasks = null;
      })
      .addCase(fetchBenchmarkTasks.fulfilled, (state, action) => {
        state.loading.tasks = false;
        state.tasks = action.payload;
      })
      .addCase(fetchBenchmarkTasks.rejected, (state, action) => {
        state.loading.tasks = false;
        state.error.tasks = action.error.message || '获取任务列表失败';
      });
    // 获取结果详情
    builder;
      .addCase(fetchBenchmarkResult.pending, (state) => {
        state.loading.result = true;
        state.error.result = null;
      })
      .addCase(fetchBenchmarkResult.fulfilled, (state, action) => {
        state.loading.result = false;
        state.currentResult = action.payload;
      })
      .addCase(fetchBenchmarkResult.rejected, (state, action) => {
        state.loading.result = false;
        state.error.result = action.error.message || '获取结果失败';
      });
    // 获取健康状态
    builder;
      .addCase(fetchHealthStatus.pending, (state) => {
        state.loading.health = true;
        state.error.health = null;
      })
      .addCase(fetchHealthStatus.fulfilled, (state, action) => {
        state.loading.health = false;
        state.healthStatus = action.payload;
      })
      .addCase(fetchHealthStatus.rejected, (state, action) => {
        state.loading.health = false;
        state.error.health = action.error.message || '获取健康状态失败';
      });
    // 获取插件列表
    builder;
      .addCase(fetchPlugins.pending, (state) => {
        state.loading.plugins = true;
        state.error.plugins = null;
      })
      .addCase(fetchPlugins.fulfilled, (state, action) => {
        state.loading.plugins = false;
        state.plugins = action.payload;
      })
      .addCase(fetchPlugins.rejected, (state, action) => {
        state.loading.plugins = false;
        state.error.plugins = action.error.message || '获取插件列表失败';
      });
    // 提交基准测试
    builder;
      .addCase(submitBenchmark.pending, (state) => {
        state.loading.submit = true;
        state.error.submit = null;
      })
      .addCase(submitBenchmark.fulfilled, (state, action) => {
        state.loading.submit = false;
        // 任务ID已返回，可以用于后续操作
      })
      .addCase(submitBenchmark.rejected, (state, action) => {
        state.loading.submit = false;
        state.error.submit = action.error.message || '提交基准测试失败';
      });
    // 提交插件基准测试
    builder;
      .addCase(submitPluginBenchmark.pending, (state) => {
        state.loading.submit = true;
        state.error.submit = null;
      })
      .addCase(submitPluginBenchmark.fulfilled, (state, action) => {
        state.loading.submit = false;
      })
      .addCase(submitPluginBenchmark.rejected, (state, action) => {
        state.loading.submit = false;
        state.error.submit = action.error.message || '提交插件基准测试失败';
      });
    // 取消基准测试
    builder;
      .addCase(cancelBenchmark.fulfilled, (state, action) => {
        const taskId = action.payload;
        const taskIndex = state.tasks.findIndex(task => task.task_id === taskId);
        if (taskIndex !== -1) {
          state.tasks[taskIndex].status = 'failed';
        }
      });
  }
});
// 导出actions;
export const {
  setCurrentTask,
  setCurrentResult,
  updateTaskStatus,
  addTask,
  removeTask,
  setFilters,
  clearFilters,
  updateStreamingStatus,
  clearError,
  clearAllErrors,
  resetState;
} = benchmarkSlice.actions;
// 选择器
export const selectBenchmarkTasks = (state: { benchmark: BenchmarkState }) => state.benchmark.tasks;
export const selectCurrentTask = (state: { benchmark: BenchmarkState }) => state.benchmark.currentTask;
export const selectCurrentResult = (state: { benchmark: BenchmarkState }) => state.benchmark.currentResult;
export const selectHealthStatus = (state: { benchmark: BenchmarkState }) => state.benchmark.healthStatus;
export const selectPlugins = (state: { benchmark: BenchmarkState }) => state.benchmark.plugins;
export const selectBenchmarkLoading = (state: { benchmark: BenchmarkState }) => state.benchmark.loading;
export const selectBenchmarkError = (state: { benchmark: BenchmarkState }) => state.benchmark.error;
export const selectBenchmarkFilters = (state: { benchmark: BenchmarkState }) => state.benchmark.filters;
export const selectStreamingStatus = (state: { benchmark: BenchmarkState }) => state.benchmark.streaming;
// 过滤后的任务列表
export const selectFilteredTasks = (state: { benchmark: BenchmarkState }) => {const { tasks, filters } = state.benchmark;
  return tasks.filter(task => {if (filters.status && task.status !== filters.status) return false;
    if (filters.modelId && task.model_id !== filters.modelId) return false;
    if (filters.benchmarkId && task.benchmark_id !== filters.benchmarkId) return false;
    return true;
  });
};
// 任务统计
export const selectTaskStats = (state: { benchmark: BenchmarkState }) => {const tasks = state.benchmark.tasks;
  return {total: tasks.length,pending: tasks.filter(t => t.status === 'pending').length,running: tasks.filter(t => t.status === 'running').length,completed: tasks.filter(t => t.status === 'completed').length,failed: tasks.filter(t => t.status === 'failed').length;
  };
};
export default benchmarkSlice.reducer;