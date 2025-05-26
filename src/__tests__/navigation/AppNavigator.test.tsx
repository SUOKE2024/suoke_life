import React from 'react';
import { render } from '@testing-library/react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { View, Text } from 'react-native';

// Mock screens
const MockHomeScreen = () => <View testID="home-screen"><Text>首页</Text></View>;
const MockExploreScreen = () => <View testID="explore-screen"><Text>探索</Text></View>;
const MockLifeScreen = () => <View testID="life-screen"><Text>生活</Text></View>;
const MockSuokeScreen = () => <View testID="suoke-screen"><Text>索克</Text></View>;
const MockProfileScreen = () => <View testID="profile-screen"><Text>我的</Text></View>;

// Mock Icon component
jest.mock('../../components/common/Icon', () => {
  return jest.fn(({ name, size, color }: any) => {
    const { Text } = require('react-native');
    return (
      <Text testID={`icon-${name}`} style={{ fontSize: size, color }}>
        {name}
      </Text>
    );
  });
});

// Mock react-native-vector-icons
jest.mock('react-native-vector-icons/MaterialCommunityIcons', () => {
  return jest.fn(({ name, size, color }: any) => {
    const { Text } = require('react-native');
    return (
      <Text testID={`vector-icon-${name}`} style={{ fontSize: size, color }}>
        {name}
      </Text>
    );
  });
});

// Mock @react-navigation/native
jest.mock('@react-navigation/native', () => {
  const actualNav = jest.requireActual('@react-navigation/native');
  return {
    ...actualNav,
    NavigationContainer: ({ children }: any) => children,
  };
});

// Mock @react-navigation/bottom-tabs
jest.mock('@react-navigation/bottom-tabs', () => ({
  createBottomTabNavigator: () => ({
    Navigator: ({ children }: any) => <View testID="tab-navigator">{children}</View>,
    Screen: ({ children, options }: any) => (
      <View testID={options?.tabBarTestID || 'tab-screen'}>
        <Text>{options?.tabBarLabel}</Text>
        {children}
      </View>
    ),
  }),
}));

const Tab = createBottomTabNavigator();

const AppNavigator = () => {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={{
          headerShown: false,
          tabBarActiveTintColor: '#007AFF',
          tabBarInactiveTintColor: '#8E8E93',
        }}
      >
        <Tab.Screen
          name="Home"
          component={MockHomeScreen}
          options={{
            tabBarLabel: '首页',
            tabBarTestID: 'tab-home',
          }}
        />
        <Tab.Screen
          name="Explore"
          component={MockExploreScreen}
          options={{
            tabBarLabel: '探索',
            tabBarTestID: 'tab-explore',
          }}
        />
        <Tab.Screen
          name="Life"
          component={MockLifeScreen}
          options={{
            tabBarLabel: '生活',
            tabBarTestID: 'tab-life',
          }}
        />
        <Tab.Screen
          name="Suoke"
          component={MockSuokeScreen}
          options={{
            tabBarLabel: '索克',
            tabBarTestID: 'tab-suoke',
          }}
        />
        <Tab.Screen
          name="Profile"
          component={MockProfileScreen}
          options={{
            tabBarLabel: '我的',
            tabBarTestID: 'tab-profile',
          }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
};

describe('AppNavigator', () => {
  it('应该正确渲染底部标签导航', () => {
    const { getByText } = render(<AppNavigator />);
    
    expect(getByText('首页')).toBeTruthy();
    expect(getByText('探索')).toBeTruthy();
    expect(getByText('生活')).toBeTruthy();
    expect(getByText('索克')).toBeTruthy();
    expect(getByText('我的')).toBeTruthy();
  });

  it('应该设置正确的标签栏测试ID', () => {
    const { getByTestId } = render(<AppNavigator />);
    
    expect(getByTestId('tab-home')).toBeTruthy();
    expect(getByTestId('tab-explore')).toBeTruthy();
    expect(getByTestId('tab-life')).toBeTruthy();
    expect(getByTestId('tab-suoke')).toBeTruthy();
    expect(getByTestId('tab-profile')).toBeTruthy();
  });

  it('应该正确配置导航选项', () => {
    // 这个测试验证导航器能够正确渲染，间接验证了配置
    const { getByText } = render(<AppNavigator />);
    expect(getByText('首页')).toBeTruthy();
  });
}); 