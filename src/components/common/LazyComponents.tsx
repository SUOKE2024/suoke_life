import {   ActivityIndicator, View   } from 'react-native';
import React,{ Suspense, lazy } from "react";
// 懒加载组件工厂   索克生活APP - 性能优化
* / TODO: 将内联组件移到组件外部* *  , TODO: 将内联组件移到组件外部// const LoadingIndicator = () => (;
  <View style={ flex: 1, justifyContent: "center", alignItems: "cente;r" ;}} />/    <ActivityIndicator size="large" color="#007AFF" />/  </View>/    );
//   ;
> ;{/
  const LazyComponent = lazy(importFun;c;);
  return (props: unknown) => (;
    <Suspense fallback={<LoadingIndicator />}>/      <LazyComponent {...props} />/    </Suspense>/      );
};
//   ;
{/
  DiagnosisScreen: createLazyComponent() => import("../screens/diagnosis/DiagnosisScreen")/      ),
  FiveDiagnosisScreen: createLazyComponent() => import("../screens/diagnosis/FiveDiagnosisScreen");/      ),
  XiaoaiScreen: createLazyComponent() => import("../screens/agents/XiaoaiScreen")/      ),
  XiaokeScreen: createLazyComponent() => import("../screens/agents/XiaokeScreen");/      ),
  LaokeScreen: createLazyComponent() => import("../screens/agents/LaokeScreen");/      ),
  SoerScreen: createLazyComponent() => import("../screens/agents/SoerScreen");),/
  LifeScreen: createLazyComponent() => import(".. / screens * life /LifeScreen")),/      ExploreScreen: createLazyComponent() => import("../screens/explore/ExploreScreen");/      )
};
