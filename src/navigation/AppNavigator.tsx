import React, { useState, useEffect } from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import { MainNavigator } from './MainNavigator';
import { AuthNavigator } from './AuthNavigator';
const ChatDetailScreen = React.lazy(() => import('../screens/main/ChatDetailScreen'));
// 临时AgentDemo组件
const AgentDemoScreen: React.FC = () => {
  return null; // TODO: 实现AgentDemo页面
};

// 根导航参数类型
export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
  ChatDetail: {
    chatId: string;
    chatType: string;
    chatName: string;
  };
  AgentDemo: undefined;
};

// 应用主导航器 - 负责管理应用的整体导航流程，包括认证状态检查和路由分发
const Stack = createNativeStackNavigator<RootStackParamList>();

const AppNavigator: React.FC = () => {
  // 从Redux获取认证状态
  const authState = useSelector((state: RootState) => state.auth);
  const isAuthenticated = 'isAuthenticated' in authState ? authState.isAuthenticated : false;

  // 本地状态管理
  const [isLoading, setIsLoading] = useState(true);
  const [isDemoMode, setIsDemoMode] = useState(false);

  // 检查认证状态
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        // TODO: 实际的认证状态检查逻辑
        // 这里可以检查AsyncStorage中的token或其他认证信息
        // const token = await AsyncStorage.getItem("authToken");
        // setIsAuthenticated(!!token);

        // 暂时设置为未认证状态，显示欢迎页面
        // setIsAuthenticated(false);
      } catch (error) {
        console.error('认证状态检查失败:', error);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  // 如果正在加载，可以显示启动画面
  if (isLoading) {
    // TODO: 添加启动画面组件
    return null;
  }

  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        gestureEnabled: true,
        animation: 'slide_from_right',
      }}
    >
      {isAuthenticated || isDemoMode ? (
        // 已认证用户或演示模式显示主应用
        <>
          <Stack.Screen
            name="Main"
            component={MainNavigator}
            options={{
              animationTypeForReplace: 'push',
            }}
          />
          <Stack.Screen
            name="ChatDetail"
            component={ChatDetailScreen}
            options={{
              presentation: 'card',
              animation: 'slide_from_right',
            }}
          />
          <Stack.Screen
            name="AgentDemo"
            component={AgentDemoScreen}
            options={{
              presentation: 'card',
              animation: 'slide_from_right',
            }}
          />
        </>
      ) : (
        // 未认证用户显示认证流程
        <>
          <Stack.Screen
            name="Auth"
            component={AuthNavigator}
            options={{
              animationTypeForReplace: 'pop',
            }}
          />
          <Stack.Screen
            name="AgentDemo"
            component={AgentDemoScreen}
            options={{
              presentation: 'card',
              animation: 'slide_from_right',
            }}
          />
        </>
      )}
    </Stack.Navigator>
  );
};

export default AppNavigator;
