import React from 'react';
import { View, Text } from 'react-native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialIcons';

// 导入屏幕组件
import LifeScreen from '../screens/life/LifeScreen';
import MedicalResourceScreen from '../screens/health/MedicalResourceScreen';
import MedicalResourceDetailScreen from '../screens/health/MedicalResourceDetailScreen';
import AppointmentScreen from '../screens/health/AppointmentScreen';
import { MedKnowledgeScreen } from '../screens/health/MedKnowledgeScreen';

// 类型定义
export type HealthTabParamList = {
  LifeOverview: undefined;
  MedicalResource: undefined;
  Appointment: undefined;
  MedKnowledge: undefined;
};

export type HealthStackParamList = {
  HealthTabs: undefined;
  MedicalResourceDetail: {
    resourceId: string;
    reschedule?: boolean;
  };
  AppointmentDetail: {
    appointmentId: string;
  };
};

const Tab = createBottomTabNavigator<HealthTabParamList>();
const Stack = createStackNavigator<HealthStackParamList>();

// 健康标签页导航器
const HealthTabNavigator: React.FC = () => {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: '#666',
        tabBarStyle: {
          backgroundColor: '#fff',
          elevation: 4,
          shadowColor: '#000',
          shadowOffset: { width: 0, height: 2 },
          shadowOpacity: 0.1,
          shadowRadius: 4,
          paddingBottom: 8,
          paddingTop: 8,
          height: 70,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '600',
        },
      }}
    >
      <Tab.Screen
        name="LifeOverview"
        component={LifeScreen}
        options={{
          tabBarLabel: '生活',
          tabBarIcon: ({ color, focused }) => (
            <Icon
              name={focused ? 'favorite' : 'favorite-border'}
              size={20}
              color={color}
            />
          ),
        }}
      />
      
      <Tab.Screen
        name="MedicalResource"
        component={MedicalResourceScreen}
        options={{
          tabBarLabel: '医疗资源',
          tabBarIcon: ({ color, focused }) => (
            <Icon
              name={focused ? 'local-hospital' : 'local-hospital'}
              size={20}
              color={color}
            />
          ),
        }}
      />
      
      <Tab.Screen
        name="Appointment"
        component={AppointmentScreen}
        options={{
          tabBarLabel: '我的预约',
          tabBarIcon: ({ color, focused }) => (
            <Icon
              name={focused ? 'event' : 'event-note'}
              size={20}
              color={color}
            />
          ),
        }}
      />
      
      <Tab.Screen
        name="MedKnowledge"
        component={MedKnowledgeScreen}
        options={{
          tabBarLabel: '医学知识',
          tabBarIcon: ({ color, focused }) => (
            <Icon
              name={focused ? 'menu-book' : 'book'}
              size={20}
              color={color}
            />
          ),
        }}
      />
    </Tab.Navigator>
  );
};

// 健康堆栈导航器
export const HealthNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        cardStyleInterpolator: ({ current, layouts }) => {
          return {
            cardStyle: {
              transform: [
                {
                  translateX: current.progress.interpolate({
                    inputRange: [0, 1],
                    outputRange: [layouts.screen.width, 0],
                  }),
                },
              ],
            },
          };
        },
      }}
    >
      <Stack.Screen
        name="HealthTabs"
        component={HealthTabNavigator}
        options={{
          gestureEnabled: false,
        }}
      />
      
      <Stack.Screen
        name="MedicalResourceDetail"
        component={MedicalResourceDetailScreen}
        options={{
          headerShown: true,
          headerTitle: '医疗资源详情',
          headerBackTitle: '返回',
          headerTintColor: '#007AFF',
          headerStyle: {
            backgroundColor: '#fff',
            shadowColor: '#000',
            shadowOffset: { width: 0, height: 1 },
            shadowOpacity: 0.1,
            shadowRadius: 2,
            elevation: 2,
          },
          headerTitleStyle: {
            fontSize: 18,
            fontWeight: '600',
            color: '#333',
          },
        }}
      />
      
      <Stack.Screen
        name="AppointmentDetail"
        component={AppointmentDetailScreen}
        options={{
          headerShown: true,
          headerTitle: '预约详情',
          headerBackTitle: '返回',
          headerTintColor: '#007AFF',
          headerStyle: {
            backgroundColor: '#fff',
            shadowColor: '#000',
            shadowOffset: { width: 0, height: 1 },
            shadowOpacity: 0.1,
            shadowRadius: 2,
            elevation: 2,
          },
          headerTitleStyle: {
            fontSize: 18,
            fontWeight: '600',
            color: '#333',
          },
        }}
      />
    </Stack.Navigator>
  );
};

// 预约详情屏幕（简单实现）
const AppointmentDetailScreen: React.FC<{ navigation: any; route: any }> = ({
  navigation,
  route,
}) => {
  const { appointmentId } = route.params;
  
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>预约详情屏幕</Text>
      <Text>预约ID: {appointmentId}</Text>
    </View>
  );
};

export default HealthNavigator; 