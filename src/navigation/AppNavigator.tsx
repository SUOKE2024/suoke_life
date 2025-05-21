import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useTheme } from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useSelector } from 'react-redux';

// 导入屏幕组件
import HomeScreen from '../screens/home/HomeScreen';
import SuokeScreen from '../screens/suoke/SuokeScreen';
import ExploreScreen from '../screens/explore/ExploreScreen';
import LifeScreen from '../screens/life/LifeScreen';
import ProfileScreen from '../screens/profile/ProfileScreen';
import LoginScreen from '../screens/auth/LoginScreen';
import RegisterScreen from '../screens/auth/RegisterScreen';
import DiagnosisScreen from '../screens/home/DiagnosisScreen';
import DiagnosisResultScreen from '../screens/home/DiagnosisResultScreen';

// 导入类型
import { RootState } from '../store';

// 定义导航栈参数类型
export type RootStackParamList = {
  Main: undefined;
  Login: undefined;
  Register: undefined;
  Diagnosis: undefined;
  DiagnosisResult: { sessionId: string };
};

export type MainTabParamList = {
  Home: undefined;
  Suoke: undefined;
  Explore: undefined;
  Life: undefined;
  Profile: undefined;
};

// 创建导航栈
const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<MainTabParamList>();

/**
 * 主标签导航
 * 包含应用的五个主要标签页
 */
const MainTabNavigator: React.FC = () => {
  const theme = useTheme();
  
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: theme.colors.disabled,
        tabBarStyle: { 
          height: 60,
          paddingBottom: 8,
          paddingTop: 8
        },
        headerShown: false
      }}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen} 
        options={{
          title: '首页',
          tabBarIcon: ({ color, size }) => (
            <Icon name="home" color={color} size={size} />
          ),
        }}
      />
      <Tab.Screen 
        name="Suoke" 
        component={SuokeScreen} 
        options={{
          title: '索克',
          tabBarIcon: ({ color, size }) => (
            <Icon name="shopping" color={color} size={size} />
          ),
        }}
      />
      <Tab.Screen 
        name="Explore" 
        component={ExploreScreen} 
        options={{
          title: '探索',
          tabBarIcon: ({ color, size }) => (
            <Icon name="compass" color={color} size={size} />
          ),
        }}
      />
      <Tab.Screen 
        name="Life" 
        component={LifeScreen} 
        options={{
          title: '生活',
          tabBarIcon: ({ color, size }) => (
            <Icon name="heart" color={color} size={size} />
          ),
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen} 
        options={{
          title: '我的',
          tabBarIcon: ({ color, size }) => (
            <Icon name="account" color={color} size={size} />
          ),
        }}
      />
    </Tab.Navigator>
  );
};

/**
 * 根导航器
 * 负责整个应用的导航结构和认证流程
 */
const AppNavigator: React.FC = () => {
  // 从Redux获取认证状态
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);
  
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false
      }}
    >
      {isAuthenticated ? (
        // 已认证用户的导航栈
        <>
          <Stack.Screen name="Main" component={MainTabNavigator} />
          <Stack.Screen 
            name="Diagnosis" 
            component={DiagnosisScreen} 
            options={{
              headerShown: true,
              title: '四诊辨证',
              animation: 'slide_from_right'
            }}
          />
          <Stack.Screen 
            name="DiagnosisResult" 
            component={DiagnosisResultScreen} 
            options={{
              headerShown: true,
              title: '体质辨识结果',
              animation: 'slide_from_right'
            }}
          />
        </>
      ) : (
        // 未认证用户的导航栈
        <>
          <Stack.Screen name="Login" component={LoginScreen} />
          <Stack.Screen name="Register" component={RegisterScreen} />
        </>
      )}
    </Stack.Navigator>
  );
};

export default AppNavigator; 