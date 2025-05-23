import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import healthReducer from './slices/healthSlice';
import agentReducer from './slices/agentSlice';
import userReducer from './slices/userSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    health: healthReducer,
    agent: agentReducer,
    user: userReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // 忽略日期和文件对象序列化检查
        ignoredActions: ['health/uploadHealthData', 'agent/uploadImage'],
        ignoredPaths: ['agent.uploadedFiles'],
      },
    }),
});

// 导出RootState和AppDispatch类型
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// 强制指定RootState对象的类型
declare module 'react-redux' {
  interface DefaultRootState extends RootState {}
}