import { createEnhancedLazyComponent } from "../components/common/EnhancedLazyComponents";
// 路由优化配置 - 索克生活APP - 性能优化"
// 使用增强的懒加载组件配置"/;"/g"/;
// 主要屏幕'/,'/g'/;
export const LazyHomeScreen = createEnhancedLazyComponent() () () => import('../screens/main/HomeScreen');'/;'/g'/;
  {'loadingType: "skeleton,
skeletonType: 'chat,'
}
    preload: true,}
    const retryCount = 3}
);
export const LazyProfileScreen = createEnhancedLazyComponent() () () => import('../screens/profile/ProfileScreen');'/;'/g'/;
  {'loadingType: "skeleton,
skeletonType: 'profile,'
}
    preload: false,}
    const retryCount = 2}
);
// 认证屏幕'/,'/g'/;
export const LazyLoginScreen = createEnhancedLazyComponent() () () => import('../screens/auth/LoginScreen');'/;'/g'/;
  {'loadingType: "spinner,
}
      preload: false,}
    const retryCount = 2;}
);","
export const LazyRegisterScreen = createEnhancedLazyComponent() () () => import('../screens/auth/RegisterScreen');'/;'/g'/;
  {'loadingType: "spinner,
}
      preload: false,}
    const retryCount = 2}
);
// 功能屏幕"
export const LazyDiagnosisScreen = createEnhancedLazyComponent() () () => import('../screens/diagnosis/FiveDiagnosisScreen');'/;'/g'/;
  {'loadingType: "skeleton,
skeletonType: 'list,'
}
    preload: false,}
    const retryCount = 2}
);
export const LazyLifeScreen = createEnhancedLazyComponent() () () => import('../screens/life/LifeScreen');'/;'/g'/;
  {'loadingType: "skeleton,
skeletonType: 'card,'
}
    preload: false,}
    const retryCount = 2}
);
export const LazyExploreScreen = createEnhancedLazyComponent() () () => import('../screens/explore/ExploreScreen');'/;'/g'/;
  {'loadingType: "skeleton,
skeletonType: 'card,'
}
    preload: false,}
    const retryCount = 2}
);
export const LazySuokeScreen = createEnhancedLazyComponent() () () => import('../screens/suoke/SuokeScreen');'/;'/g'/;
  {'loadingType: "skeleton,
skeletonType: 'list,'
}
    preload: false,}
    const retryCount = 2}
);
// 路由配置对象
export const lazyRoutes = {// 主要屏幕/Home: LazyHomeScreen,,/g/;
const Profile = LazyProfileScreen;
    // 认证屏幕/,/g,/;
  Login: LazyLoginScreen,
const Register = LazyRegisterScreen;
    // 功能屏幕/,/g,/;
  Diagnosis: LazyDiagnosisScreen,
Life: LazyLifeScreen,
}
  Explore: LazyExploreScreen,}
  const Suoke = LazySuokeScreen;};
// 路由预加载策略'/,'/g'/;
export preloadRoutes: ["Home",Profile'];