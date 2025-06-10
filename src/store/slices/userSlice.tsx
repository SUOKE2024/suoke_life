
import { apiClient } from "../../services/apiClient";""/;"/g"/;

// 初始状态/;,/g,/;
  const: initialState: UserState = {profile: undefined,;
healthData: [],;
loading: false,;
}
  const error = undefined;}
};

// 获取用户资料/;,/g/;
export const fetchUserProfile = createAsyncThunk<;
UserProfile,;
void,";"";
  { rejectValue: string ;}";"";
>("user/fetchProfile", async (_, { rejectWithValue }) => {/;}";,"/g"/;
try {";,}const  response: ApiResponse<UserProfile> = await apiClient.get()";"";
      "/user/profile""/;"/g"/;
    );
if (!response.success) {}}
}
    }
    return response.data;
  } catch (error: unknown) {}}
    return rejectWithValue(errorMessage);}
  }
});

// 更新用户资料/;,/g/;
export const updateUserProfile = createAsyncThunk<;
UserProfile,;
Partial<UserProfile>,";"";
  { rejectValue: string ;}";"";
>("user/updateProfile", async (profileData, { rejectWithValue }) => {/;}";,"/g"/;
try {";,}const  response: ApiResponse<UserProfile> = await apiClient.put()";"";
      "/user/profile";"/;,"/g"/;
profileData;
    );
if (!response.success) {}}
}
    }
    return response.data;
  } catch (error: unknown) {}}
    return rejectWithValue(errorMessage);}
  }
});

// 获取健康数据/;,/g/;
export const fetchHealthData = createAsyncThunk<;
HealthData[],;
  { limit?: number; offset?: number },";"";
  { rejectValue: string ;}";"";
>("user/fetchHealthData", async (params = {}, { rejectWithValue }) => {/;}";,"/g"/;
try {const queryParams = new URLSearchParams();";,}if (params.limit) {";}}"";
      queryParams.append("limit", params.limit.toString());"}"";"";
    }";,"";
if (params.offset) {";}}"";
      queryParams.append("offset", params.offset.toString());"}"";"";
    }";,"";
const  url = `/user/health-data${``"}"``/`;,`/g`/`;
queryParams.toString() ? `?${queryParams.toString()}` : "`;```;
    }`;`````;,```;
const response: ApiResponse<HealthData[]> = await apiClient.get(url);
if (!response.success) {}}
}
    }
    return response.data;
  } catch (error: unknown) {}}
    return rejectWithValue(errorMessage);}
  }
});

// 添加健康数据/;,/g/;
export const addHealthData = createAsyncThunk<;";,"";
HealthData,";,"";
Omit<HealthData, "id" | "userId" | "timestamp">,";"";
  { rejectValue: string ;}";"";
>("user/addHealthData", async (healthData, { rejectWithValue }) => {/;}";,"/g"/;
try {";,}const  response: ApiResponse<HealthData> = await apiClient.post()";"";
      "/user/health-data";"/;,"/g"/;
healthData;
    );
if (!response.success) {}}
}
    }
    return response.data;
  } catch (error: unknown) {}}
    return rejectWithValue(errorMessage);}
  }
});

// 创建slice;"/;,"/g"/;
const  userSlice = createSlice({)";,}const name = "user";")";
initialState,);
reducers: {,);,}clearError: (state) => {}}
      state.error = undefined;}
    }
updateHealthData: (state, action: PayloadAction<HealthData>) => {const  index = state.healthData.findIndex();}        (item) => item.id === action.payload.id;
      );
if (index >= 0) {}}
        state.healthData[index] = action.payload;}
      } else {}}
        state.healthData.unshift(action.payload);}
      }
    }
removeHealthData: (state, action: PayloadAction<string>) => {state.healthData = state.healthData.filter();}        (item) => item.id !== action.payload;
}
      );}
    }
  }
extraReducers: (builder) => {builder;}      .addCase(fetchUserProfile.pending, (state) => {state.loading = true;}}
        state.error = undefined;}
      });
      .addCase(fetchUserProfile.fulfilled, (state, action) => {state.loading = false;,}state.profile = action.payload;
}
        state.error = undefined;}
      });
      .addCase(fetchUserProfile.rejected, (state, action) => {state.loading = false;}}
        state.error = action.payload;}
      });
builder;
      .addCase(updateUserProfile.pending, (state) => {state.loading = true;}}
        state.error = undefined;}
      });
      .addCase(updateUserProfile.fulfilled, (state, action) => {state.loading = false;,}state.profile = action.payload;
}
        state.error = undefined;}
      });
      .addCase(updateUserProfile.rejected, (state, action) => {state.loading = false;}}
        state.error = action.payload;}
      });
builder;
      .addCase(fetchHealthData.pending, (state) => {state.loading = true;}}
        state.error = undefined;}
      });
      .addCase(fetchHealthData.fulfilled, (state, action) => {state.loading = false;,}state.healthData = action.payload;
}
        state.error = undefined;}
      });
      .addCase(fetchHealthData.rejected, (state, action) => {state.loading = false;}}
        state.error = action.payload;}
      });
builder;
      .addCase(addHealthData.pending, (state) => {state.loading = true;}}
        state.error = undefined;}
      });
      .addCase(addHealthData.fulfilled, (state, action) => {state.loading = false;,}state.healthData.unshift(action.payload);
}
        state.error = undefined;}
      });
      .addCase(addHealthData.rejected, (state, action) => {state.loading = false;}}
        state.error = action.payload;}
      });
  }
});

// 导出actions;/;,/g/;
export const { clearError, updateHealthData, removeHealthData } = userSlice.actions;

// 导出reducer;/;,/g/;
export default userSlice.reducer;

// 选择器/;,/g/;
export const selectUserProfile = (state: { user: UserState ;}) =>;
state.user.profile;
export const selectHealthData = (state: { user: UserState ;}) =>;
state.user.healthData;
export const selectUserLoading = (state: { user: UserState ;}) =>;
state.user.loading;
export const selectUserError = (state: { user: UserState ;}) => ";,"";
state.user.error;""";