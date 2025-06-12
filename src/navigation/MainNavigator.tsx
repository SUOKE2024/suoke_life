import React, { Suspense } from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';

// 导入主要屏幕
import HomeScreen from '../screens/main/HomeScreen';
import AgentChatScreen from '../screens/agents/AgentChatScreen';

// 导入导航器
import AgentNavigator from './AgentNavigator';

// 导航参数类型定义
export type MainStackParamList = {
  Home: undefined;
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
  Search: undefined;
  NewChat: undefined;
  Agents: undefined;
};

const Stack = createNativeStackNavigator<MainStackParamList>();

// 加载指示器组件
const LoadingSpinner = () => (
  <View style={styles.loadingContainer}>
    <ActivityIndicator size="large" color="#2196F3" />
    <Text style={styles.loadingText}>正在加载...</Text>
  </View>
);

// 搜索屏幕占位符
const SearchScreen = () => (
  <View style={styles.placeholderContainer}>
    <Text style={styles.placeholderTitle}>搜索功能</Text>
    <Text style={styles.placeholderSubtitle}>该功能正在开发中，敬请期待</Text>
  </View>
);

// 新建聊天屏幕占位符
const NewChatScreen = () => (
  <View style={styles.placeholderContainer}>
    <Text style={styles.placeholderTitle}>新建聊天</Text>
    <Text style={styles.placeholderSubtitle}>该功能正在开发中，敬请期待</Text>
  </View>
);

// 通用聊天屏幕占位符
const ChatScreen = () => (
  <View style={styles.placeholderContainer}>
    <Text style={styles.placeholderTitle}>聊天界面</Text>
    <Text style={styles.placeholderSubtitle}>该功能正在开发中，敬请期待</Text>
  </View>
);

// 主导航器
export const MainNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      initialRouteName="Home"
      screenOptions={{
        headerShown: false,
        animation: 'slide_from_right',
        gestureEnabled: true,
        gestureDirection: 'horizontal',
      }}
    >
      {/* 首页 */}
      <Stack.Screen
        name="Home"
        options={{
          gestureEnabled: false,
        }}
      >
        {() => (
          <Suspense fallback={<LoadingSpinner />}>
            <HomeScreen />
          </Suspense>
        )}
      </Stack.Screen>

      {/* 智能体聊天 */}
      <Stack.Screen
        name="AgentChat"
        options={{
          animation: 'slide_from_bottom',
          presentation: 'modal',
        }}
      >
        {() => (
          <Suspense fallback={<LoadingSpinner />}>
            <AgentChatScreen />
          </Suspense>
        )}
      </Stack.Screen>

      {/* 通用聊天 */}
      <Stack.Screen
        name="Chat"
        component={ChatScreen}
        options={{
          animation: 'slide_from_right',
        }}
      />

      {/* 搜索 */}
      <Stack.Screen
        name="Search"
        component={SearchScreen}
        options={{
          animation: 'slide_from_top',
          presentation: 'modal',
        }}
      />

      {/* 新建聊天 */}
      <Stack.Screen
        name="NewChat"
        component={NewChatScreen}
        options={{
          animation: 'slide_from_bottom',
          presentation: 'modal',
        }}
      />

      {/* 智能体导航器 */}
      <Stack.Screen
        name="Agents"
        component={AgentNavigator}
        options={{
          animation: 'slide_from_right',
        }}
      />
    </Stack.Navigator>
  );
};

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666666',
  },
  placeholderContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  placeholderTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333333',
    marginBottom: 16,
  },
  placeholderSubtitle: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
    lineHeight: 24,
  },
});

export default MainNavigator;