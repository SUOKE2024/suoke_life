import { Middleware } from '@reduxjs/toolkit';
import {
  showErrorNotification,
  showSuccessNotification,
} from '../slices/uiSlice';

// API中间件 - 统一处理API请求和响应
export const apiMiddleware: Middleware = (store) => (next) => (action: any) => {
  // 检查是否是异步action
  if (action.type && typeof action.type === 'string') {
    const { type } = action;

    // 处理pending状态
    if (type.endsWith('/pending')) {
      // 可以在这里添加全局loading逻辑
      console.log('API请求开始:', type);
    }

    // 处理fulfilled状态
    if (type.endsWith('/fulfilled')) {
      console.log('API请求成功:', type);

      // 对于某些操作显示成功通知
      if (shouldShowSuccessNotification(type)) {
        const message = getSuccessMessage(type);
        if (message) {
          store.dispatch(showSuccessNotification(message));
        }
      }
    }

    // 处理rejected状态
    if (type.endsWith('/rejected')) {
      console.error('API请求失败:', type, action.payload);

      // 显示错误通知
      const errorMessage = action.payload || '操作失败，请稍后重试';
      store.dispatch(showErrorNotification(errorMessage));
    }
  }

  return next(action);
};

// 判断是否应该显示成功通知
function shouldShowSuccessNotification(actionType: string): boolean {
  const successNotificationActions = [
    'auth/login/fulfilled',
    'auth/register/fulfilled',
    'user/updateProfile/fulfilled',
    'diagnosis/completeSession/fulfilled',
    'health/syncData/fulfilled',
  ];

  return successNotificationActions.some((pattern) =>
    actionType.includes(pattern.split('/')[0])
  );
}

// 获取成功消息
function getSuccessMessage(actionType: string): string | null {
  const messageMap: Record<string, string> = {
    'auth/login/fulfilled': '登录成功',
    'auth/register/fulfilled': '注册成功',
    'auth/logout/fulfilled': '退出登录成功',
    'user/updateProfile/fulfilled': '资料更新成功',
    'diagnosis/completeSession/fulfilled': '诊断完成',
    'health/syncData/fulfilled': '健康数据同步成功',
  };

  for (const [pattern, message] of Object.entries(messageMap)) {
    if (actionType.includes(pattern)) {
      return message;
    }
  }

  return null;
}

export default apiMiddleware;
