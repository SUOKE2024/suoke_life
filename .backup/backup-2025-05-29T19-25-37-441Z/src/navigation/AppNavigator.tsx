/**
 * 应用主导航器
 * 负责管理应用的整体导航流程，包括认证状态检查和路由分发
 */

import React, { useEffect, useState } from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { useSelector, useDispatch } from 'react-redux';

// 导航器
import { AuthNavigator } from './AuthNavigator';
import { MainNavigator } from './MainNavigator';

// Redux
import {
  selectIsAuthenticated,
  // selectAuthLoading,
  checkAuthStatus,
} from '../store/slices/authSlice';

// 简单的启动屏幕组件
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';

const SimpleSplashScreen: React.FC = () => (
  <View style={styles.splashContainer}>
    <Text style={styles.splashTitle}>索克生活</Text>
    <Text style={styles.splashSubtitle}>Suoke Life</Text>
    <ActivityIndicator size="large" color="#007AFF" style={styles.loading} />
  </View>
);

// 类型
export type AppStackParamList = {
  Splash: undefined;
  Auth: undefined;
  Main: undefined;
};

const Stack = createStackNavigator<AppStackParamList>();

export const AppNavigator: React.FC = () => {
  const dispatch = useDispatch();
  const isAuthenticated = useSelector(selectIsAuthenticated);
  // const isLoading = useSelector(selectAuthLoading);
  const [isInitializing, setIsInitializing] = useState(true);

  // 检查认证状态
  useEffect(() => {
    const initializeApp = async () => {
      try {
        await dispatch(checkAuthStatus() as any);
      } catch (error) {
        console.log('认证检查失败:', error);
      } finally {
        setIsInitializing(false);
      }
    };

    const timer = setTimeout(() => {
      initializeApp();
    }, 1500); // 1.5秒启动屏幕

    return () => clearTimeout(timer);
  }, [dispatch]);

  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        gestureEnabled: false,
      }}
    >
      {isInitializing ? (
        // 初始化状态
        <Stack.Screen name="Splash" component={SimpleSplashScreen} />
      ) : (
        // 直接进入主应用（跳过认证）
        <Stack.Screen name="Main" component={MainNavigator} />
      )}
    </Stack.Navigator>
  );
};

const styles = StyleSheet.create({
  splashContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#007AFF',
  },
  splashTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  splashSubtitle: {
    fontSize: 16,
    color: 'white',
    marginBottom: 40,
  },
  loading: {
    marginTop: 20,
  },
});
