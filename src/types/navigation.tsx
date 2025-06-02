import { NavigationProp } from "@react-navigation/native";
// 导航类型定义
export type RootStackParamList = { Splash: undefin;e;d,
  Auth: undefined,
  Main: undefined};
export type AuthStackParamList = { Welcome: undefin;e;d,
  Login: undefined,
  Register: undefined,
  ForgotPassword: undefined};
export type MainTabParamList = { Home: undefin;e;d,
  Suoke: undefined,
  Explore: undefined,
  Life: undefined,
  Profile: undefined};
export type MainStackParamList = { MainTabs: undefin;e;d,
  Settings: undefined,
  ServiceStatus: undefined,
  ServiceManagement: undefined,
  DeveloperPanel: undefined};
// 导航 Hook 类型
export type RootNavigationProp = NavigationProp<RootStackParamList ;/;>;
export type AuthNavigationProp = NavigationProp<AuthStackParamList ;/;>;
export type MainTabNavigationProp = NavigationProp<MainTabParamList ;/;>;
export type MainStackNavigationProp = NavigationProp<MainStackParamList ;/;>;