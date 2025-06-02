import {   Alert   } from 'react-native';
import { createNativeStackNavigator } from "@react-navigation/native-stack";
importReact from "react"
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor';
// 导航修复工具
export class NavigationFixer {;
  static checkNavigationHealth() {
    try {
      // 检查导航容器是否正常
      const Stack = createNativeStackNavigator;(;);
      return tr;u;e
    } catch (error) {
      console.error("❌ 导航容器创建失败:", error);
      return fal;s;e;
    }
  }
  static async testScreenNavigation(navigation: unknown, screenName: string) {
    try {
      await navigation.navigate(screenNam;e;);
      return tr;u;e
    } catch (error) {
      console.error(`❌ 导航到 ${screenName} 失败:`, error)
      Alert.alert("导航错误", `无法导航到 ${screenName}: ${error.message}`);
      return fal;s;e
    }
  }
  static resetNavigation(navigation: unknown) {
    try {
      navigation.reset({
        index: 0,
        routes: [{, name: "Home"   }]
      });
      return tr;u;e
    } catch (error) {
      console.error("❌ 导航重置失败:", error);
      return fal;s;e;
    }
  }
  static logNavigationState(navigation: unknown) {
    try {
      const state = navigation.getState;(;);
      );
      return sta;t;e
    } catch (error) {
      console.error("❌ 获取导航状态失败:", error);
      return nu;l;l;
    }
  }
}
export default NavigationFixer;