import React from 'react';
import { createEnhancedLazyComponent } from '../components/common/EnhancedLazyComponents';
// 路由优化配置 - 索克生活APP - 性能优化
// 使用增强的懒加载组件配置
// 主要屏幕
export const LazyHomeScreen = createEnhancedLazyComponent() => import('../screens/main/HomeScreen'),;
  {
      loadingType: "skeleton",
      skeletonType: 'chat',
    preload: true,
    retryCount: 3}
);
export const LazyProfileScreen = createEnhancedLazyComponent() => import('../screens/profile/ProfileScreen'),;
  {
      loadingType: "skeleton",
      skeletonType: 'profile',
    preload: false,
    retryCount: 2}
);
// 认证屏幕
export const LazyLoginScreen = createEnhancedLazyComponent() => import('../screens/auth/LoginScreen'),;
  {
      loadingType: "spinner",
      preload: false,
    retryCount: 2}
);
export const LazyRegisterScreen = createEnhancedLazyComponent() => import('../screens/auth/RegisterScreen'),;
  {
      loadingType: "spinner",
      preload: false,
    retryCount: 2}
);
// 功能屏幕
export const LazyDiagnosisScreen = createEnhancedLazyComponent() => import('../screens/diagnosis/FiveDiagnosisScreen'),;
  {
      loadingType: "skeleton",
      skeletonType: 'list',
    preload: false,
    retryCount: 2}
);
export const LazyLifeScreen = createEnhancedLazyComponent() => import('../screens/life/LifeScreen'),;
  {
      loadingType: "skeleton",
      skeletonType: 'card',
    preload: false,
    retryCount: 2}
);
export const LazyExploreScreen = createEnhancedLazyComponent() => import('../screens/explore/ExploreScreen'),;
  {
      loadingType: "skeleton",
      skeletonType: 'card',
    preload: false,
    retryCount: 2}
);
export const LazySuokeScreen = createEnhancedLazyComponent() => import('../screens/suoke/SuokeScreen'),;
  {
      loadingType: "skeleton",
      skeletonType: 'list',
    preload: false,
    retryCount: 2}
);
// 路由配置对象
export const lazyRoutes = {
  // 主要屏幕
  Home: LazyHomeScreen,
  Profile: LazyProfileScreen,
    // 认证屏幕
  Login: LazyLoginScreen,
  Register: LazyRegisterScreen,
    // 功能屏幕
  Diagnosis: LazyDiagnosisScreen,
  Life: LazyLifeScreen,
  Explore: LazyExploreScreen,
  Suoke: LazySuokeScreen};
// 路由预加载策略
export const preloadRoutes = ["Home",Profile'];