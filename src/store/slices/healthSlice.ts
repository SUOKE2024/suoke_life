import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { API_URL } from '../../config/constants';
import axios from 'axios';

// 健康相关接口定义
export interface HealthData {
  id: string;
  userId: string;
  date: string;
  sleepHours: number;
  steps: number;
  activeMinutes: number;
  weight?: number;
  bloodPressureSystolic?: number;
  bloodPressureDiastolic?: number;
  heartRate?: number;
  bloodSugar?: number;
  mood?: string;
  symptoms?: string[];
}

export interface HealthReport {
  id: string;
  userId: string;
  date: string;
  score: number;
  constitution: string;
  indicators: HealthIndicator[];
  suggestions: string[];
  createdAt: number;
}

export interface HealthIndicator {
  name: string;
  score: number;
  status: string;
}

export interface HealthPlan {
  id: string;
  userId: string;
  title: string;
  description: string;
  startDate: string;
  endDate: string;
  progress: number;
  tasks: HealthTask[];
  createdAt: number;
}

export interface HealthTask {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  dueDate?: string;
}

export interface HealthState {
  healthData: HealthData[];
  reports: HealthReport[];
  plans: HealthPlan[];
  latestReport: HealthReport | null;
  isLoading: boolean;
  error: string | null;
}

// 初始状态
const initialState: HealthState = {
  healthData: [],
  reports: [],
  plans: [],
  latestReport: null,
  isLoading: false,
  error: null
};

// 健康状态切片
const healthSlice = createSlice({
  name: 'health',
  initialState,
  reducers: {
    clearHealthError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    // 这里将来会添加异步操作的处理
  }
});

export const { clearHealthError } = healthSlice.actions;

export default healthSlice.reducer; 