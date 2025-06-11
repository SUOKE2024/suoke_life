import React, { Component, ReactNode } from "react";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";

// ErrorBoundary.tsx 索克生活APP - 错误边界组件

interface AppError {
  code: string;
  message: string;
  timestamp: string;
  stack?: string;
  service?: string;
}

interface Props {
  children: ReactNode;
  fallback?: (error: AppError, retry: () => void) => ReactNode;
  onError?: (error: AppError) => void;
}

interface State {
  hasError: boolean;
  error: AppError | null;
  retryCount: number;
}

export class ErrorBoundary extends Component<Props, State> {
  private maxRetries = 3;

  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      retryCount: 0,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    // 将错误转换为AppError
    const appError: AppError = {
      code: 'COMPONENT_ERROR',
      message: error.message || '组件发生未知错误',
      timestamp: new Date().toISOString(),
      stack: error.stack,
    };

    return {
      hasError: true,
      error: appError,
      retryCount: 0,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    const appError: AppError = {
      code: 'COMPONENT_ERROR',
      message: error.message || '组件发生未知错误',
      timestamp: new Date().toISOString(),
      stack: error.stack,
    };

    // 调用错误回调
    if (this.props.onError) {
      this.props.onError(appError);
    }

    // 记录错误详情
    console.error('ErrorBoundary caught an error:', {
      error: appError,
      errorInfo,
      componentStack: errorInfo.componentStack,
    });
  }

  handleRetry = () => {
    if (this.state.retryCount >= this.maxRetries) {
      return;
    }

    this.setState(prevState => ({
      hasError: false,
      error: null,
      retryCount: prevState.retryCount + 1,
    }));
  };

  handleRefresh = () => {
    // 在React Native中，可以使用RNRestart.Restart()
    // 这里提供基本的重置
    this.setState({
      hasError: false,
      error: null,
      retryCount: 0,
    });
  };

  renderDefaultError = (error: AppError, retry: () => void) => {
    return (
      <View style={styles.errorContainer}>
        <View style={styles.errorHeader}>
          <Text style={styles.errorIcon}>⚠️</Text>
          <Text style={styles.errorTitle}>出现了一些问题</Text>
        </View>

        <View style={styles.errorBody}>
          <Text style={styles.errorMessage}>{error.message}</Text>
          <Text style={styles.errorCode}>错误代码: {error.code}</Text>
        </View>

        <View style={styles.errorActions}>
          <TouchableOpacity style={styles.primaryButton} onPress={retry}>
            <Text style={styles.primaryButtonText}>重试</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.secondaryButton} onPress={this.handleRefresh}>
            <Text style={styles.secondaryButtonText}>刷新应用</Text>
          </TouchableOpacity>
        </View>

        {__DEV__ && (
          <View style={styles.debugInfo}>
            <Text style={styles.debugTitle}>调试信息</Text>
            <Text style={styles.debugText}>错误代码: {error.code}</Text>
            <Text style={styles.debugText}>时间: {error.timestamp}</Text>
            {error.stack && (
              <Text style={styles.debugText} numberOfLines={3}>
                堆栈: {error.stack}
              </Text>
            )}
          </View>
        )}
      </View>
    );
  };

  render() {
    if (this.state.hasError && this.state.error) {
      // 如果提供了自定义fallback，使用它
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.handleRetry);
      }

      // 否则使用默认错误显示
      return this.renderDefaultError(this.state.error, this.handleRetry);
    }

    return this.props.children;
  }
}

// 错误显示组件（用于非边界错误）
interface ErrorDisplayProps {
  error: AppError;
  onRetry?: () => void;
  onDismiss?: () => void;
  style?: any;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  error,
  onRetry,
  onDismiss,
  style,
}) => {
  return (
    <View style={[styles.errorDisplay, style]}>
      <View style={styles.errorDisplayHeader}>
        <Text style={styles.errorDisplayIcon}>⚠️</Text>
        <Text style={styles.errorDisplayTitle}>出现错误</Text>
        {onDismiss && (
          <TouchableOpacity onPress={onDismiss}>
            <Text style={styles.closeButton}>✕</Text>
          </TouchableOpacity>
        )}
      </View>
      
      <Text style={styles.errorDisplayMessage}>{error.message}</Text>
      
      {onRetry && (
        <View style={styles.errorDisplayActions}>
          <TouchableOpacity style={styles.retryButton} onPress={onRetry}>
            <Text style={styles.retryButtonText}>重试</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
};

// 样式
const styles = StyleSheet.create({
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  errorHeader: {
    alignItems: 'center',
    marginBottom: 20,
  },
  errorIcon: {
    fontSize: 48,
    marginBottom: 10,
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
  },
  errorBody: {
    alignItems: 'center',
    marginBottom: 30,
  },
  errorMessage: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 10,
    lineHeight: 24,
  },
  errorCode: {
    fontSize: 12,
    color: '#999',
    marginBottom: 10,
  },
  errorActions: {
    flexDirection: 'row',
    gap: 10,
  },
  primaryButton: {
    backgroundColor: '#35bb78',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
  },
  primaryButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  secondaryButton: {
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
  },
  secondaryButtonText: {
    color: '#333',
  },
  debugInfo: {
    marginTop: 20,
    padding: 10,
    backgroundColor: '#fff',
    borderRadius: 8,
    width: '100%',
  },
  debugTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  debugText: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  errorDisplay: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    margin: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  errorDisplayHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  errorDisplayIcon: {
    fontSize: 24,
    marginRight: 8,
  },
  errorDisplayTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    flex: 1,
  },
  closeButton: {
    fontSize: 18,
    color: '#666',
  },
  errorDisplayMessage: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
  },
  errorDisplayActions: {
    alignItems: 'flex-end',
  },
  retryButton: {
    backgroundColor: '#35bb78',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  retryButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
});

export default ErrorBoundary;