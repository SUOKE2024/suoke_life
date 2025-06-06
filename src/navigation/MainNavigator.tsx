import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
const Icon = React.lazy(() => import('../components/common/Icon'));
import { HomeScreen } from '../screens/main';
const SuokeScreen = React.lazy(() => import('../screens/suoke/SuokeScreen'));
const LifeScreen = React.lazy(() => import('../screens/life/LifeScreen'));
const ProfileScreen = React.lazy(() => import('../screens/profile/ProfileScreen'));
const ExploreScreen = React.lazy(() => import('../screens/explore/ExploreScreen'));
import { MazeNavigator } from './MazeNavigator';
import { SettingsScreen } from '../screens/profile/SettingsScreen';
import { ServiceStatusScreen } from '../screens/profile/ServiceStatusScreen';
import { ServiceManagementScreen } from '../screens/profile/ServiceManagementScreen';
import { DeveloperPanelScreen } from '../screens/profile/DeveloperPanelScreen';
import { ApiIntegrationDemo } from '../screens/demo/ApiIntegrationDemo';
import { BenchmarkScreen } from '../screens/benchmark/BenchmarkScreen';
import { colors } from '../constants/theme';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor';

// 主导航参数类型
export type MainTabParamList = {Home: undefined;
  Suoke: undefined;
  Explore: undefined;
  Life: undefined;
  Profile: undefined;
  Maze: undefined;
  Benchmark: undefined;
};

// 堆栈导航参数类型
export type MainStackParamList = {MainTabs: undefined;
  Settings: undefined;
  ServiceStatus: undefined;
  ServiceManagement: undefined;
  DeveloperPanel: undefined;
  ApiIntegrationDemo: undefined;
  Benchmark: undefined;
};

const Tab = createBottomTabNavigator<MainTabParamList>();
const Stack = createNativeStackNavigator<MainStackParamList>();

// 图标渲染函数
const getTabBarIcon = ({route,focused,color,size;
}: {route: any;
  focused: boolean;
  color: string;
  size: number;
}) => {
  let iconName: string;

  switch (route.name) {
    case 'Home':
      iconName = focused ? 'chat' : 'chat-outline';
      break;
    case 'Suoke':
      iconName = focused ? 'stethoscope' : 'stethoscope';
      break;
    case 'Explore':
      iconName = focused ? 'compass' : 'compass-outline';
      break;
    case 'Life':
      iconName = focused ? 'heart-pulse' : 'heart-outline';
      break;
    case 'Profile':
      iconName = focused ? 'account' : 'account-outline';
      break;
    case 'Maze':
      iconName = focused ? 'maze' : 'maze';
      break;
    case 'Benchmark':
      iconName = focused ? 'speedometer' : 'speedometer-slow';
      break;
    default:
      iconName = 'help-circle-outline';
  }

  return <Icon name={iconName} size={size} color={color} />;
};

// 底部标签导航器
const MainTabNavigator: React.FC = () => {
  // 性能监控
  const metrics = usePerformanceMonitor({componentName: 'MainNavigator',enableMemoryMonitoring: false,threshold: 100;
  });

  return (
    <Tab.Navigator
      initialRouteName='Home'
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ focused, color, size }) => getTabBarIcon({ route, focused, color, size }),
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textSecondary,
        tabBarStyle: {
          backgroundColor: colors.surface,
          borderTopColor: colors.border,
          paddingBottom: 8,
          paddingTop: 8,
          height: 70
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '600'
        }
      })}
    >;
      <Tab.Screen name='Home' component={HomeScreen} options={{ tabBarLabel: '聊天' }} />;
      <Tab.Screen name='Suoke' component={SuokeScreen} options={{ tabBarLabel: 'SUOKE' }} />;
      <Tab.Screen name='Explore' component={ExploreScreen} options={{ tabBarLabel: '探索' }} />;
      <Tab.Screen name='Life' component={LifeScreen} options={{ tabBarLabel: 'LIFE' }} />;
      <Tab.Screen;
        name='Maze';
        component={MazeNavigator};
        options={{tabBarLabel: '迷宫',headerShown: false;
        }};
      />;
      <Tab.Screen name='Benchmark' component={BenchmarkScreen} options={{ tabBarLabel: '评测' }} />;
      <Tab.Screen name='Profile' component={ProfileScreen} options={{ tabBarLabel: '我的' }} />;
    </Tab.Navigator>;
  );
};

// 主导航器
export const MainNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      initialRouteName='MainTabs'
      screenOptions={{
        headerShown: false,
        animation: 'slide_from_right',
        gestureEnabled: true,
        gestureDirection: 'horizontal'
      }}
    >
      <Stack.Screen
        name='MainTabs'
        component={MainTabNavigator}
        options={{ gestureEnabled: false }}
      />
      <Stack.Screen
        name='Settings'
        component={SettingsScreen}
        options={{ animation: 'slide_from_right' }}
      />
      <Stack.Screen
        name='ServiceStatus'
        component={ServiceStatusScreen}
        options={{ animation: 'slide_from_right' }}
      />
      <Stack.Screen
        name='ServiceManagement'
        component={ServiceManagementScreen}
        options={{ animation: 'slide_from_right' }}
      />
      <Stack.Screen;
        name='DeveloperPanel';
        component={DeveloperPanelScreen};
        options={{ animation: 'slide_from_right' }};
      />;
      <Stack.Screen;
        name='ApiIntegrationDemo';
        component={ApiIntegrationDemo};
        options={{ animation: 'slide_from_right' }};
      />;
      <Stack.Screen;
        name='Benchmark';
        component={BenchmarkScreen};
        options={{ animation: 'slide_from_right' }};
      />;
    </Stack.Navigator>;
  );
};
