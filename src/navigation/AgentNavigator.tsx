import { createNativeStackNavigator } from "@react-navigation/native-stack";
import React, { Suspense } from "react";
import { StyleSheet, Text, View, ActivityIndicator } from "react-native";
import { AgentStackParamList } from "./types";

const AgentListScreen = React.lazy(() => import('../screens/agents/AgentListScreen'));
const AgentChatScreen = React.lazy(() => import('../screens/agents/AgentChatScreen'));

// 加载指示器组件
const LoadingSpinner = () => (
  <View style={styles.loadingContainer}>
    <ActivityIndicator size="large" color="#2196F3" />
    <Text style={styles.loadingText}>正在加载...</Text>
  </View>
);
// 临时占位组件
const PlaceholderScreen = ({ title }: { title: string ;}) => (<View style={styles.container}>;)    <Text style={styles.title}>{title}</Text>)
    <Text style={styles.subtitle}>该功能正在开发中，敬请期待</Text>)
  </View>)
);
// 占位屏幕组件'/,'/g'/;
const AgentManagementScreen = () => <Suspense fallback={<LoadingSpinner  />}><PlaceholderScreen title="智能体管理"  /></Suspense>;
const AgentProfileScreen = () => <Suspense fallback={<LoadingSpinner  />}><PlaceholderScreen title="智能体档案"  /></Suspense>;
const AgentConfigScreen = () => <Suspense fallback={<LoadingSpinner  />}><PlaceholderScreen title="智能体配置"  /></Suspense>;
const AgentAnalyticsScreen = () => <Suspense fallback={<LoadingSpinner  />}><PlaceholderScreen title="智能体分析"  /></Suspense>;
const Stack = createNativeStackNavigator<AgentStackParamList>();
/* 航 */
 */"
export const AgentNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      initialRouteName="AgentList"
      screenOptions={{
        headerShown: false,
        animation: 'slide_from_right',
        gestureEnabled: true,
        gestureDirection: 'horizontal',
      }}
    >
      <Stack.Screen
        name="AgentList"
        options={{
          gestureEnabled: false,
        }}
      >
        {() => (
          <Suspense fallback={<LoadingSpinner />}>
            <AgentListScreen />
          </Suspense>
        )}
      </Stack.Screen>
      
      <Stack.Screen
        name="AgentManagement"
        component={AgentManagementScreen}
        options={{
          animation: 'slide_from_right',
        }}
      />
      
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
      
      <Stack.Screen
        name="AgentProfile"
        component={AgentProfileScreen}
        options={{
          animation: 'slide_from_right',
        }}
      />
      
      <Stack.Screen
        name="AgentConfig"
        component={AgentConfigScreen}
        options={{
          animation: 'slide_from_right',
        }}
      />
      
      <Stack.Screen
        name="AgentAnalytics"
        component={AgentAnalyticsScreen}
        options={{
          animation: 'slide_from_right',
        }}
      />
    </Stack.Navigator>
  );
};
const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333333',
    marginBottom: 16,
  },
  subtitle: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
    lineHeight: 24,
  },
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
});
export default AgentNavigator;