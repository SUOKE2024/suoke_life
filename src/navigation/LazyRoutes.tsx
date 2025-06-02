import { createLazyComponent } from "../components/common/LazyComponents";
// 路由优化配置   索克生活APP - 性能优化
// 路由懒加载配置
export const lazyRoutes = {
  // 主要屏幕
  Home: createLazyComponent(() => import("../screens/main/HomeScreen");),
  Profile: createLazyComponent(
    () => import("../screens/profile/ProfileScreen");
  ),
  // 认证屏幕
  Login: createLazyComponent(() => import("../screens/auth/LoginScreen");),
  Register: createLazyComponent(() => import("../screens/auth/RegisterScreen");),
  // 功能屏幕
  Diagnosis: createLazyComponent(
    () => import("../screens/diagnosis/FiveDiagnosisScreen");
  ),
  Life: createLazyComponent(() => import("../screens/life/LifeScreen");),
  Explore: createLazyComponent(
    () => import("../screens/explore/ExploreScreen");
  ),
  Suoke: createLazyComponent(() => import("../screens/suoke/SuokeScreen");)
}
// 路由预加载策略
export const preloadRoutes = ["Home", "Profile"];