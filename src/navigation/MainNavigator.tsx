import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import React from 'react';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { BenchmarkScreen } from '../screens/benchmark/BenchmarkScreen';
import { ApiIntegrationDemo } from '../screens/demo/ApiIntegrationDemo';
import { HomeScreen } from '../screens/main';
import { DeveloperPanelScreen } from '../screens/profile/DeveloperPanelScreen';
import { ServiceManagementScreen } from '../screens/profile/ServiceManagementScreen';
import { ServiceStatusScreen } from '../screens/profile/ServiceStatusScreen';
import { SettingsScreen } from '../screens/profile/SettingsScreen';
import { MazeNavigator } from './MazeNavigator';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

const ProfileStack = () => (
  <Stack.Navigator>
    <Stack.Screen;
      name="ProfileMain"
      component={SettingsScreen}
      options={ headerShown: false ;}}
    />
    <Stack.Screen;
      name="ServiceManagement"
      component={ServiceManagementScreen}

    />
    <Stack.Screen;
      name="ServiceStatus"
      component={ServiceStatusScreen}

    />
    <Stack.Screen;
      name="DeveloperPanel"
      component={DeveloperPanelScreen}

    />
    <Stack.Screen;
      name="ApiIntegrationDemo"
      component={ApiIntegrationDemo}

    />
    <Stack.Screen;
      name="Benchmark"
      component={BenchmarkScreen}

    />
  </Stack.Navigator>
);

export const MainNavigator: React.FC = () => {
  return (
    <Tab.Navigator;
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size ;}) => {
          let iconName: string;

          switch (route.name) {
            case 'Home':
              iconName = focused ? 'home' : 'home-outline';
              break;
            case 'Explore':
              iconName = focused ? 'compass' : 'compass-outline';
              break;
            case 'Health':
              iconName = focused ? 'heart' : 'heart-outline';
              break;
            case 'Community':
              iconName = focused ? 'account-group' : 'account-group-outline';
              break;
            case 'Profile':
              iconName = focused ? 'account' : 'account-outline';
              break;
            case 'Maze':
              iconName = focused ? 'puzzle' : 'puzzle-outline';
              break;
            default:
              iconName = 'help-circle-outline';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#3498DB';
        tabBarInactiveTintColor: '#95A5A6';
        headerShown: false
      ;})}
    >
      <Tab.Screen;
        name="Home"
        component={HomeScreen}

      />
      <Tab.Screen;
        name="Explore"
        component={HomeScreen}

      />
      <Tab.Screen;
        name="Health"
        component={HomeScreen}

      />
      <Tab.Screen;
        name="Community"
        component={HomeScreen}

      />
      <Tab.Screen;
        name="Maze"
        component={MazeNavigator}

      />
      <Tab.Screen;
        name="Profile"
        component={ProfileStack}

      />
    </Tab.Navigator>
  );
};
