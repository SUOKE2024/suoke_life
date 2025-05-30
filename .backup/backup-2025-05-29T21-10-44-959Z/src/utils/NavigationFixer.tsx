import { Alert } from "react-native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import React from "react";


// 导航修复工具
export class NavigationFixer {
  static checkNavigationHealth() {
    try {
      // 检查导航容器是否正常
      const Stack = createNativeStackNavigator();
      console.log("✅ 导航容器创建成功");
      return true;
    } catch (error) {
      console.error("❌ 导航容器创建失败:", error);
      return false;
    }
  }

  static async testScreenNavigation(navigation: any, screenName: string) {
    try {
      await navigation.navigate(screenName);
      console.log(`✅ 成功导航到 ${screenName}`);
      return true;
    } catch (error) {
      console.error(`❌ 导航到 ${screenName} 失败:`, error);
      Alert.alert("导航错误", `无法导航到 ${screenName}: ${error.message}`);
      return false;
    }
  }

  static resetNavigation(navigation: any) {
    try {
      navigation.reset({
        index: 0,
        routes: [{ name: "Home" }],
      });
      console.log("✅ 导航重置成功");
      return true;
    } catch (error) {
      console.error("❌ 导航重置失败:", error);
      return false;
    }
  }

  static logNavigationState(navigation: any) {
    try {
      const state = navigation.getState();
      console.log("📊 当前导航状态:", JSON.stringify(state, null, 2));
      return state;
    } catch (error) {
      console.error("❌ 获取导航状态失败:", error);
      return null;
    }
  }
}

export default NavigationFixer;
