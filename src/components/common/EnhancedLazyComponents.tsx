import React, { Suspense, ComponentType, LazyExoticComponent, useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import SkeletonLoader from './SkeletonLoader';
// 错误边界组件
interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: any;
}
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback?: ComponentType<{ error: Error; retry: () => void ;}> },
  ErrorBoundaryState;
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false ;};
  }
  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error ;};
  }
  componentDidCatch(error: Error, errorInfo: any) {
    console.error('LazyComponent Error:', error, errorInfo);
    this.setState({ error, errorInfo });
  }
  retry = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined ;});
  };
  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback;
      return <FallbackComponent error={this.state.error!} retry={this.retry} />;
    }
    return this.props.children;
  }
}
// 默认错误回退组件
const DefaultErrorFallback: React.FC<{ error: Error; retry: () => void ;}> = ({ error, retry }) => ()
  <View style={styles.errorContainer}>
    <Text style={styles.errorTitle}>加载失败</Text>
    <Text style={styles.errorMessage}>{error.message}</Text>
    <TouchableOpacity style={styles.retryButton} onPress={retry}>
      <Text style={styles.retryButtonText}>重试</Text>
    </TouchableOpacity>
  </View>
);
// 加载指示器组件
interface LoadingIndicatorProps {
  type?: 'spinner' | 'skeleton';
  skeletonType?: 'list' | 'card' | 'profile' | 'chat';
  message?: string;
}
const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  type = 'skeleton',
  skeletonType = 'list',

;}) => {
  if (type === 'spinner') {
    return (
  <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>{message}</Text>
      </View>
    );
  }
  return <SkeletonLoader type={skeletonType} />;
};
// 懒加载配置接口
interface LazyComponentConfig {
  fallback?: ComponentType<any>;
  errorFallback?: ComponentType<{ error: Error; retry: () => void;
}>;
  loadingType?: 'spinner' | 'skeleton';
  skeletonType?: 'list' | 'card' | 'profile' | 'chat';
  preload?: boolean;
  retryCount?: number;
  timeout?: number;
}
// 预加载管理器
class PreloadManager {
  private static instance: PreloadManager;
  private preloadedComponents = new Map<string, Promise<any>>();
  private loadingComponents = new Set<string>();
  static getInstance(): PreloadManager {
    if (!PreloadManager.instance) {
      PreloadManager.instance = new PreloadManager();
    }
    return PreloadManager.instance;
  }
  preload(key: string, importFunc: () => Promise<any>): void {
    if (!this.preloadedComponents.has(key) && !this.loadingComponents.has(key)) {
      this.loadingComponents.add(key);
      const promise = importFunc()
        .then(module => {
          this.preloadedComponents.set(key, Promise.resolve(module));
          this.loadingComponents.delete(key);
          return module;
        })
        .catch(error => {
          this.loadingComponents.delete(key);
          console.warn(`Failed to preload component ${key}:`, error);
          throw error;
        });
            this.preloadedComponents.set(key, promise);
    }
  }
  getPreloaded(key: string): Promise<any> | undefined {
    return this.preloadedComponents.get(key);
  }
  isLoading(key: string): boolean {
    return this.loadingComponents.has(key);
  }
  clear(): void {
    this.preloadedComponents.clear();
    this.loadingComponents.clear();
  }
}
// 创建增强的懒加载组件
export const createEnhancedLazyComponent = <T extends ComponentType<any>>();
  importFunc: () => Promise<{ default: T ;}>,
  config: LazyComponentConfig = {;}
): LazyExoticComponent<T> => {
  const {
    fallback,
    errorFallback,
    loadingType = 'skeleton',
    skeletonType = 'list',
    preload = false,
    retryCount = 3,
    timeout = 10000} = config;
  // 生成组件键
  const componentKey = importFunc.toString();
  const preloadManager = PreloadManager.getInstance();
  // 如果启用预加载，立即开始预加载
  if (preload) {
    preloadManager.preload(componentKey, importFunc);
  }
  // 创建带重试机制的导入函数
  const importWithRetry = async (attempt = 1): Promise<{ default: T ;}> => {
    try {
      // 检查是否有预加载的组件
      const preloaded = preloadManager.getPreloaded(componentKey);
      if (preloaded) {
        return await preloaded;
      }
      // 添加超时控制
      const timeoutPromise = new Promise<never>(_, reject) => {
        setTimeout() => reject(new Error('Component load timeout')), timeout);
      });
      const result = await Promise.race([importFunc(), timeoutPromise]);
      return result;
    } catch (error) {
      console.warn(`Component load attempt ${attempt} failed:`, error);
            if (attempt < retryCount) {
        // 指数退避重试
        const delay = Math.pow(2, attempt - 1) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
        return importWithRetry(attempt + 1);
      }
            throw error;
    }
  };
  const LazyComponent = React.lazy(importWithRetry);
  // 返回包装后的组件
  const WrappedComponent = (props: any) => ()
    <ErrorBoundary fallback={errorFallback;}>
      <Suspense;
        fallback={
          fallback ? ()
            React.createElement(fallback)
          ) : (
            <LoadingIndicator type={loadingType} skeletonType={skeletonType} />
          )
        }
      >
        <LazyComponent {...props} />
      </Suspense>
    </ErrorBoundary>
  );
  return WrappedComponent as LazyExoticComponent<T>;
};
// 预加载Hook;
export const usePreloadComponent = ();
  importFunc: () => Promise<any>;
  condition: boolean = true;
) => {
  const [isPreloaded, setIsPreloaded] = useState(false);
  const preloadManager = PreloadManager.getInstance();
  useEffect() => {
    if (condition && !isPreloaded) {
      const componentKey = importFunc.toString();
      preloadManager.preload(componentKey, importFunc);
      setIsPreloaded(true);
    }
  }, [condition, importFunc, isPreloaded, preloadManager]);
  return isPreloaded;
};
// 批量预加载Hook;
export const useBatchPreload = ();
  components: Array<{,
  key: string;
  importFunc: () => Promise<any>;
    condition?: boolean;
  }>
) => {
  const [preloadedCount, setPreloadedCount] = useState(0);
  const preloadManager = PreloadManager.getInstance();
  useEffect() => {
    let count = 0;
        components.forEach({ key, importFunc, condition = true }) => {
      if (condition) {
        preloadManager.preload(key, importFunc);
        count++;
      }
    });
    setPreloadedCount(count);
  }, [components, preloadManager]);
  return {
    preloadedCount,
    totalCount: components.length;
    isComplete: preloadedCount === components.filter(c => c.condition !== false).length;};
};
// 路由预加载Hook;
export const useRoutePreload = (routeName: string, isActive: boolean) => {
  const preloadManager = PreloadManager.getInstance();
  useEffect() => {
    if (isActive) {
            // 预加载相关路由组件
      const routePreloadMap: Record<string, () => Promise<any>> = {
        'Home': () => import('../../screens/main/HomeScreen'),
        // 其他路由组件可以根据实际存在的文件进行配置
      ;};
      const importFunc = routePreloadMap[routeName];
      if (importFunc) {
        preloadManager.preload(routeName, importFunc);
      }
    }
  }, [routeName, isActive, preloadManager]);
};
const styles = StyleSheet.create({
  errorContainer: {,
  flex: 1;
    justifyContent: 'center';
    alignItems: 'center';
    padding: 20;},
  errorTitle: {,
  fontSize: 18;
    fontWeight: 'bold';
    color: '#FF3B30';
    marginBottom: 8;},
  errorMessage: {,
  fontSize: 14;
    color: '#666';
    textAlign: 'center';
    marginBottom: 20;},
  retryButton: {,
  backgroundColor: '#007AFF';
    paddingHorizontal: 20;
    paddingVertical: 10;
    borderRadius: 8;},
  retryButtonText: {,
  color: '#FFFFFF';
    fontSize: 16;
    fontWeight: '600';},
  loadingContainer: {,
  flex: 1;
    justifyContent: 'center';
    alignItems: 'center';
    padding: 20;},
  loadingText: {,
  marginTop: 12;
    fontSize: 16;
    color: '#666';}});
export { PreloadManager, LoadingIndicator, ErrorBoundary };