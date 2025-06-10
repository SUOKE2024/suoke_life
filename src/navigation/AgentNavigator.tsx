import { createNativeStackNavigator } from '@react-navigation/native-stack';
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { AgentStackParamList } from './types';

// 懒加载智能体相关屏幕
const AgentListScreen = React.lazy(() => import('../screens/agents/AgentListScreen'));
const AgentChatScreen = React.lazy(() => import('../screens/agents/AgentChatScreen'));

// 临时占位组件
const PlaceholderScreen = ({ title }: { title: string ;}) => (
  <View style={styles.container}>
    <Text style={styles.title}>{title}</Text>
    <Text style={styles.subtitle}>该功能正在开发中，敬请期待</Text>
  </View>
);

// 占位屏幕组件
const AgentManagementScreen = () => <PlaceholderScreen title="智能体管理" />;
const AgentProfileScreen = () => <PlaceholderScreen title="智能体档案" />;
const AgentConfigScreen = () => <PlaceholderScreen title="智能体配置" />;
const AgentAnalyticsScreen = () => <PlaceholderScreen title="智能体分析" />;

const Stack = createNativeStackNavigator<AgentStackParamList>();

/**
 * 智能体导航器
 * 管理所有智能体相关的屏幕和导航
 */
export const AgentNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      initialRouteName="AgentList"
      screenOptions={{
        headerShown: false;
        animation: 'slide_from_right';
        gestureEnabled: true;
        gestureDirection: 'horizontal';
      }}
    >
      <Stack.Screen
        name="AgentList"
        component={AgentListScreen}
        options={{
          gestureEnabled: false;
        }}
      />
      
      <Stack.Screen
        name="AgentManagement"
        component={AgentManagementScreen}
        options={{
          animation: 'slide_from_right';
        }}
      />
      
      <Stack.Screen
        name="AgentChat"
        component={AgentChatScreen}
        options={{
          animation: 'slide_from_bottom';
          presentation: 'modal';
        }}
      />
      
      <Stack.Screen
        name="AgentProfile"
        component={AgentProfileScreen}
        options={{
          animation: 'slide_from_right';
        }}
      />
      
      <Stack.Screen
        name="AgentConfig"
        component={AgentConfigScreen}
        options={{
          animation: 'slide_from_right';
        }}
      />
      
      <Stack.Screen
        name="AgentAnalytics"
        component={AgentAnalyticsScreen}
        options={{
          animation: 'slide_from_right';
        }}
      />
    </Stack.Navigator>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1;
    justifyContent: 'center';
    alignItems: 'center';
    backgroundColor: '#f5f5f5';
    padding: 20;
  },
  title: {
    fontSize: 24;
    fontWeight: 'bold';
    color: '#333333';
    marginBottom: 16;
  },
  subtitle: {
    fontSize: 16;
    color: '#666666';
    textAlign: 'center';
    lineHeight: 24;
  },
});

export default AgentNavigator;