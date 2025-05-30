import { configureStore } from "@reduxjs/toolkit";
import { TypedUseSelectorHook, useDispatch, useSelector } from "react-redux";
import authSlice from "./slices/authSlice";
import userSlice from "./slices/userSlice";
import agentsSlice from "./slices/agentsSlice";
import diagnosisSlice from "./slices/diagnosisSlice";
import healthSlice from "./slices/healthSlice";
import uiSlice from "./slices/uiSlice";
import { apiMiddleware } from "./middleware/apiMiddleware";
import { persistMiddleware } from "./middleware/persistMiddleware";

// 导入各个slice

// 导入中间件

// 配置store
export const store = configureStore({
  reducer: {
    auth: authSlice,
    user: userSlice,
    agents: agentsSlice,
    diagnosis: diagnosisSlice,
    health: healthSlice,
    ui: uiSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // 忽略这些action类型的序列化检查
        ignoredActions: [
          "persist/PERSIST",
          "persist/REHYDRATE",
          "persist/REGISTER",
        ],
        // 忽略这些路径的序列化检查
        ignoredPaths: ["auth.token", "auth.refreshToken"],
      },
    })
      .concat(apiMiddleware)
      .concat(persistMiddleware),
  devTools: __DEV__,
});

// 导出类型
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// 创建类型化的hooks
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// 导出store
export default store;
