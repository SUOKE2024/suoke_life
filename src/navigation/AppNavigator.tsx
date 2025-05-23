import React, { useEffect } from 'react';
import { useColorScheme, View, Text } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useTheme } from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';
import { AnyAction } from '@reduxjs/toolkit';

import { initializeAuth } from '../store/slices/userSlice';

// 导入屏幕
import HomeScreen from '../screens/home/HomeScreen';
import ExploreScreen from '../screens/explore/ExploreScreen';
import LifeScreen from '../screens/life/LifeScreen';
import SuokeScreen from '../screens/suoke/SuokeScreen';
import ProfileScreen from '../screens/profile/ProfileScreen';
import LoginScreen from '../screens/auth/LoginScreen';
import RegisterScreen from '../screens/auth/RegisterScreen';
// import ForgotPasswordScreen from '../screens/auth/ForgotPasswordScreen';

// 导入智能体相关页面
import AgentSelection from '../features/agents/AgentSelection';
import AgentChannel from '../features/agents/AgentChannel';
import AgentCollaboration from '../features/agents/AgentCollaboration';
import ChatHistoryScreen from '../screens/agents/ChatHistoryScreen';

// 导入新增页面
import ArticleDetailScreen from '../screens/explore/ArticleDetailScreen';
import HealthAssessmentScreen from '../screens/suoke/HealthAssessmentScreen';
import LifeRecordScreen from '../screens/life/LifeRecordScreen';
import ProfileSettingsScreen from '../screens/profile/ProfileSettingsScreen';
import FourDiagnosisSystem from '../components/medical/FourDiagnosisSystem';
import HealthDataChartScreen from '../screens/common/HealthDataChartScreen';
import HealthPlanScreen from '../screens/common/HealthPlanScreen';

// 定义认证栈的参数类型
export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
};

// 定义主应用栈的参数类型
export type AppStackParamList = {
  Main: undefined;
  Auth: undefined;
  AgentSelection: undefined;
  AgentChannel: { agentType: string };
  AgentCollaboration: undefined;
  ChatHistory: undefined;
  ArticleDetail: { articleId: string };
  HealthAssessment: undefined;
  LifeRecord: undefined;
  ProfileSettings: undefined;
  FourDiagnosisSystem: undefined;
  HealthDataChart: undefined;
  HealthPlan: undefined;
  XiaoaiChat: undefined;
  XiaoaiFourDiagnosis: undefined;
  XiaoaiHealthRecords: undefined;
  XiaoaiConstitution: undefined;
  XiaokeMedicalResources: undefined;
  XiaokeAppointments: undefined;
  XiaokeCustomProducts: undefined;
  XiaokeProductTrace: undefined;
  XiaokeProductRecommendations: undefined;
  LaokeKnowledge: undefined;
  LaokeLearningPath: undefined;
  LaokeCommunity: undefined;
  LaokeGames: undefined;
  SoerHealthPlan: undefined;
  SoerNutrition: undefined;
  SoerSensorData: undefined;
  SoerSleep: undefined;
  SoerEmotions: undefined;
  HealthAnalysisFlow: undefined;
  SeasonalCareFlow: undefined;
  ChronicManagementFlow: undefined;
  FamilyHealthFlow: undefined;
};

// 定义底部标签的参数类型
export type TabParamList = {
  Home: undefined;
  Explore: undefined;
  Life: undefined;
  Suoke: undefined;
  Profile: undefined;
};

// 创建导航器
const Tab = createBottomTabNavigator<TabParamList>();
const AuthStack = createNativeStackNavigator<AuthStackParamList>();
const AppStack = createNativeStackNavigator<AppStackParamList>();

// 临时占位组件（待实现的屏幕）
const PlaceholderScreen = () => {
  const theme = useTheme();
  return (
    <View style={{ 
      flex: 1, 
      justifyContent: 'center', 
      alignItems: 'center',
      backgroundColor: theme.colors.background
    }}>
      <Text style={{ color: theme.colors.primary, fontSize: 18 }}>
        此功能正在开发中...
      </Text>
    </View>
  );
};

// 临时占位组件（待实现的屏幕）
const ForgotPasswordScreen = PlaceholderScreen;

// 认证堆栈导航器
const AuthNavigator = () => {
  const { t } = useTranslation();
  
  return (
    <AuthStack.Navigator 
      screenOptions={{ 
        headerShown: false,
        animation: 'slide_from_right'
      }}
    >
      <AuthStack.Screen name="Login" component={LoginScreen} />
      <AuthStack.Screen name="Register" component={RegisterScreen} />
      <AuthStack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
    </AuthStack.Navigator>
  );
};

// 主标签导航器
const TabNavigator = () => {
  const theme = useTheme();
  const { t } = useTranslation();
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';
  
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: isDark ? '#888' : '#666',
        tabBarStyle: {
          paddingBottom: 5,
          paddingTop: 5,
          height: 60,
          backgroundColor: theme.colors.background,
          borderTopColor: theme.colors.outline,
        },
        tabBarIcon: ({ focused, color, size }) => {
          let iconName = '';
          
          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Explore') {
            iconName = focused ? 'compass' : 'compass-outline';
          } else if (route.name === 'Life') {
            iconName = focused ? 'sprout' : 'sprout-outline';
          } else if (route.name === 'Suoke') {
            iconName = focused ? 'flower-tulip' : 'flower-tulip-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'account' : 'account-outline';
          }
          
          return <Icon name={iconName} size={size} color={color} />;
        },
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen} 
        options={{ tabBarLabel: t('home.title') }} 
      />
      <Tab.Screen 
        name="Explore" 
        component={ExploreScreen} 
        options={{ tabBarLabel: t('home.explore') }}
      />
      <Tab.Screen 
        name="Life" 
        component={LifeScreen} 
        options={{ tabBarLabel: t('home.life') }}
      />
      <Tab.Screen 
        name="Suoke" 
        component={SuokeScreen} 
        options={{ tabBarLabel: t('home.suoke') }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen} 
        options={{ tabBarLabel: t('home.profile') }}
      />
    </Tab.Navigator>
  );
};

// 主应用导航器
const AppNavigator = () => {
  const dispatch = useDispatch();
  const { currentUser } = useSelector((state: any) => state.user);
  
  // 初始化认证状态
  useEffect(() => {
    dispatch(initializeAuth() as unknown as AnyAction);
  }, [dispatch]);
  
  return (
    <AppStack.Navigator screenOptions={{ headerShown: false }}>
      {currentUser ? (
        <>
          <AppStack.Screen name="Main" component={TabNavigator} />
                      {/* 智能体相关页面 */}
            <AppStack.Screen name="AgentSelection" component={AgentSelection} />
            <AppStack.Screen name="AgentChannel" component={AgentChannel} />
            <AppStack.Screen name="AgentCollaboration" component={AgentCollaboration} />
            <AppStack.Screen name="ChatHistory" component={ChatHistoryScreen} />
            
            {/* 新增功能页面 */}
            <AppStack.Screen name="ArticleDetail" component={ArticleDetailScreen} />
            <AppStack.Screen name="HealthAssessment" component={HealthAssessmentScreen} />
            <AppStack.Screen name="LifeRecord" component={LifeRecordScreen} />
            <AppStack.Screen name="ProfileSettings" component={ProfileSettingsScreen} />
            <AppStack.Screen name="FourDiagnosisSystem" component={FourDiagnosisSystem} />
            <AppStack.Screen name="HealthDataChart" component={HealthDataChartScreen} />
            <AppStack.Screen name="HealthPlan" component={HealthPlanScreen} />
          
          {/* 智能体功能页面（后续需要实现） */}
          <AppStack.Group screenOptions={{ presentation: 'card' }}>
            {/* 小艾功能页面 */}
            <AppStack.Screen name="XiaoaiChat" component={PlaceholderScreen} />
            <AppStack.Screen name="XiaoaiFourDiagnosis" component={PlaceholderScreen} />
            <AppStack.Screen name="XiaoaiHealthRecords" component={PlaceholderScreen} />
            <AppStack.Screen name="XiaoaiConstitution" component={PlaceholderScreen} />
            
            {/* 小克功能页面 */}
            <AppStack.Screen name="XiaokeMedicalResources" component={PlaceholderScreen} />
            <AppStack.Screen name="XiaokeAppointments" component={PlaceholderScreen} />
            <AppStack.Screen name="XiaokeCustomProducts" component={PlaceholderScreen} />
            <AppStack.Screen name="XiaokeProductTrace" component={PlaceholderScreen} />
            <AppStack.Screen name="XiaokeProductRecommendations" component={PlaceholderScreen} />
            
            {/* 老克功能页面 */}
            <AppStack.Screen name="LaokeKnowledge" component={PlaceholderScreen} />
            <AppStack.Screen name="LaokeLearningPath" component={PlaceholderScreen} />
            <AppStack.Screen name="LaokeCommunity" component={PlaceholderScreen} />
            <AppStack.Screen name="LaokeGames" component={PlaceholderScreen} />
            
            {/* 索儿功能页面 */}
            <AppStack.Screen name="SoerHealthPlan" component={PlaceholderScreen} />
            <AppStack.Screen name="SoerNutrition" component={PlaceholderScreen} />
            <AppStack.Screen name="SoerSensorData" component={PlaceholderScreen} />
            <AppStack.Screen name="SoerSleep" component={PlaceholderScreen} />
            <AppStack.Screen name="SoerEmotions" component={PlaceholderScreen} />
            
            {/* 协作流程页面 */}
            <AppStack.Screen name="HealthAnalysisFlow" component={PlaceholderScreen} />
            <AppStack.Screen name="SeasonalCareFlow" component={PlaceholderScreen} />
            <AppStack.Screen name="ChronicManagementFlow" component={PlaceholderScreen} />
            <AppStack.Screen name="FamilyHealthFlow" component={PlaceholderScreen} />
          </AppStack.Group>
        </>
      ) : (
        <AppStack.Screen name="Auth" component={AuthNavigator} />
      )}
    </AppStack.Navigator>
  );
};

export default AppNavigator; 