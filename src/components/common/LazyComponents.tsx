import {   ActivityIndicator, View   } from "react-native";";
import React,{ Suspense, lazy } from "react";"";"";
// 懒加载组件工厂   索克生活APP - 性能优化"/;"/g"/;
* / TODO: 将内联组件移到组件外部* *  , TODO: 将内联组件移到组件外部// const LoadingIndicator = () => (;)"/;"/g"/;
  <View style={ flex: 1, justifyContent: "center", alignItems: "cente;r" ;}}  />/    <ActivityIndicator size="large" color="#007AFF"  />/  </View>/    );"/;"/g"/;
//   ;/;/g/;
> ;{//;,}const LazyComponent = lazy(importFun;c;);/g/;
}
  return (props: unknown) => (;)}
    <Suspense fallback={<LoadingIndicator  />}>/      <LazyComponent {...props}  />/    </Suspense>/      );/;/g/;
};
//   ;"/;"/g"/;
{/"/;,}DiagnosisScreen: createLazyComponent() () () => import("../screens/diagnosis/DiagnosisScreen")/      );",""/;,"/g,"/;
  FiveDiagnosisScreen: createLazyComponent() () () => import("../screens/diagnosis/FiveDiagnosisScreen");/      ),"/;,"/g,"/;
  XiaoaiScreen: createLazyComponent() () () => import("../screens/agents/XiaoaiScreen")/      );",""/;,"/g,"/;
  XiaokeScreen: createLazyComponent() () () => import("../screens/agents/XiaokeScreen");/      ),"/;,"/g,"/;
  LaokeScreen: createLazyComponent() () () => import("../screens/agents/LaokeScreen");/      ),"/;,"/g,"/;
  SoerScreen: createLazyComponent() () () => import("../screens/agents/SoerScreen");),/"/;"/g"/;
}
  LifeScreen: createLazyComponent() () () => import(".. / screens * life /LifeScreen")),/      ExploreScreen: createLazyComponent() () () => import("../screens/explore/ExploreScreen");/      )"}""/;"/g"/;
};""";