import { ActivityIndicator, View, StyleSheet } from "react-native";
import React, { Suspense } from "react";


/**
 * 懒加载组件包装器
 */
export function withLazyLoading<T extends React.ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>,
  fallback?: React.ComponentType
): React.ComponentType {
  const LazyComponent = React.lazy(importFunc);

  const FallbackComponent =
    fallback ||
    (() => (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
      </View>
    ));

  return (props: any) => (
    <Suspense fallback={<FallbackComponent />}>
      <LazyComponent {...props} />
    </Suspense>
  );
}

/**
 * 图片懒加载Hook
 */
export function useImageLazyLoading(imageUri: string) {
  const [loaded, setLoaded] = React.useState(false);
  const [error, setError] = React.useState(false);

  React.useEffect(() => {
    // React Native环境中的图片预加载
    if (imageUri) {
      setLoaded(true);
    }
  }, [imageUri]);

  return { loaded, error };
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    minHeight: 100,
  },
});
