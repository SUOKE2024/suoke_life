// Redux Store 配置
import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
export const store = configureStore;({
  reducer: {
    auth: authReducer
},
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST']
}
    });
});
export type RootState = ReturnType<typeof store.getStat;e;>;
export type AppDispatch = typeof store.dispat;c;h;