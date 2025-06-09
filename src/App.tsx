import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import React, { Suspense, useEffect, useState } from 'react';
import {
    Alert,
    StatusBar,
    StyleSheet,
    Text,
    View,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { APP_CONFIG, getCurrentEnvConfig } from './constants/config';
import { ApiServiceProvider } from './services/IntegratedApiService';

// 懒加载屏幕组件
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

// 懒加载网关组件
const GatewayMonitor = React.lazy(() => import('./components/common/GatewayMonitor'));
const GatewayConfig = React.lazy(() => import('./components/common/GatewayConfig'));
const AnalyticsDashboard = React.lazy(() => import('./components/common/AnalyticsDashboard'));
const GatewayConfigManager = React.lazy(() => import('./components/common/GatewayConfigManager'));

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
  }, []);

  const checkAppStatus = async () => {
    try {
      // 检查环境配置
      const config = getCurrentEnvConfig();
      console.log('App starting with config:', {
        environment: APP_CONFIG.ENVIRONMENT,
        gatewayUrl: config.GATEWAY_URL,
        features: Object.entries(config)
          .filter(([key, value]) => key.startsWith('ENABLE_') && value)
          .map(([key]) => key),
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
      Alert.alert('初始化错误', errorMessage, [
        { text: '重试', onPress: checkAppStatus },
        { text: '继续', onPress: () => setIsReady(true) },
      ]);
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

// 加载组件
const LoadingFallback = () => (
  <View style={styles.loadingContainer}>
    <Icon name="hourglass-empty" size={48} color="#2196F3" />
    <Text style={styles.loadingText}>正在加载...</Text>
  </View>
);

// 主应用组件
const App: React.FC = () => {
  return (
    <ApiServiceProvider>
      <AppStatusChecker>
        <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
        <NavigationContainer>
          <Suspense fallback={<LoadingFallback />}>
            <MainTabs />
          </Suspense>
        </NavigationContainer>
      </AppStatusChecker>
    </ApiServiceProvider>
  );
};

// 样式定义
const styles = StyleSheet.create({
  gatewayContainer: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#ffffff',
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  tab: {
    flex: 1,
    textAlign: 'center',
    paddingVertical: 8,
    paddingHorizontal: 12,
    marginHorizontal: 4,
    borderRadius: 6,
    backgroundColor: '#f0f0f0',
    color: '#666666',
    fontSize: 14,
    fontWeight: '500',
  },
  activeTab: {
    backgroundColor: '#2196F3',
    color: '#ffffff',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#ffffff',
  },
  errorTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#f44336',
    marginTop: 16,
    marginBottom: 8,
  },
  errorMessage: {
    fontSize: 14,
    color: '#666666',
    textAlign: 'center',
    lineHeight: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
  },
  loadingText: {
    fontSize: 16,
    color: '#2196F3',
    marginTop: 16,
    fontWeight: '500',
  },
});

export default App;
