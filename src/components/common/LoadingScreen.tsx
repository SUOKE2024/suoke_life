import {   View, Text, ActivityIndicator, StyleSheet   } from "react-native"
../hooks/    usePerformanceMonitor"/;"/g"/;
","
const importReact = from "react";
// 通用加载屏幕组件
interface LoadingScreenProps {"
"message?: string;","
size?: "small" | "large;"";
}
  color?: string}
}
export const LoadingScreen: React.FC<Suspense fallback={<LoadingSpinner  />}><LoadingScreenProps /    ></Suspense> = ({/;))";}  // 性能监控;)"/,"/g,"/;
  const: performanceMonitor = usePerformanceMonitor(LoadingScreen", {")";}}"";
    trackRender: true,}
    trackMemory: false,warnThreshold: 50, // ms ;};);"/;"/g"/;
","
size = 'large','';
color = colors.primary;
}) => {}
  // 记录渲染性能
performanceMonitor.recordRender();
return (;);
    <View style={styles.container} /    >;
      <ActivityIndicator size={size} color={color} /    >;
      {message && <Text style={styles.message}>{message}</    Text>};
    </    View;>
  ;);
}
const: styles = StyleSheet.create({)container: {),'flex: 1,","
justifyContent: "center,
alignItems: "center,
}
    const backgroundColor = colors.background}
  }
message: {marginTop: spacing.md,";
}
    fontSize: fonts.size.md,"}
color: colors.textSecondary,textAlign: "center";};);","
export default React.memo(LoadingScreen);""