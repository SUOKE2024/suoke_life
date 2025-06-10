import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { NavigationContainer } from '@react-navigation/native';
import React, { Suspense, useEffect, useState } from 'react';
import {
  StatusBar,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';

// 懒加载屏幕组件
const HomeScreen = React.lazy(() => import('./screens/main/HomeScreen'));
const LifeOverviewScreen = React.lazy(
  () => import('./screens/health/LifeOverviewScreen')
);
const FiveDiagnosisAgentIntegrationScreen = React.lazy(
  () => import('./screens/demo/FiveDiagnosisAgentIntegrationScreen')
);
const ExploreScreen = React.lazy(
  () => import('./screens/explore/ExploreScreen')
);

// 导航器
const BusinessNavigator = React.lazy(
  () => import('./navigation/BusinessNavigator')
);
const AgentNavigator = React.lazy(() => import('./navigation/AgentNavigator'));

// 组件
const BusinessQuickAccess = React.lazy(
  () => import('./components/business/BusinessQuickAccess')
);
const GatewayMonitor = React.lazy(
  () => import('./components/common/GatewayMonitor')
);
const GatewayConfig = React.lazy(
  () => import('./components/common/GatewayConfig')
);
const AnalyticsDashboard = React.lazy(
  () => import('./components/common/AnalyticsDashboard')
);
const GatewayConfigManager = React.lazy(
  () => import('./components/common/GatewayConfigManager')
);

const Tab = createBottomTabNavigator();

// 加载组件
const LoadingFallback = () => (
  <View style={styles.loadingContainer}>
    <Text style={styles.loadingText}>正在加载...</Text>
  </View>
);

// 简单的ProfileScreen组件
const ProfileScreen = () => (
  <View style={styles.profileContainer}>
    <Text style={styles.profileTitle}>个人中心</Text>
    <Suspense fallback={<LoadingFallback />}>
      <BusinessQuickAccess />
    </Suspense>
  </View>
);

// 网关管理屏幕
const GatewayManagementScreen = () => {
  const [activeTab, setActiveTab] = useState('monitor');

  const renderContent = () => {
    switch (activeTab) {
      case 'monitor':
        return <GatewayMonitor />;
      case 'config':
        return <GatewayConfig />;
      case 'analytics':
        return <AnalyticsDashboard />;
      case 'settings':
        return <GatewayConfigManager />;
      default:
        return <GatewayMonitor />;
    }
  };

  return (
    <View style={styles.gatewayContainer}>
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'monitor' && styles.activeTab]}
          onPress={() => setActiveTab('monitor')}
        >
          <Text>监控</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'config' && styles.activeTab]}
          onPress={() => setActiveTab('config')}
        >
          <Text>配置</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'analytics' && styles.activeTab]}
          onPress={() => setActiveTab('analytics')}
        >
          <Text>分析</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'settings' && styles.activeTab]}
          onPress={() => setActiveTab('settings')}
        >
          <Text>设置</Text>
        </TouchableOpacity>
      </View>
      {renderContent()}
    </View>
  );
};

// 图标组件
const TabBarIcon = ({ focused, color, size, route }: any) => {
  let iconName = 'help';

  switch (route.name) {
    case 'Main':
      iconName = focused ? 'home' : 'home';
      break;
    case 'Health':
      iconName = focused ? 'favorite' : 'favorite-border';
      break;
    case 'Diagnosis':
      iconName = focused ? 'healing' : 'local-hospital';
      break;
    case 'Explore':
      iconName = focused ? 'explore' : 'explore';
      break;
    case 'Business':
      iconName = focused ? 'business' : 'business';
      break;
    case 'Agents':
      iconName = focused ? 'smart-toy' : 'android';
      break;
    case 'Profile':
      iconName = focused ? 'person' : 'person';
      break;
    case 'Gateway':
      iconName = focused ? 'settings' : 'settings';
      break;
  }

  return <Icon name={iconName} size={size} color={color} />;
};

// 主标签导航
const MainTabs = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => (
          <TabBarIcon
            focused={focused}
            color={color}
            size={size}
            route={route}
          />
        ),
        tabBarActiveTintColor: '#2196F3',
        tabBarInactiveTintColor: 'gray',
        headerShown: false,
      })}
    >
      <Tab.Screen
        name="Main"
        component={HomeScreen}
        options={{ title: '首页' }}
      />
      <Tab.Screen
        name="Health"
        component={LifeOverviewScreen}
        options={{ title: '健康' }}
      />
      <Tab.Screen
        name="Diagnosis"
        component={FiveDiagnosisAgentIntegrationScreen}
        options={{ title: '诊断' }}
      />
      <Tab.Screen
        name="Explore"
        component={ExploreScreen}
        options={{ title: '探索' }}
      />
      <Tab.Screen
        name="Business"
        component={BusinessNavigator}
        options={{ title: '商业' }}
      />
      <Tab.Screen
        name="Agents"
        component={AgentNavigator}
        options={{ title: '智能体' }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{ title: '我的' }}
      />
      <Tab.Screen
        name="Gateway"
        component={GatewayManagementScreen}
        options={{ title: '网关' }}
      />
    </Tab.Navigator>
  );
};

// 主应用组件
const App = () => {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // 应用初始化逻辑
    const initializeApp = async () => {
      try {
        // 这里可以添加应用启动时的初始化逻辑
        await new Promise((resolve) => setTimeout(resolve, 1000));
        setIsReady(true);
      } catch (error) {
        console.error('应用初始化失败:', error);
        setIsReady(true); // 即使失败也要显示应用
      }
    };

    initializeApp();
  }, []);

  if (!isReady) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>索克生活正在启动...</Text>
      </View>
    );
  }

  return (
    <NavigationContainer>
      <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
      <Suspense fallback={<LoadingFallback />}>
        <MainTabs />
      </Suspense>
    </NavigationContainer>
  );
};

// 样式定义
const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
  },
  loadingText: {
    fontSize: 16,
    color: '#666666',
    marginTop: 10,
  },
  profileContainer: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  profileTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  gatewayContainer: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#f0f0f0',
    paddingVertical: 10,
  },
  tab: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    backgroundColor: '#ffffff',
    marginHorizontal: 2,
    borderRadius: 5,
  },
  activeTab: {
    backgroundColor: '#2196F3',
  },
});

export default App;
