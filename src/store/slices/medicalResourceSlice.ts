import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../index';

// 类型定义
export interface MedicalResource {
  id: string;
  type: 'hospital' | 'clinic' | 'pharmacy' | 'specialist' | 'doctor';
  name: string;
  location: {
    address: string;
    coordinates: { lat: number; lng: number };
    city: string;
    district: string;
  };
  services: string[];
  rating: number;
  availability: {
    isOpen: boolean;
    hours: string;
    nextAvailable: string;
    slots: TimeSlot[];
  };
  contact: {
    phone: string;
    website?: string;
    email?: string;
  };
  specialty?: string;
  experience?: number;
  consultationFee?: number;
  description?: string;
  images?: string[];
  reviews?: Review[];
}

export interface TimeSlot {
  id: string;
  startTime: string;
  endTime: string;
  available: boolean;
  price?: number;
}

export interface Review {
  id: string;
  userId: string;
  userName: string;
  rating: number;
  comment: string;
  date: string;
}

export interface Appointment {
  id: string;
  resourceId: string;
  resourceName: string;
  userId: string;
  serviceType: string;
  scheduledTime: string;
  duration: number;
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled';
  notes?: string;
  price?: number;
  location?: string;
  contact?: string;
}

export interface ResourceFilters {
  type?: string[];
  location?: {
    lat: number;
    lng: number;
    radius: number;
  };
  services?: string[];
  rating?: number;
  priceRange?: {
    min: number;
    max: number;
  };
  availability?: 'now' | 'today' | 'week';
  sortBy?: 'distance' | 'rating' | 'price' | 'availability';
}

export interface SearchQuery {
  keyword?: string;
  filters: ResourceFilters;
  page?: number;
  limit?: number;
}

interface MedicalResourceState {
  // 资源数据
  resources: MedicalResource[];
  searchResults: MedicalResource[];
  selectedResource: MedicalResource | null;
  nearbyResources: MedicalResource[];

  // 预约数据
  appointments: Appointment[];
  selectedAppointment: Appointment | null;

  // 搜索和筛选
  searchQuery: SearchQuery;
  searchHistory: string[];
  filters: ResourceFilters;

  // 加载状态
  loading: {
    search: boolean;
    details: boolean;
    booking: boolean;
    appointments: boolean;
    nearby: boolean;
  };

  // 错误状态
  errors: {
    search: string | null;
    details: string | null;
    booking: string | null;
    appointments: string | null;
    nearby: string | null;
  };

  // UI状态
  ui: {
    showFilters: boolean;
    showMap: boolean;
    viewMode: 'list' | 'grid' | 'map';
  };

  // 缓存和分页
  pagination: {
    currentPage: number;
    totalPages: number;
    totalItems: number;
    hasMore: boolean;
  };

  // 服务健康状态
  serviceHealth: {
    status: 'healthy' | 'unhealthy' | 'unknown';
    lastCheck: string | null;
    message?: string;
  };
}

const initialState: MedicalResourceState = {
  resources: [],
  searchResults: [],
  selectedResource: null,
  nearbyResources: [],
  appointments: [],
  selectedAppointment: null,
  searchQuery: {
    filters: {},
    page: 1,
    limit: 20
  },
  searchHistory: [],
  filters: {},
  loading: {
    search: false,
    details: false,
    booking: false,
    appointments: false,
    nearby: false
  },
  errors: {
    search: null,
    details: null,
    booking: null,
    appointments: null,
    nearby: null
  },
  ui: {
    showFilters: false,
    showMap: false,
    viewMode: 'list'
  },
  pagination: {
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    hasMore: false
  },
  serviceHealth: {
    status: 'unknown',
    lastCheck: null
  }
};

// 异步Actions
export const searchMedicalResources = createAsyncThunk(;
  'medicalResource/searchResources',
  async (query: SearchQuery, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/v1/medical-resources/search', {method: 'POST',headers: {'Content-Type': 'application/json';
        },body: JSON.stringify(query);
      });

      if (!response.ok) {
        throw new Error('搜索医疗资源失败');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '搜索失败');
    }
  }
);

export const getMedicalResourceDetails = createAsyncThunk(;
  'medicalResource/getDetails',
  async (resourceId: string, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/v1/medical-resources/${resourceId}`);

      if (!response.ok) {
        throw new Error('获取资源详情失败');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '获取详情失败');
    }
  }
);

export const bookAppointment = createAsyncThunk(;
  'medicalResource/bookAppointment',
  async (appointmentData: Omit<Appointment, 'id' | 'status'>, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/v1/medical-resources/appointments', {method: 'POST',headers: {'Content-Type': 'application/json';
        },body: JSON.stringify(appointmentData);
      });

      if (!response.ok) {
        throw new Error('预约失败');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '预约失败');
    }
  }
);

export const getUserAppointments = createAsyncThunk(;
  'medicalResource/getUserAppointments',
  async (userId: string, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/v1/medical-resources/appointments/user/${userId}`);

      if (!response.ok) {
        throw new Error('获取预约记录失败');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '获取预约记录失败');
    }
  }
);

export const getNearbyResources = createAsyncThunk(;
  'medicalResource/getNearbyResources',
  async (location: { lat: number; lng: number; radius?: number }, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/v1/medical-resources/nearby', {method: 'POST',headers: {'Content-Type': 'application/json';
        },body: JSON.stringify(location);
      });

      if (!response.ok) {
        throw new Error('获取附近资源失败');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '获取附近资源失败');
    }
  }
);

export const checkServiceHealth = createAsyncThunk(;
  'medicalResource/checkServiceHealth',
  async (_, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/v1/medical-resources/health');

      if (!response.ok) {
        throw new Error('服务健康检查失败');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '健康检查失败');
    }
  }
);

// Slice
const medicalResourceSlice = createSlice({name: 'medicalResource',initialState,reducers: {// 设置选中的资源;
    setSelectedResource: (state, action: PayloadAction<MedicalResource | null>) => {state.selectedResource = action.payload;
    },

    // 设置选中的预约
    setSelectedAppointment: (state, action: PayloadAction<Appointment | null>) => {
      state.selectedAppointment = action.payload;
    },

    // 更新搜索查询
    updateSearchQuery: (state, action: PayloadAction<Partial<SearchQuery>>) => {
      state.searchQuery = { ...state.searchQuery, ...action.payload };
    },

    // 更新筛选条件
    updateFilters: (state, action: PayloadAction<Partial<ResourceFilters>>) => {
      state.filters = { ...state.filters, ...action.payload };
      state.searchQuery.filters = { ...state.searchQuery.filters, ...action.payload };
    },

    // 添加搜索历史
    addToSearchHistory: (state, action: PayloadAction<string>) => {
      const keyword = action.payload.trim();
      if (keyword && !state.searchHistory.includes(keyword)) {
        state.searchHistory.unshift(keyword);
        // 保持最多10条历史记录
        if (state.searchHistory.length > 10) {
          state.searchHistory = state.searchHistory.slice(0, 10);
        }
      }
    },

    // 清除搜索历史
    clearSearchHistory: (state) => {
      state.searchHistory = [];
    },

    // 切换UI状态
    toggleFilters: (state) => {
      state.ui.showFilters = !state.ui.showFilters;
    },

    toggleMap: (state) => {
      state.ui.showMap = !state.ui.showMap;
    },

    setViewMode: (state, action: PayloadAction<'list' | 'grid' | 'map'>) => {
      state.ui.viewMode = action.payload;
    },

    // 清除错误
    clearError: (state, action: PayloadAction<keyof typeof state.errors>) => {
      state.errors[action.payload] = null;
    },

    // 清除所有错误
    clearAllErrors: (state) => {
      Object.keys(state.errors).forEach(key => {
        state.errors[key as keyof typeof state.errors] = null;
      });
    },

    // 重置状态
    resetState: (state) => {
      return { ...initialState, searchHistory: state.searchHistory };
    }
  },
  extraReducers: (builder) => {
    // 搜索医疗资源
    builder
      .addCase(searchMedicalResources.pending, (state) => {
        state.loading.search = true;
        state.errors.search = null;
      })
      .addCase(searchMedicalResources.fulfilled, (state, action) => {
        state.loading.search = false;
        state.searchResults = action.payload.data || [];
        state.pagination = {
          currentPage: action.payload.pagination?.currentPage || 1,
          totalPages: action.payload.pagination?.totalPages || 1,
          totalItems: action.payload.pagination?.totalItems || 0,
          hasMore: action.payload.pagination?.hasMore || false
        };
      })
      .addCase(searchMedicalResources.rejected, (state, action) => {
        state.loading.search = false;
        state.errors.search = action.payload as string;
        state.searchResults = [];
      });

    // 获取资源详情
    builder
      .addCase(getMedicalResourceDetails.pending, (state) => {
        state.loading.details = true;
        state.errors.details = null;
      })
      .addCase(getMedicalResourceDetails.fulfilled, (state, action) => {
        state.loading.details = false;
        state.selectedResource = action.payload.data;
      })
      .addCase(getMedicalResourceDetails.rejected, (state, action) => {
        state.loading.details = false;
        state.errors.details = action.payload as string;
      });

    // 预约
    builder
      .addCase(bookAppointment.pending, (state) => {
        state.loading.booking = true;
        state.errors.booking = null;
      })
      .addCase(bookAppointment.fulfilled, (state, action) => {
        state.loading.booking = false;
        state.appointments.unshift(action.payload.data);
      })
      .addCase(bookAppointment.rejected, (state, action) => {
        state.loading.booking = false;
        state.errors.booking = action.payload as string;
      });

    // 获取用户预约
    builder
      .addCase(getUserAppointments.pending, (state) => {
        state.loading.appointments = true;
        state.errors.appointments = null;
      })
      .addCase(getUserAppointments.fulfilled, (state, action) => {
        state.loading.appointments = false;
        state.appointments = action.payload.data || [];
      })
      .addCase(getUserAppointments.rejected, (state, action) => {
        state.loading.appointments = false;
        state.errors.appointments = action.payload as string;
      });

    // 获取附近资源
    builder
      .addCase(getNearbyResources.pending, (state) => {
        state.loading.nearby = true;
        state.errors.nearby = null;
      })
      .addCase(getNearbyResources.fulfilled, (state, action) => {
        state.loading.nearby = false;
        state.nearbyResources = action.payload.data || [];
      })
      .addCase(getNearbyResources.rejected, (state, action) => {
        state.loading.nearby = false;
        state.errors.nearby = action.payload as string;
      });

    // 服务健康检查
    builder
      .addCase(checkServiceHealth.fulfilled, (state, action) => {
        state.serviceHealth = {
          status: action.payload.status === 'healthy' ? 'healthy' : 'unhealthy',
          lastCheck: new Date().toISOString(),
          message: action.payload.message
        };
      })
      .addCase(checkServiceHealth.rejected, (state, action) => {
        state.serviceHealth = {
          status: 'unhealthy',
          lastCheck: new Date().toISOString(),
          message: action.payload as string
        };
      });
  }
});

// Actions
export const {
  setSelectedResource,
  setSelectedAppointment,
  updateSearchQuery,
  updateFilters,
  addToSearchHistory,
  clearSearchHistory,
  toggleFilters,
  toggleMap,
  setViewMode,
  clearError,
  clearAllErrors,
  resetState
} = medicalResourceSlice.actions;

// Selectors
export const selectMedicalResources = (state: RootState) => state.medicalResource.resources;
export const selectSearchResults = (state: RootState) => state.medicalResource.searchResults;
export const selectSelectedResource = (state: RootState) => state.medicalResource.selectedResource;
export const selectNearbyResources = (state: RootState) => state.medicalResource.nearbyResources;
export const selectAppointments = (state: RootState) => state.medicalResource.appointments;
export const selectSelectedAppointment = (state: RootState) => state.medicalResource.selectedAppointment;
export const selectSearchQuery = (state: RootState) => state.medicalResource.searchQuery;
export const selectFilters = (state: RootState) => state.medicalResource.filters;
export const selectSearchHistory = (state: RootState) => state.medicalResource.searchHistory;
export const selectLoading = (state: RootState) => state.medicalResource.loading;
export const selectErrors = (state: RootState) => state.medicalResource.errors;
export const selectUI = (state: RootState) => state.medicalResource.ui;
export const selectPagination = (state: RootState) => state.medicalResource.pagination;
export const selectServiceHealth = (state: RootState) => state.medicalResource.serviceHealth;

export default medicalResourceSlice.reducer; 
