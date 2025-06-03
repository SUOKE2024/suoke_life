import React, { useState, useEffect } from "react";
import { createStackNavigator } from "@react-navigation/stack";
import { MainNavigator } from "./MainNavigator";
import { AuthNavigator } from "./AuthNavigator";
import AgentDemoScreen from "../screens/demo/AgentDemoScreen";

// 应用主导航器 - 负责管理应用的整体导航流程，包括认证状态检查和路由分发
const Stack = createStackNavigator();

const AppNavigator: React.FC = () => {
  // 简单的认证状态管理（后续可以集成到Redux或Context中）
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isDemoMode, setIsDemoMode] = useState(false);

  // 检查认证状态
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        // TODO: 实际的认证状态检查逻辑
        // 这里可以检查AsyncStorage中的token或其他认证信息
        // const token = await AsyncStorage.getItem("authToken")
        // setIsAuthenticated(!!token)
        
        // 暂时设置为未认证状态，显示欢迎页面
        setIsAuthenticated(false);
      } catch (error) {
        setIsAuthenticated(false);
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
        animationEnabled: true
      }}
    >
      {isAuthenticated || isDemoMode ? (
        // 已认证用户或演示模式显示主应用
        <>
          <Stack.Screen
            name="Main"
            component={MainNavigator}
            options={{
              animationTypeForReplace: "push"
            }}
          />
          <Stack.Screen
            name="AgentDemo"
            component={AgentDemoScreen}
            options={{
              cardStyleInterpolator: ({ current, layouts }) => {
                return {
                  cardStyle: {
                    transform: [
                      {
                        translateX: current.progress.interpolate({
                          inputRange: [0, 1],
                          outputRange: [layouts.screen.width, 0]
                        })
                      }
                    ]
                  }
                };
              }
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
              animationTypeForReplace: 'pop'
            }}
          />
          <Stack.Screen
            name="AgentDemo"
            component={AgentDemoScreen}
            options={{
              cardStyleInterpolator: ({ current, layouts }) => {
                return {
                  cardStyle: {
                    transform: [
                      {
                        translateX: current.progress.interpolate({
                          inputRange: [0, 1],
                          outputRange: [layouts.screen.width, 0]
                        })
                      }
                    ]
                  }
                };
              }
            }}
          />
        </>
      )}
    </Stack.Navigator>
  );
};

export default AppNavigator;