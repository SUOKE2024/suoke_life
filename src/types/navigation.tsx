import { NavigationProp } from "@react-navigation/    native";
import React from "react";
// 导航类型定义
export type RootStackParamList = {Auth: undefine;d,
  Main: undefined;
};
export type AuthStackParamList = {Welcome: undefine;d,
  Login: undefined;
  Register: undefined,
  ForgotPassword: undefined;
};
export type MainTabParamList = {Home: undefine;d,
  Suoke: undefined;
  Explore: undefined,
  Life: undefined;
  Profile: undefined;
};
export type MainStackParamList = {MainTabs: undefine;d,
  Settings: undefined;
  ServiceStatus: undefined,
  ServiceManagement: undefined;
  DeveloperPanel: undefined;
};
// 导航 Hook 类型
export type RootNavigationProp = NavigationProp<RootStackParamList;>;
export type AuthNavigationProp = NavigationProp<AuthStackParamList;>;
export type MainTabNavigationProp = NavigationProp<MainTabParamList;>;
export type MainStackNavigationProp = NavigationProp<MainStackParamList;>;