import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { STORAGE_KEYS, API_URL, API_TIMEOUT } from '../config/constants';
import { store } from '../store';
import { logout } from '../store/slices/userSlice';

// 创建一个axios实例
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// 请求拦截器：添加身份验证令牌
apiClient.interceptors.request.use(
  async (config) => {
    // 从本地存储获取访问令牌
    const token = await AsyncStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
    
    // 如果存在令牌，则添加到请求头中
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 是否正在刷新令牌
let isRefreshing = false;
// 等待令牌刷新的请求队列
let refreshSubscribers: ((token: string) => void)[] = [];

// 响应拦截器：处理令牌过期
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
    
    // 如果是401未授权错误，并且不是刷新令牌的请求，并且没有重试过
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (!isRefreshing) {
        isRefreshing = true;
        originalRequest._retry = true;
        
        try {
          // 从本地存储获取刷新令牌
          const refreshToken = await AsyncStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
          
          if (!refreshToken) {
            // 如果没有刷新令牌，则直接退出登录
            store.dispatch(logout());
            return Promise.reject(error);
          }
          
          // 尝试刷新令牌
          const response = await axios.post(`${API_URL}/auth/refresh-token`, { refreshToken });
          const { access_token } = response.data.data;
          
          // 更新本地存储的访问令牌
          await AsyncStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, access_token);
          
          // 更新所有等待中的请求的令牌
          refreshSubscribers.forEach(callback => callback(access_token));
          refreshSubscribers = [];
          
          // 重试原始请求
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          
          return apiClient(originalRequest);
        } catch (refreshError) {
          // 如果刷新令牌失败，则退出登录
          store.dispatch(logout());
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      } else {
        // 如果已经在刷新令牌，将请求添加到等待队列
        return new Promise((resolve) => {
          refreshSubscribers.push((token: string) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            resolve(apiClient(originalRequest));
          });
        });
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient; 