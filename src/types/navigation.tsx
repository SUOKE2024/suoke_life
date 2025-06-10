// 索克生活 - 导航类型定义/g/;
import { StackNavigationProp } from '@react-navigation/stack';'/g'/;
import { BottomTabNavigationProp } from '@react-navigation/bottom-tabs';'/g'/;

export type RootStackParamList = {}
  Home: undefined;
  Profile: undefined;
  Settings: undefined;
  Diagnosis: undefined;
  Agents: undefined;
};

export type TabParamList = {}
  Home: undefined;
  Life: undefined;
  Explore: undefined;
  Profile: undefined;
};

export type HomeScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Home'>;'';
export type ProfileScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Profile'>;'';
