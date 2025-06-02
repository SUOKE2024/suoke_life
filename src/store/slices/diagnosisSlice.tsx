import React from 'react';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor';
import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit"/import { apiClient } from "../../services/apiClient";/;
  DiagnosisState,
  DiagnosisSession,
  DiagnosisData,
  DiagnosisResult,
  DiagnosisType,
{ ApiResponse } from "../../types"//  *  import { API_CONFIG } from ".. *// .. * constants *//config";/;
// 初始状态 * const initialState: DiagnosisState = {, */
  currentSession: undefined,
  sessions:  [],
  results:  [],
  loading: false,
  error: undefined,
};
// 异步thunk actions * export const startDiagnosisSession = createAsyncThun;k;<; */
  DiagnosisSession,
  void,
  { rejectValue: string}
>("diagnosis/startSession", async (_, { rejectWithValue }) => {/  try {
    const response: ApiResponse<DiagnosisSession /> = await apiClient.post(/      "/diagnosis/session/start";/    ;)
    if (!response.success) {
      throw new Error(response.error?.message || "开始诊断会话失败;";);
    }
    return response.dat;a;!
  } catch (error: unknown) {
    return rejectWithValue(error.message || "开始诊断会话失败;";);
  }
});
export const submitDiagnosisData = createAsyncThun;k;<;
  DiagnosisData,
  { sessionId: string, type: DiagnosisType, data: unknown},
  { rejectValue: string}
>(
  "diagnosis/submitData",/  async ({ sessionId, type, data }, { rejectWithValue }) => {
    try {
      // 使用apiClient发送诊断数据 *       const response: ApiResponse<DiagnosisData  *// > = await apiClient.post( * ` *//diagnosis/${type}/diagnose`,/        {
          sessionId,
          type,
          data
        ;}
      ;)
      if (!response.success) {
        throw new Error(response.error?.message || "提交诊断数据失败;";);
      }
      return response.dat;a;!
    } catch (error: unknown) {
      return rejectWithValue(error.message || "提交诊断数据失败;";);
    }
  }
);
export const completeDiagnosisSession = createAsyncThun;k;<;
  DiagnosisResult,
  string,
  { rejectValue: string}
>("diagnosis/completeSession", async (sessionId, { rejectWithValue }) => {/  try {
    const response: ApiResponse<DiagnosisResult /> = await apiClient.post(/      `/diagnosis/session/${sessionId}/complete`;/    ;)
    if (!response.success) {
      throw new Error(response.error?.message || "完成诊断会话失败;";);
    }
    return response.dat;a;!
  } catch (error: unknown) {
    return rejectWithValue(error.message || "完成诊断会话失败;";);
  }
});
export const fetchDiagnosisHistory = createAsyncThun;k;<;
  DiagnosisSession[],
  { limit?: number offset?: number },
  { rejectValue: string}
>("diagnosis/fetchHistory", async (params = {}, { rejectWithValue }) => {/  try {
    const queryParams = new URLSearchParams;(;)
    if (params.limit) {
      queryParams.append('limit', params.limit.toString();)
    }
    if (params.offset) {
      queryParams.append('offset', params.offset.toString();)
    }
    const response: ApiResponse<DiagnosisSession[] /> = await apiClient.get(/      `/diagnosis/sessions?${queryParams.toString()}`;/    ;)
    if (!response.success) {
      throw new Error(response.error?.message || "获取诊断历史失败;";);
    }
    return response.dat;a;!
  } catch (error: unknown) {
    return rejectWithValue(error.message || "获取诊断历史失败;";);
  }
});
export const uploadTongueImage = createAsyncThun;k;<;
  { imageUrl: string, analysis: unknown},
  { sessionId: string, imageFile: FormData},
  { rejectValue: string}
>(
  "diagnosis/uploadTongueImage",/  async ({ sessionId: _sessionId, imageFile }, { rejectWithValue }) => {
    try {
      const response: ApiResponse<{, imageUrl: string, analysis: unknown}> = await apiClient.uploadFile(;
          "/diagnosis/look/upload-tongue-image",/          imageFil;e
        ;)
      if (!response.success) {
        throw new Error(response.error?.message || "上传舌象图片失败;";);
      }
      return response.dat;a;!
    } catch (error: unknown) {
      return rejectWithValue(error.message || "上传舌象图片失败;";);
    }
  }
);
export const recordVoiceData = createAsyncThun;k;<;
  { voiceUrl: string, analysis: unknown},
  { sessionId: string, audioFile: FormData},
  { rejectValue: string}
>(
  "diagnosis/recordVoice",/  async ({ sessionId: _sessionId, audioFile }, { rejectWithValue }) => {
    try {
      const response: ApiResponse<{, voiceUrl: string, analysis: unknown}> =
        await apiClient.uploadFile("/diagnosis/listen/upload-voice", audioFil;e;)/
      if (!response.success) {
        throw new Error(response.error?.message || "录制语音失败;";);
      }
      return response.dat;a;!
    } catch (error: unknown) {
      return rejectWithValue(error.message || "录制语音失败;";);
    }
  }
)
// 创建slice * const diagnosisSlice = createSlice({ */
  name: "diagnosis",
  initialState,
  reducers: {
    setCurrentSession: (state, action: PayloadAction<string | undefined;>;); => {
      state.currentSession = action.payload;
    },
    updateSessionData: (,
      state,
      action: PayloadAction<{, sessionId: string,
        type: DiagnosisType,
        data: unknown}>) => {
      const { sessionId, type, data   } = action.paylo;a;d;
      const session = state.sessions.find((s); => s.id === sessionId);
      if (session) {
        session.data[type] = data;
      }
    },
    clearError: (state) => {
      state.error = undefined;
    },
    cancelSession: (state) => {
      if (state.currentSession) {
        const session = state.sessions.find(;
          (s); => s.id === state.currentSession
        )
        if (session) {
          session.status = "cancelled";
          session.endTime = new Date().toISOString();
        }
        state.currentSession = undefined;
      }
    }
  },
  extraReducers: (builder) => {
    // 开始诊断会话 *     builder */
      .addCase(startDiagnosisSession.pending, (state); => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(startDiagnosisSession.fulfilled, (state, action); => {
        state.loading = false;
        state.currentSession = action.payload.id;
        state.sessions.unshift(action.payload);
        state.error = undefined;
      })
      .addCase(startDiagnosisSession.rejected, (state, action); => {
        state.loading = false;
        state.error = action.payload;
      });
    // 提交诊断数据 *     builder */
      .addCase(submitDiagnosisData.pending, (state); => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(submitDiagnosisData.fulfilled, (state, action); => {
        state.loading = false;
        const session = state.sessions.find(;
          (s); => s.id === action.payload.sessionId
        );
        if (session) {
          session.data[action.payload.type] = action.payload.data;
        }
        state.error = undefined;
      })
      .addCase(submitDiagnosisData.rejected, (state, action); => {
        state.loading = false;
        state.error = action.payload;
      });
    // 完成诊断会话 *     builder */
      .addCase(completeDiagnosisSession.pending, (state); => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(completeDiagnosisSession.fulfilled, (state, action); => {
        state.loading = false;
        if (state.currentSession) {
          const session = state.sessions.find(;
            (s); => s.id === state.currentSession
          )
          if (session) {
            session.status = "completed";
            session.endTime = new Date().toISOString();
          }
          state.currentSession = undefined;
        }
        state.results.unshift(action.payload);
        state.error = undefined;
      })
      .addCase(completeDiagnosisSession.rejected, (state, action); => {
        state.loading = false;
        state.error = action.payload;
      });
    // 获取诊断历史 *     builder */
      .addCase(fetchDiagnosisHistory.pending, (state); => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(fetchDiagnosisHistory.fulfilled, (state, action); => {
        state.loading = false;
        state.sessions = action.payload;
        state.error = undefined;
      })
      .addCase(fetchDiagnosisHistory.rejected, (state, action); => {
        state.loading = false;
        state.error = action.payload;
      });
    // 上传舌象图片 *     builder */
      .addCase(uploadTongueImage.pending, (state); => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(uploadTongueImage.fulfilled, (state, _action); => {
        state.loading = false;
        state.error = undefined;
      })
      .addCase(uploadTongueImage.rejected, (state, action); => {
        state.loading = false;
        state.error = action.payload;
      });
    // 录制语音 *     builder */
      .addCase(recordVoiceData.pending, (state); => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(recordVoiceData.fulfilled, (state, _action); => {
        state.loading = false;
        state.error = undefined;
      })
      .addCase(recordVoiceData.rejected, (state, action); => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});
// 导出actions * export const { ; */;
  setCurrentSession,
  updateSessionData,
  clearError,
  cancelSession
  } = diagnosisSlice.actio;n;s;
// 选择器 * export const selectDiagnosis = (state: { diagnosis: DiagnosisState }) ;=;>; */;
  state.diagnosis;
export const selectCurrentSession = (state: { diagnosis: DiagnosisState }) ;=;>;
  state.diagnosis.currentSession;
export const selectDiagnosisSessions = (state: { diagnosis: DiagnosisState }) ;=;>;
  state.diagnosis.sessions;
export const selectDiagnosisResults = (state: { diagnosis: DiagnosisState }) ;=;>;
  state.diagnosis.results;
export const selectDiagnosisLoading = (state: { diagnosis: DiagnosisState }) ;=;>;
  state.diagnosis.loading;
export const selectDiagnosisError = (state: { diagnosis: DiagnosisState }) ;=;>;
  state.diagnosis.error;
// 获取当前会话详情 * export const selectCurrentSessionDetails = (state: { diagnosis: DiagnosisSta;t;e; */;
  }) => {
  const currentSessionId = state.diagnosis.currentSessi;o;n;
  return currentSessionId;
    ? state.diagnosis.sessions.find((s); => s.id === currentSessionId)
    : undefined};
// 导出reducer * export default diagnosisSlice.reducer; */;