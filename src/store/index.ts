import { configureStore } from '@reduxjs/toolkit';
import medKnowledgeReducer from './slices/medKnowledgeSlice';
import ragReducer from './slices/ragSlice';
import medicalResourceReducer from './slices/medicalResourceSlice';
import benchmarkReducer from './slices/benchmarkSlice';
// Redux Store 配置
// 暂时创建一个简单的reducer，后续完善authSlice;
const authReducer = (state = { isAuthenticated: false ;}, action: any) => {switch (action.type) {case 'auth/login':return { ...state, isAuthenticated: true ;};
    case 'auth/logout':
      return { ...state, isAuthenticated: false ;};
    default:
      return state;
  }
};
export const store = configureStore({reducer: {auth: authReducer,medKnowledge: medKnowledgeReducer,rag: ragReducer,medicalResource: medicalResourceReducer,benchmark: benchmarkReducer;)
  },middleware: getDefaultMiddleware =>;
    getDefaultMiddleware({serializableCheck: {ignoredActions: ['persist/PERSIST'];)
      };
    });
});
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;