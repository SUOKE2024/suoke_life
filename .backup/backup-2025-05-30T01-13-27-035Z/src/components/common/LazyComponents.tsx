import { ActivityIndicator, View } from "react-native";
import React, { Suspense, lazy } from "react";



/**
 * 懒加载组件工厂
 * 索克生活APP - 性能优化
 */


// 加载指示器组件
// TODO: 将内联组件移到组件外部
// TODO: 将内联组件移到组件外部
// TODO: 将内联组件移到组件外部
const LoadingIndicator = () => (
  <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
    <ActivityIndicator size="large" color="#007AFF" />
  </View>
);

// 懒加载组件工厂
export const createLazyComponent = (importFunc: () => Promise<any>) => {
  const LazyComponent = lazy(importFunc);

  return (props: any) => (
    <Suspense fallback={<LoadingIndicator />}>
      <LazyComponent {...props} />
    </Suspense>
  );
};

// 预定义的懒加载组件
export const LazyScreens = {
  // 诊断相关屏幕
  DiagnosisScreen: createLazyComponent(
    () => import("../screens/diagnosis/DiagnosisScreen")
  ),
  FiveDiagnosisScreen: createLazyComponent(
    () => import("../screens/diagnosis/FiveDiagnosisScreen")
  ),

  // 智能体相关屏幕
  XiaoaiScreen: createLazyComponent(
    () => import("../screens/agents/XiaoaiScreen")
  ),
  XiaokeScreen: createLazyComponent(
    () => import("../screens/agents/XiaokeScreen")
  ),
  LaokeScreen: createLazyComponent(
    () => import("../screens/agents/LaokeScreen")
  ),
  SoerScreen: createLazyComponent(() => import("../screens/agents/SoerScreen")),

  // 生活相关屏幕
  LifeScreen: createLazyComponent(() => import("../screens/life/LifeScreen")),
  ExploreScreen: createLazyComponent(
    () => import("../screens/explore/ExploreScreen")
  ),
};
