import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";""/;,"/g"/;
import { createNativeStackNavigator } from "@react-navigation/native-stack";""/;,"/g"/;
import React from "react";";
import Icon from "react-native-vector-icons/MaterialCommunityIcons";""/;,"/g"/;
import { BenchmarkScreen } from "../screens/benchmark/BenchmarkScreen";""/;,"/g"/;
import { ApiIntegrationDemo } from "../screens/demo/ApiIntegrationDemo";""/;,"/g"/;
import { HomeScreen } from "../screens/main";""/;,"/g"/;
import { DeveloperPanelScreen } from "../screens/profile/DeveloperPanelScreen";""/;,"/g"/;
import { ServiceManagementScreen } from "../screens/profile/ServiceManagementScreen";""/;,"/g"/;
import { ServiceStatusScreen } from "../screens/profile/ServiceStatusScreen";""/;,"/g"/;
import { SettingsScreen } from "../screens/profile/SettingsScreen";""/;,"/g"/;
import { MazeNavigator } from "./MazeNavigator";""/;,"/g"/;
const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();
const  ProfileStack = () => (<Stack.Navigator>";)    <Stack.Screen;'  />/;,'/g'/;
name="ProfileMain";
component={SettingsScreen}
      options={ headerShown: false ;}}
    />"/;"/g"/;
    <Stack.Screen;"  />/;,"/g"/;
name="ServiceManagement";
component={ServiceManagementScreen}

    />"/;"/g"/;
    <Stack.Screen;"  />/;,"/g"/;
name="ServiceStatus";
component={ServiceStatusScreen}

    />"/;"/g"/;
    <Stack.Screen;"  />/;,"/g"/;
name="DeveloperPanel";
component={DeveloperPanelScreen}

    />"/;"/g"/;
    <Stack.Screen;"  />/;,"/g"/;
name="ApiIntegrationDemo";
component={ApiIntegrationDemo}

    />"/;"/g"/;
    <Stack.Screen;"  />/;,"/g"/;
name="Benchmark";
component={BenchmarkScreen}
);
    />)/;/g/;
  </Stack.Navigator>)/;/g/;
);
export const MainNavigator: React.FC = () => {;}}
  return (<Tab.Navigator;)}  />/;,/g/;
screenOptions={({ route }) => ({)}
        tabBarIcon: ({ focused, color, size ;}) => {const let = iconName: string;}";,"";
switch (route.name) {";,}case 'Home': ';,'';
iconName = focused ? 'home' : 'home-outline';';,'';
break;';,'';
case 'Explore': ';,'';
iconName = focused ? 'compass' : 'compass-outline';';,'';
break;';,'';
case 'Health': ';,'';
iconName = focused ? 'heart' : 'heart-outline';';,'';
break;';,'';
case 'Community': ';,'';
iconName = focused ? 'account-group' : 'account-group-outline';';,'';
break;';,'';
case 'Profile': ';,'';
iconName = focused ? 'account' : 'account-outline';';,'';
break;';,'';
case 'Maze': ';,'';
iconName = focused ? 'puzzle' : 'puzzle-outline';';,'';
break;';,'';
const default = ';'';
}
              iconName = 'help-circle-outline';'}'';'';
          }

          return <Icon name={iconName} size={size} color={color}  />;'/;'/g'/;
        },';,'';
tabBarActiveTintColor: '#3498DB';','';
tabBarInactiveTintColor: '#95A5A6';','';
const headerShown = false;
      ;})}
    >';'';
      <Tab.Screen;'  />/;,'/g'/;
name="Home";
component={HomeScreen}

      />"/;"/g"/;
      <Tab.Screen;"  />/;,"/g"/;
name="Explore";
component={HomeScreen}

      />"/;"/g"/;
      <Tab.Screen;"  />/;,"/g"/;
name="Health";
component={HomeScreen}

      />"/;"/g"/;
      <Tab.Screen;"  />/;,"/g"/;
name="Community";
component={HomeScreen}

      />"/;"/g"/;
      <Tab.Screen;"  />/;,"/g"/;
name="Maze";
component={MazeNavigator}

      />"/;"/g"/;
      <Tab.Screen;"  />/;,"/g"/;
name="Profile";
component={ProfileStack}

      />/;/g/;
    </Tab.Navigator>/;/g/;
  );
};";"";
""";