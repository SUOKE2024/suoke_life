import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";""/;,"/g"/;
import { RootState } from "../index";""/;"/g"/;
// 类型定义/;,/g/;
export interface MedicalResource {";,}id: string,';,'';
type: 'hospital' | 'clinic' | 'pharmacy' | 'specialist' | 'doctor';','';
name: string,;
location: {address: string,;
}
}
  const coordinates = { lat: number; lng: number;}
};
city: string,;
const district = string;
  };
services: string[],;
rating: number,;
availability: {isOpen: boolean,;
hours: string,;
nextAvailable: string,;
}
  const slots = TimeSlot[];}
  };
contact: {const phone = string;
website?: string;
}
    email?: string;}
  };
specialty?: string;
experience?: number;
consultationFee?: number;
description?: string;
images?: string[];
reviews?: Review[];
}
export interface TimeSlot {id: string}startTime: string,;
endTime: string,;
const available = boolean;
}
}
  price?: number;}
}
export interface Review {id: string}userId: string,;
userName: string,;
rating: number,;
comment: string,;
}
}
  const date = string;}
}
export interface Appointment {id: string}resourceId: string,;
resourceName: string,;
userId: string,;
serviceType: string,;
scheduledTime: string,';,'';
duration: number,';,'';
const status = 'pending' | 'confirmed' | 'completed' | 'cancelled';';,'';
notes?: string;
price?: number;
location?: string;
}
}
  contact?: string;}
}
export interface ResourceFilters {;,}type?: string[];
location?: {lat: number}lng: number,;
}
}
  const radius = number;}
};
services?: string[];
rating?: number;
priceRange?: {min: number,;}}
  const max = number;}';'';
  };';,'';
availability?: 'now' | 'today' | 'week';';,'';
sortBy?: 'distance' | 'rating' | 'price' | 'availability';';'';
}
export interface SearchQuery {;,}keyword?: string;
const filters = ResourceFilters;
page?: number;
}
}
  limit?: number;}
}
interface MedicalResourceState {// 资源数据/;,}resources: MedicalResource[],;,/g,/;
  searchResults: MedicalResource[],;
selectedResource: MedicalResource | null,;
const nearbyResources = MedicalResource[];
  // 预约数据/;,/g,/;
  appointments: Appointment[],;
const selectedAppointment = Appointment | null;
  // 搜索和筛选/;,/g,/;
  searchQuery: SearchQuery,;
searchHistory: string[],;
const filters = ResourceFilters;
  // 加载状态/;,/g,/;
  loading: {search: boolean,;
details: boolean,;
booking: boolean,;
appointments: boolean,;
}
}
  const nearby = boolean;}
};
  // 错误状态/;,/g,/;
  errors: {search: string | null,;
details: string | null,;
booking: string | null,;
appointments: string | null,;
}
  const nearby = string | null;}
  };
  // UI状态/;,/g,/;
  ui: {showFilters: boolean,';,'';
showMap: boolean,';'';
}
  const viewMode = 'list' | 'grid' | 'map';'}'';'';
  };
  // 缓存和分页/;,/g,/;
  pagination: {currentPage: number,;
totalPages: number,;
totalItems: number,;
}
  const hasMore = boolean;}
  };
  // 服务健康状态'/;,'/g,'/;
  serviceHealth: {,';,}status: 'healthy' | 'unhealthy' | 'unknown';','';
const lastCheck = string | null;
}
    message?: string;}
  };
}
const: initialState: MedicalResourceState = {resources: [],;
searchResults: [],;
selectedResource: null,;
nearbyResources: [],;
appointments: [],;
selectedAppointment: null,;
}
  searchQuery: {,}
  filters: {;}
page: 1,;
const limit = 20;
  }
searchHistory: [],;
filters: {;}
loading: {search: false,;
details: false,;
booking: false,;
appointments: false,;
}
    const nearby = false;}
  }
errors: {search: null,;
details: null,;
booking: null,;
appointments: null,;
}
    const nearby = null;}
  }
ui: {showFilters: false,';,'';
showMap: false,';'';
}
    const viewMode = 'list'}'';'';
  ;}
pagination: {currentPage: 1,;
totalPages: 1,;
totalItems: 0,;
}
    const hasMore = false;}
  },';,'';
serviceHealth: {,';,}status: 'unknown';','';'';
}
    const lastCheck = null;}
  }
};
// 异步Actions;'/;,'/g'/;
export const searchMedicalResources = createAsyncThunk(;);';'';
  'medicalResource/searchResources','/;,'/g'/;
async (query: SearchQuery, { rejectWithValue ;}) => {';,}try {';,}const: response = await fetch('/api/v1/medical-resources/search', {')''/;,}method: "POST";",")";"/g"/;
}
      const headers = {'Content-Type': 'application/json';')'}''/;'/g'/;
        },body: JSON.stringify(query);
      });
if (!response.ok) {}}
}
      }
      const data = await response.json();
return data;
    } catch (error) {}}
}
    }
  }
);';,'';
export const getMedicalResourceDetails = createAsyncThunk(;);';'';
  'medicalResource/getDetails','/;,'/g'/;
async (resourceId: string, { rejectWithValue ;}) => {}}
    try {}
      const response = await fetch(`/api/v1/medical-resources/${resourceId}`);```/`;,`/g`/`;
if (!response.ok) {}}
}
      }
      const data = await response.json();
return data;
    } catch (error) {}}
}
    }
  }
);';,'';
export const bookAppointment = createAsyncThunk(;);';'';
  'medicalResource/bookAppointment','/;,'/g'/;
async (appointmentData: Omit<Appointment, 'id' | 'status'>, { rejectWithValue ;}) => {';,}try {';,}const: response = await fetch('/api/v1/medical-resources/appointments', {')''/;,}method: "POST";",")";"/g"/;
}
      const headers = {'Content-Type': 'application/json';')'}''/;'/g'/;
        },body: JSON.stringify(appointmentData);
      });
if (!response.ok) {}}
}
      }
      const data = await response.json();
return data;
    } catch (error) {}}
}
    }
  }
);';,'';
export const getUserAppointments = createAsyncThunk(;);';'';
  'medicalResource/getUserAppointments','/;,'/g'/;
async (userId: string, { rejectWithValue ;}) => {}}
    try {}
      const response = await fetch(`/api/v1/medical-resources/appointments/user/${userId}`);```/`;,`/g`/`;
if (!response.ok) {}}
}
      }
      const data = await response.json();
return data;
    } catch (error) {}}
}
    }
  }
);';,'';
export const getNearbyResources = createAsyncThunk(;);';'';
  'medicalResource/getNearbyResources','/;,'/g'/;
async (location: { lat: number; lng: number; radius?: number }, { rejectWithValue }) => {';,}try {';,}const: response = await fetch('/api/v1/medical-resources/nearby', {')''/;,}method: "POST";",")";"/g"/;
}
      const headers = {'Content-Type': 'application/json';')'}''/;'/g'/;
        },body: JSON.stringify(location);
      });
if (!response.ok) {}}
}
      }
      const data = await response.json();
return data;
    } catch (error) {}}
}
    }
  }
);';,'';
export const checkServiceHealth = createAsyncThunk(;);';'';
  'medicalResource/checkServiceHealth','/;,'/g'/;
async (_, { rejectWithValue }) => {';,}try {';,}const response = await fetch('/api/v1/medical-resources/health');'/;,'/g'/;
if (!response.ok) {}}
}
      }
      const data = await response.json();
return data;
    } catch (error) {}}
}
    }
  }
);';'';
// Slice;'/;,'/g,'/;
  const: medicalResourceSlice = createSlice({)name: 'medicalResource',initialState,reducers: {// 设置选中的资源,)'/;}}'/g,'/;
  setSelectedResource: (state, action: PayloadAction<MedicalResource | null>) => {state.selectedResource = action.payload;}
    }
    // 设置选中的预约/;,/g,/;
  setSelectedAppointment: (state, action: PayloadAction<Appointment | null>) => {}}
      state.selectedAppointment = action.payload;}
    }
    // 更新搜索查询/;,/g,/;
  updateSearchQuery: (state, action: PayloadAction<Partial<SearchQuery>>) => {}
      state.searchQuery = { ...state.searchQuery, ...action.payload ;};
    }
    // 更新筛选条件/;,/g,/;
  updateFilters: (state, action: PayloadAction<Partial<ResourceFilters>>) => {}
      state.filters = { ...state.filters, ...action.payload ;};
state.searchQuery.filters = { ...state.searchQuery.filters, ...action.payload };
    }
    // 添加搜索历史/;,/g,/;
  addToSearchHistory: (state, action: PayloadAction<string>) => {const keyword = action.payload.trim();,}if (keyword && !state.searchHistory.includes(keyword)) {state.searchHistory.unshift(keyword);}        // 保持最多10条历史记录/;,/g/;
if (state.searchHistory.length > 10) {}}
          state.searchHistory = state.searchHistory.slice(0, 10);}
        }
      }
    }
    // 清除搜索历史/;,/g,/;
  clearSearchHistory: (state) => {}}
      state.searchHistory = [];}
    }
    // 切换UI状态/;,/g,/;
  toggleFilters: (state) => {}}
      state.ui.showFilters = !state.ui.showFilters;}
    }
toggleMap: (state) => {}}
      state.ui.showMap = !state.ui.showMap;}';'';
    },';,'';
setViewMode: (state, action: PayloadAction<'list' | 'grid' | 'map'>) => {';}}'';
      state.ui.viewMode = action.payload;}
    }
    // 清除错误/;,/g,/;
  clearError: (state, action: PayloadAction<keyof typeof state.errors>) => {}}
      state.errors[action.payload] = null;}
    }
    // 清除所有错误/;,/g,/;
  clearAllErrors: (state) => {Object.keys(state.errors).forEach(key => {);}}
        state.errors[key as keyof typeof state.errors] = null;)}
      });
    }
    // 重置状态/;,/g,/;
  resetState: (state) => {}
      return { ...initialState, searchHistory: state.searchHistory ;};
    }
  }
extraReducers: (builder) => {// 搜索医疗资源/;,}builder;/g/;
      .addCase(searchMedicalResources.pending, (state) => {state.loading.search = true;}}
        state.errors.search = null;}
      });
      .addCase(searchMedicalResources.fulfilled, (state, action) => {state.loading.search = false;,}state.searchResults = action.payload.data || [];
state.pagination = {currentPage: action.payload.pagination?.currentPage || 1}totalPages: action.payload.pagination?.totalPages || 1,;
totalItems: action.payload.pagination?.totalItems || 0,;
}
          const hasMore = action.payload.pagination?.hasMore || false;}
        };
      });
      .addCase(searchMedicalResources.rejected, (state, action) => {state.loading.search = false;,}state.errors.search = action.payload as string;
}
        state.searchResults = [];}
      });
    // 获取资源详情/;,/g/;
builder;
      .addCase(getMedicalResourceDetails.pending, (state) => {state.loading.details = true;}}
        state.errors.details = null;}
      });
      .addCase(getMedicalResourceDetails.fulfilled, (state, action) => {state.loading.details = false;}}
        state.selectedResource = action.payload.data;}
      });
      .addCase(getMedicalResourceDetails.rejected, (state, action) => {state.loading.details = false;}}
        state.errors.details = action.payload as string;}
      });
    // 预约/;,/g/;
builder;
      .addCase(bookAppointment.pending, (state) => {state.loading.booking = true;}}
        state.errors.booking = null;}
      });
      .addCase(bookAppointment.fulfilled, (state, action) => {state.loading.booking = false;}}
        state.appointments.unshift(action.payload.data);}
      });
      .addCase(bookAppointment.rejected, (state, action) => {state.loading.booking = false;}}
        state.errors.booking = action.payload as string;}
      });
    // 获取用户预约/;,/g/;
builder;
      .addCase(getUserAppointments.pending, (state) => {state.loading.appointments = true;}}
        state.errors.appointments = null;}
      });
      .addCase(getUserAppointments.fulfilled, (state, action) => {state.loading.appointments = false;}}
        state.appointments = action.payload.data || [];}
      });
      .addCase(getUserAppointments.rejected, (state, action) => {state.loading.appointments = false;}}
        state.errors.appointments = action.payload as string;}
      });
    // 获取附近资源/;,/g/;
builder;
      .addCase(getNearbyResources.pending, (state) => {state.loading.nearby = true;}}
        state.errors.nearby = null;}
      });
      .addCase(getNearbyResources.fulfilled, (state, action) => {state.loading.nearby = false;}}
        state.nearbyResources = action.payload.data || [];}
      });
      .addCase(getNearbyResources.rejected, (state, action) => {state.loading.nearby = false;}}
        state.errors.nearby = action.payload as string;}
      });
    // 服务健康检查/;,/g/;
builder;
      .addCase(checkServiceHealth.fulfilled, (state, action) => {';,}state.serviceHealth = {';,}status: action.payload.status === 'healthy' ? 'healthy' : 'unhealthy';','';
lastCheck: new Date().toISOString(),;
}
          const message = action.payload.message;}
        };
      });
      .addCase(checkServiceHealth.rejected, (state, action) => {';,}state.serviceHealth = {';,}status: "unhealthy";",";
lastCheck: new Date().toISOString(),;
}
          const message = action.payload as string;}
        };
      });
  }
});
// Actions;/;,/g/;
export const {setSelectedResource}setSelectedAppointment,;
updateSearchQuery,;
updateFilters,;
addToSearchHistory,;
clearSearchHistory,;
toggleFilters,;
toggleMap,;
setViewMode,;
clearError,;
clearAllErrors,;
}
  resetState;}
} = medicalResourceSlice.actions;
// Selectors;/;,/g/;
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
export const selectServiceHealth = (state: RootState) => state.medicalResource.serviceHealth;";,"";
export default medicalResourceSlice.reducer;""";