import React, { ComponentType, ReactNode } from 'react';
import {;
  ActivityIndicator,
  StyleSheet,
  Text,
  TouchableOpacity,
  View
} from 'react-native';
import {;
  borderRadius,
  colors,
  spacing,
  typography
} from '../../constants/theme';

interface LazyLoaderProps {
  /** 懒加载的组件工厂函数 */
  factory: () => Promise<{ default: ComponentType<any> }>;
  /** 加载中的占位组件 */
  fallback?: ReactNode;
  /** 错误时的占位组件 */
  errorFallback?: ReactNode;
  /** 组件属性 */
  props?: any;
  /** 是否显示加载进度 */
  showProgress?: boolean;
  /** 加载超时时间（毫秒） */
  timeout?: number;
  /** 重试次数 */
  retryCount?: number;
  /** 组件名称（用于调试） */
  componentName?: string;
}

interface LazyLoaderState {
  hasError: boolean;,
  isLoading: boolean;,
  retryAttempts: number;
  error?: Error;
}

class LazyLoaderErrorBoundary extends React.Component<
  { children: ReactNode; onError?: (error: Error) => void },
  { hasError: boolean; error?: Error }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('LazyLoader Error:', error, errorInfo);
    this.props.onError?.(error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <View style={styles.errorContainer}>
          <Text style={styles.errorTitle}>组件加载失败</Text>
          <Text style={styles.errorMessage}>
            {this.state.error?.message || '未知错误'}
          </Text>
          <TouchableOpacity;
            style={styles.retryButton}
            onPress={() => this.setState({ hasError: false, error: undefined })}
          >
            <Text style={styles.retryButtonText}>重试</Text>
          </TouchableOpacity>
        </View>
      );
    }

    return this.props.children;
  }
}

const DefaultFallback: React.FC<{
  componentName?: string;
  showProgress?: boolean;
}> = ({ componentName, showProgress = true }) => (
  <View style={styles.fallbackContainer}>
    {showProgress && <ActivityIndicator size="large" color={colors.primary} />}
    <Text style={styles.fallbackText}>
      {componentName ? `正在加载 ${componentName}...` : '正在加载...'}
    </Text>
  </View>
);

const DefaultErrorFallback: React.FC<{ onRetry?: () => void }> = ({
  onRetry
}) => (
  <View style={styles.errorContainer}>
    <Text style={styles.errorTitle}>加载失败</Text>
    <Text style={styles.errorMessage}>组件加载时出现错误</Text>
    {onRetry && (
      <TouchableOpacity style={styles.retryButton} onPress={onRetry}>
        <Text style={styles.retryButtonText}>重试</Text>
      </TouchableOpacity>
    )}
  </View>
);

export const LazyLoader: React.FC<LazyLoaderProps> = ({
  factory,
  fallback,
  errorFallback,
  props = {},
  showProgress = true,
  timeout = 10000,
  retryCount = 3,
  componentName
}) => {
  const [state, setState] = React.useState<LazyLoaderState>({
    hasError: false,
    isLoading: false,
    retryAttempts: 0
  });

  const [LazyComponent, setLazyComponent] =
    React.useState<ComponentType<any> | null>(null);

  const loadComponent = React.useCallback(async () => {
    if (state.retryAttempts >= retryCount) {
      setState(prev) => ({ ...prev, hasError: true }));
      return;
    }

    setState(prev) => ({ ...prev, isLoading: true, hasError: false }));

    try {
      const timeoutPromise = new Promise(_, reject) =>
        setTimeout() => reject(new Error('组件加载超时')), timeout)
      );

      const componentModule = (await Promise.race([
        factory(),
        timeoutPromise
      ])) as any;
      setLazyComponent() => componentModule.default);
      setState(prev) => ({ ...prev, isLoading: false }));
    } catch (error) {
      console.error('LazyLoader: 组件加载失败', error);
      setState(prev) => ({
        ...prev,
        isLoading: false,
        hasError: true,
        error: error as Error,
        retryAttempts: prev.retryAttempts + 1
      }));
    }
  }, [factory, timeout, retryCount, state.retryAttempts]);

  React.useEffect() => {
    loadComponent();
  }, [loadComponent]);

  const handleRetry = React.useCallback() => {
    setState(prev) => ({ ...prev, retryAttempts: 0 }));
    loadComponent();
  }, [loadComponent]);

  if (state.hasError) {
    return errorFallback || <DefaultErrorFallback onRetry={handleRetry} />;
  }

  if (state.isLoading || !LazyComponent) {
    return (
      fallback || (
        <DefaultFallback;
          componentName={componentName}
          showProgress={showProgress}
        />
      )
    );
  }

  return (
    <LazyLoaderErrorBoundary;
      onError={(error) =>
        setState(prev) => ({ ...prev, hasError: true, error }))
      }
    >
      <LazyComponent {...props} />
    </LazyLoaderErrorBoundary>
  );
};

// 高阶组件版本
export const withLazyLoader = <P extends object>(;
  factory: () => Promise<{ default: ComponentType<P> }>,
  options?: Omit<LazyLoaderProps, 'factory' | 'props'>
) => {
  return (props: P) => (
    <LazyLoader factory={factory} props={props} {...options} />
  );
};

// Hook 版本
export const useLazyComponent = <T extends ComponentType<any>>(;
  factory: () => Promise<{ default: T }>,
  deps: React.DependencyList = []
) => {
  const [component, setComponent] = React.useState<T | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<Error | null>(null);

  React.useEffect() => {
    let cancelled = false;

    const loadComponent = async () => {
      setLoading(true);
      setError(null);

      try {
        const module = await factory();
        if (!cancelled) {
          setComponent() => module.default);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err as Error);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadComponent();

    return () => {
      cancelled = true;
    };
  }, deps);

  return { component, loading, error };
};

// 预加载函数
export const preloadComponent = (;
  factory: () => Promise<{ default: ComponentType<any> }>
) => {
  return factory().catch(error) => {
    console.warn('组件预加载失败:', error);
  });
};

// 批量预加载
export const preloadComponents = (;
  factories: Array<() => Promise<{ default: ComponentType<any> }>>
) => {
  return Promise.allSettled(
    factories.map(factory) => preloadComponent(factory))
  );
};

const styles = StyleSheet.create({
  fallbackContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
    backgroundColor: colors.background
  },
  fallbackText: {,
  fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    marginTop: spacing.md,
    textAlign: 'center'
  },
  errorContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
    backgroundColor: colors.background
  },
  errorTitle: {,
  fontSize: typography.fontSize.lg,
    fontWeight: '600' as const,
    color: colors.error,
    marginBottom: spacing.sm,
    textAlign: 'center'
  },
  errorMessage: {,
  fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
    textAlign: 'center',
    lineHeight: 22
  },
  retryButton: {,
  backgroundColor: colors.primary,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.md
  },
  retryButtonText: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.white
  }
});

export default LazyLoader;
