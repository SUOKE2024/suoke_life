import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { View, Text, StyleSheet, Alert } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';

// 导入服务提供者
import { ApiServiceProvider } from './services/IntegratedApiService';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { OfflineIndicator } from './components/common/OfflineIndicator';

// 导入屏幕组件
const HomeScreen = React.lazy(() => import('./screens/main/HomeScreen'));
const LifeOverviewScreen = React.lazy(() => import('./screens/health/LifeOverviewScreen'));
const FiveDiagnosisAgentIntegrationScreen = React.lazy(() => import('./screens/demo/FiveDiagnosisAgentIntegrationScreen'));
const ExploreScreen = React.lazy(() => import('./screens/explore/ExploreScreen'));

// 临时创建简单的ProfileScreen组件
const ProfileScreen = () => (
  <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
    <Text>个人资料页面</Text>
  </View>
);

// 导入网关组件
const GatewayMonitor = React.lazy(() => import('./components/common/GatewayMonitor'));
const GatewayConfig = React.lazy(() => import('./components/common/GatewayConfig'));
const AnalyticsDashboard = React.lazy(() => import('./components/common/AnalyticsDashboard'));
const GatewayConfigManager = React.lazy(() => import('./components/common/GatewayConfigManager'));

// 导入配置
import { APP_CONFIG, getCurrentEnvConfig } from './constants/config';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// 网关管理屏幕
const GatewayManagementScreen = () => {
  const [activeTab, setActiveTab] = useState<'monitor' | 'config' | 'analytics' | 'settings'>('monitor');

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
      {/* 标签切换 */}
      <View style={styles.tabContainer}>
        <Text
          style={[styles.tab, activeTab === 'monitor' && styles.activeTab]}
          onPress={() => setActiveTab('monitor')}
        >
          监控
        </Text>
        <Text
          style={[styles.tab, activeTab === 'config' && styles.activeTab]}
          onPress={() => setActiveTab('config')}
        >
          配置
        </Text>
        <Text
          style={[styles.tab, activeTab === 'analytics' && styles.activeTab]}
          onPress={() => setActiveTab('analytics')}
        >
          分析
        </Text>
        <Text
          style={[styles.tab, activeTab === 'settings' && styles.activeTab]}
          onPress={() => setActiveTab('settings')}
        >
          设置
        </Text>
      </View>

      {/* 内容区域 */}
      {renderContent()}
    </View>
  );
};

// 主标签导航
const MainTabs = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: string;

          switch (route.name) {
            case 'Main':
              iconName = 'home';
              break;
            case 'Health':
              iconName = 'favorite';
              break;
            case 'Diagnosis':
              iconName = 'healing';
              break;
            case 'Explore':
              iconName = 'explore';
              break;
            case 'Profile':
              iconName = 'person';
              break;
            case 'Gateway':
              iconName = 'settings';
              break;
            default:
              iconName = 'help';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
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
        options={{ title: '四诊' }}
      />
      <Tab.Screen
        name="Explore"
        component={ExploreScreen}
        options={{ title: '探索' }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{ title: '我的' }}
      />
      {/* 开发环境显示网关管理 */}
      {APP_CONFIG.ENVIRONMENT === 'development' && (
        <Tab.Screen
          name="Gateway"
          component={GatewayManagementScreen}
          options={{ title: '网关' }}
        />
      )}
    </Tab.Navigator>
  );
};

// 应用状态检查组件
const AppStatusChecker: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkAppStatus();
  }, []);  // 检查是否需要添加依赖项;

  const checkAppStatus = async () => {
    try {
      // 检查环境配置
      const config = getCurrentEnvConfig();
      console.log('App starting with config:', {
        environment: APP_CONFIG.ENVIRONMENT,
        gatewayUrl: config.GATEWAY_URL,
        features: Object.entries(config).filter(([key, value]) =>
          key.startsWith('ENABLE_') && value,
        ).map(([key]) => key),
      });

      // 在开发环境中进行额外检查
      if (APP_CONFIG.ENVIRONMENT === 'development') {
        console.log('Development mode: Gateway monitoring enabled');
      }

      setIsReady(true);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '应用初始化失败';
      setError(errorMessage);
      console.error('App initialization error:', err);

      Alert.alert(
        '初始化错误',
        errorMessage,
        [
          { text: '重试', onPress: checkAppStatus },
          { text: '继续', onPress: () => setIsReady(true) },
        ],
      );
    }
  };

  if (error && !isReady) {
    return (
      <View style={styles.errorContainer}>
        <Icon name="error" size={48} color="#f44336" />
        <Text style={styles.errorTitle}>应用启动失败</Text>
        <Text style={styles.errorMessage}>{error}</Text>
      </View>
    );
  }

  if (!isReady) {
    return (
      <View style={styles.loadingContainer}>
        <Icon name="hourglass-empty" size={48} color="#2196F3" />
        <Text style={styles.loadingText}>正在初始化索克生活...</Text>
      </View>
    );
  }

  return <>{children}</>;
};

// 主应用组件
const App: React.FC = () => {
  return (
    <ErrorBoundary
      onError={(error) => {
        console.error('App-level error:', error);
        // 这里可以发送错误报告到监控服务
      }}
    >
      <ApiServiceProvider>
        <AppStatusChecker>
          <NavigationContainer>
            <Stack.Navigator screenOptions={{ headerShown: false }}>
              <Stack.Screen name="MainTabs" component={MainTabs} />
            </Stack.Navigator>
            {/* 离线状态指示器 */}
            <OfflineIndicator />
          </NavigationContainer>
        </AppStatusChecker>
      </ApiServiceProvider>
    </ErrorBoundary>
  );
};

const styles = StyleSheet.create({
  gatewayContainer: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  tab: {
    flex: 1,
    textAlign: 'center',
    paddingVertical: 16,
    fontSize: 16,
    fontWeight: '500',
    color: '#666',
  },
  activeTab: {
    color: '#2196F3',
    borderBottomWidth: 2,
    borderBottomColor: '#2196F3',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 20,
  },
  errorTitle: {
    marginTop: 16,
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
  },
  errorMessage: {
    marginTop: 8,
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    lineHeight: 20,
  },
});

export default App;
