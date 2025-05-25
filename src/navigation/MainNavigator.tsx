import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
// import { useTranslation } from 'react-i18next';

// 导入屏幕组件
import { HomeScreen } from '../screens/main/HomeScreen';
import SuokeScreen from '../screens/suoke/SuokeScreen';
import LifeScreen from '../screens/life/LifeScreen';
import ProfileScreen from '../screens/profile/ProfileScreen';
import ExploreScreen from '../screens/explore/ExploreScreen';

// 导入详情屏幕
import { SettingsScreen } from '../screens/profile/SettingsScreen';

import { colors } from '../constants/theme';

// 主导航参数类型
export type MainTabParamList = {
  Home: undefined;
  Suoke: undefined;
  Explore: undefined;
  Life: undefined;
  Profile: undefined;
};

// 堆栈导航参数类型
export type MainStackParamList = {
  MainTabs: undefined;
  Settings: undefined;
};

const Tab = createBottomTabNavigator<MainTabParamList>();
const Stack = createNativeStackNavigator<MainStackParamList>();

// 图标渲染函数
const getTabBarIcon = ({ route, focused, color, size }: {
  route: any;
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
    default:
      iconName = 'help-circle-outline';
  }

  return <Icon name={iconName} size={size} color={color} />;
};

// 底部标签导航器
const MainTabNavigator: React.FC = () => {
  // const { t } = useTranslation();

  return (
    <Tab.Navigator
      initialRouteName="Home"
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ focused, color, size }) => 
          getTabBarIcon({ route, focused, color, size }),
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textSecondary,
        tabBarStyle: {
          backgroundColor: colors.surface,
          borderTopColor: colors.border,
          paddingBottom: 8,
          paddingTop: 8,
          height: 70,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '600',
        },
      })}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{
          tabBarLabel: '聊天',
        }}
      />

      <Tab.Screen
        name="Suoke"
        component={SuokeScreen}
        options={{
          tabBarLabel: 'SUOKE',
        }}
      />

      <Tab.Screen
        name="Explore"
        component={ExploreScreen}
        options={{
          tabBarLabel: '探索',
        }}
      />

      <Tab.Screen
        name="Life"
        component={LifeScreen}
        options={{
          tabBarLabel: 'LIFE',
        }}
      />

      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          tabBarLabel: '我的',
        }}
      />
    </Tab.Navigator>
  );
};

// 主导航器
export const MainNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      initialRouteName="MainTabs"
      screenOptions={{
        headerShown: false,
        animation: 'slide_from_right',
        gestureEnabled: true,
        gestureDirection: 'horizontal',
      }}
    >
      <Stack.Screen
        name="MainTabs"
        component={MainTabNavigator}
        options={{
          gestureEnabled: false,
        }}
      />

      <Stack.Screen
        name="Settings"
        component={SettingsScreen}
        options={{
          animation: 'slide_from_right',
        }}
      />
    </Stack.Navigator>
  );
};
