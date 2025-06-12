import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { NavigationContainer } from '@react-navigation/native';

// 导入屏幕组件
import WelcomeScreen from '../screens/auth/WelcomeScreen';
import LoginScreen from '../screens/auth/LoginScreen';
import RegisterScreen from '../screens/auth/RegisterScreen';
import ForgotPasswordScreen from '../screens/auth/ForgotPasswordScreen';
import MainTabNavigator from './MainTabNavigator';
import AgentChatScreen from '../screens/chat/AgentChatScreen';

// 导航参数类型定义
export type RootStackParamList = {
  Welcome: undefined;
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
  MainApp: undefined;
  AgentChat: {
    agentId: string;
    agentName: string;
    agentType: string;
  };
  Chat: {
    contactId: string;
    contactName: string;
    contactType: string;
  };
  NewChat: undefined;
  Search: undefined;
};

const Stack = createStackNavigator<RootStackParamList>();

const AppNavigator: React.FC = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Welcome"
        screenOptions={{
          headerShown: false,
          gestureEnabled: true,
          cardStyleInterpolator: ({ current, layouts }) => {
            return {
              cardStyle: {
                transform: [
                  {
                    translateX: current.progress.interpolate({
                      inputRange: [0, 1],
                      outputRange: [layouts.screen.width, 0],
                    }),
                  },
                ],
              },
            };
          },
        }}
      >
        {/* 欢迎页面 */}
        <Stack.Screen
          name="Welcome"
          component={WelcomeScreen}
          options={{
            cardStyleInterpolator: ({ current }) => ({
              cardStyle: {
                opacity: current.progress,
              },
            }),
          }}
        />

        {/* 认证流程 */}
        <Stack.Screen
          name="Login"
          component={LoginScreen}
          options={{
            gestureDirection: 'horizontal',
          }}
        />
        <Stack.Screen
          name="Register"
          component={RegisterScreen}
          options={{
            gestureDirection: 'horizontal',
          }}
        />
        <Stack.Screen
          name="ForgotPassword"
          component={ForgotPasswordScreen}
          options={{
            gestureDirection: 'horizontal',
          }}
        />

        {/* 主应用 */}
        <Stack.Screen
          name="MainApp"
          component={MainTabNavigator}
          options={{
            gestureEnabled: false, // 禁用手势返回，防止意外退出主应用
            cardStyleInterpolator: ({ current }) => ({
              cardStyle: {
                opacity: current.progress,
              },
            }),
          }}
        />

        {/* 聊天相关屏幕 */}
        <Stack.Screen
          name="AgentChat"
          component={AgentChatScreen}
          options={{
            headerShown: true,
            headerTitle: '',
            headerBackTitleVisible: false,
            headerStyle: {
              backgroundColor: '#ffffff',
              elevation: 0,
              shadowOpacity: 0,
              borderBottomWidth: 1,
              borderBottomColor: '#f0f0f0',
            },
            headerTintColor: '#333',
            gestureDirection: 'horizontal',
          }}
        />

        {/* 占位符屏幕 */}
        <Stack.Screen
          name="Chat"
          component={PlaceholderChatScreen}
          options={{
            headerShown: true,
            headerTitle: '聊天',
            headerBackTitleVisible: false,
            headerStyle: {
              backgroundColor: '#ffffff',
              elevation: 0,
              shadowOpacity: 0,
              borderBottomWidth: 1,
              borderBottomColor: '#f0f0f0',
            },
            headerTintColor: '#333',
            gestureDirection: 'horizontal',
          }}
        />

        <Stack.Screen
          name="NewChat"
          component={PlaceholderNewChatScreen}
          options={{
            headerShown: true,
            headerTitle: '新建聊天',
            headerBackTitleVisible: false,
            headerStyle: {
              backgroundColor: '#ffffff',
              elevation: 0,
              shadowOpacity: 0,
              borderBottomWidth: 1,
              borderBottomColor: '#f0f0f0',
            },
            headerTintColor: '#333',
            gestureDirection: 'horizontal',
          }}
        />

        <Stack.Screen
          name="Search"
          component={PlaceholderSearchScreen}
          options={{
            headerShown: true,
            headerTitle: '搜索',
            headerBackTitleVisible: false,
            headerStyle: {
              backgroundColor: '#ffffff',
              elevation: 0,
              shadowOpacity: 0,
              borderBottomWidth: 1,
              borderBottomColor: '#f0f0f0',
            },
            headerTintColor: '#333',
            gestureDirection: 'horizontal',
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

// 占位符组件
import { View, Text, StyleSheet } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';

const PlaceholderScreen: React.FC<{ title: string; description: string }> = ({ title, description }) => (
  <View style={styles.placeholderContainer}>
    <Icon name="construction" size={80} color="#ccc" />
    <Text style={styles.placeholderTitle}>{title}</Text>
    <Text style={styles.placeholderDescription}>{description}</Text>
  </View>
);

const PlaceholderChatScreen = () => (
  <PlaceholderScreen 
    title="通用聊天" 
    description="与用户、名医、服务商、供应商的聊天功能" 
  />
);

const PlaceholderNewChatScreen = () => (
  <PlaceholderScreen 
    title="新建聊天" 
    description="创建新的聊天会话或群组" 
  />
);

const PlaceholderSearchScreen = () => (
  <PlaceholderScreen 
    title="搜索" 
    description="搜索联系人、消息、服务和内容" 
  />
);

const styles = StyleSheet.create({
  placeholderContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    paddingHorizontal: 40,
  },
  placeholderTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 20,
    marginBottom: 12,
  },
  placeholderDescription: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
  },
});

export default AppNavigator;