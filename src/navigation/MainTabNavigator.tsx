import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { View, Text, StyleSheet } from 'react-native';

// 导入屏幕组件
import HomeScreen from '../screens/main/HomeScreen';
import SuokeScreen from '../screens/main/SuokeScreen';
import ExploreScreen from '../screens/main/ExploreScreen';
import LifeScreen from '../screens/main/LifeScreen';
import ProfileScreen from '../screens/main/ProfileScreen';

const Tab = createBottomTabNavigator();

// 占位符组件
const PlaceholderScreen: React.FC<{ title: string; description: string }> = ({ title, description }) => (
  <View style={styles.placeholderContainer}>
    <Icon name="construction" size={80} color="#ccc" />
    <Text style={styles.placeholderTitle}>{title}</Text>
    <Text style={styles.placeholderDescription}>{description}</Text>
  </View>
);

const SuokeScreenPlaceholder = () => (
  <PlaceholderScreen 
    title="SUOKE" 
    description="智能体协作中心，四大智能体协同工作平台" 
  />
);

const ExploreScreenPlaceholder = () => (
  <PlaceholderScreen 
    title="探索" 
    description="发现健康知识、中医文化和养生资讯" 
  />
);

const LifeScreenPlaceholder = () => (
  <PlaceholderScreen 
    title="LIFE" 
    description="生活方式管理、健康数据和个人档案" 
  />
);

const ProfileScreenPlaceholder = () => (
  <PlaceholderScreen 
    title="我的" 
    description="个人设置、账户管理和系统配置" 
  />
);

const MainTabNavigator: React.FC = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: string;

          switch (route.name) {
            case 'Chat':
              iconName = 'chat';
              break;
            case 'Suoke':
              iconName = 'smart-toy';
              break;
            case 'Explore':
              iconName = 'explore';
              break;
            case 'Life':
              iconName = 'favorite';
              break;
            case 'Profile':
              iconName = 'person';
              break;
            default:
              iconName = 'help';
          }

          return (
            <View style={styles.tabIconContainer}>
              <Icon name={iconName} size={size} color={color} />
              {focused && <View style={styles.activeIndicator} />}
            </View>
          );
        },
        tabBarActiveTintColor: '#2196F3',
        tabBarInactiveTintColor: '#999',
        tabBarStyle: {
          backgroundColor: '#ffffff',
          borderTopWidth: 1,
          borderTopColor: '#f0f0f0',
          height: 60,
          paddingBottom: 8,
          paddingTop: 8,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
          marginTop: 4,
        },
        headerShown: false,
      })}
    >
      <Tab.Screen
        name="Chat"
        component={HomeScreen}
        options={{
          tabBarLabel: '聊天',
          tabBarBadge: undefined, // 可以动态设置未读消息数量
        }}
      />
      <Tab.Screen
        name="Suoke"
        component={SuokeScreenPlaceholder}
        options={{
          tabBarLabel: 'SUOKE',
        }}
      />
      <Tab.Screen
        name="Explore"
        component={ExploreScreenPlaceholder}
        options={{
          tabBarLabel: '探索',
        }}
      />
      <Tab.Screen
        name="Life"
        component={LifeScreenPlaceholder}
        options={{
          tabBarLabel: 'LIFE',
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreenPlaceholder}
        options={{
          tabBarLabel: '我的',
        }}
      />
    </Tab.Navigator>
  );
};

const styles = StyleSheet.create({
  tabIconContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  activeIndicator: {
    position: 'absolute',
    bottom: -8,
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#2196F3',
  },
  placeholderContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    paddingHorizontal: 40,
  },
  placeholderTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 20,
    marginBottom: 12,
  },
  placeholderDescription: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
  },
});

export default MainTabNavigator;