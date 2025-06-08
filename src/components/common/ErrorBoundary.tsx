import React, { Component, ReactNode } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { errorHandler, AppError, formatErrorForDisplay, getRecoveryAdvice } from '../../services/errorHandler';
// ErrorBoundary.tsx   索克生活APP - 自动生成的类型安全文件     @description TODO: 添加文件描述 @author 索克生活开发团队   @version 1.0.0;
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
    // 将错误转换为AppError;
    const appError = errorHandler.handleError(error, 'error-boundary');
        return {
      hasError: true,
      error: appError,
      retryCount: 0,
    };
  }
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    const appError = errorHandler.handleError(error, 'error-boundary');
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
      Alert.alert(
        "重试次数已达上限",请刷新应用或联系技术支持',
        [
          {
      text: "刷新应用",
      onPress: this.handleRefresh },
          {
      text: "联系客服",
      onPress: this.handleContactSupport },
        ]
      );
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
  handleContactSupport = () => {
    // 这里可以集成客服系统或发送错误报告
    Alert.alert(
      "联系客服",请通过以下方式联系我们：\n\n客服电话：400-123-4567\n邮箱：support@suokelife.com',
      [{ text: '确定' }]
    );
  };
  handleReportError = () => {
    if (!this.state.error) return;
    const errorReport = {
      error: this.state.error,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location?.href,
    };
    // 发送错误报告
    console.log('Error report:', errorReport);
        Alert.alert(
      "错误报告已发送",感谢您的反馈，我们会尽快处理此问题',
      [{ text: '确定' }]
    );
  };
  renderDefaultError = (error: AppError, retry: () => void) => {
    const errorDisplay = formatErrorForDisplay(error);
    const recovery = getRecoveryAdvice(error);
    const isCritical = errorHandler.isCriticalError(error);
    return (
      <View style={styles.errorContainer}>
        <View style={styles.errorHeader}>
          <Icon;
            name={isCritical ? 'error' : 'warning'}
            size={48}
            color={isCritical ? '#f44336' : '#ff9800'}
          />
          <Text style={styles.errorTitle}>{errorDisplay.title}</Text>
        </View>
        <View style={styles.errorBody}>
          <Text style={styles.errorMessage}>{errorDisplay.message}</Text>
                    {error.requestId && (
            <Text style={styles.errorId}>错误ID: {error.requestId}</Text>
          )}
          <Text style={styles.recoveryMessage}>{recovery.message}</Text>
        </View>
        <View style={styles.errorActions}>
          {recovery.action === 'retry' && (
            <TouchableOpacity style={styles.primaryButton} onPress={retry}>
              <Icon name="refresh" size={20} color="#fff" />
              <Text style={styles.primaryButtonText}>重试</Text>
            </TouchableOpacity>
          )}
          {recovery.action === 'refresh' && (
            <TouchableOpacity style={styles.primaryButton} onPress={this.handleRefresh}>
              <Icon name="refresh" size={20} color="#fff" />
              <Text style={styles.primaryButtonText}>刷新应用</Text>
            </TouchableOpacity>
          )}
          <TouchableOpacity style={styles.secondaryButton} onPress={this.handleReportError}>
            <Icon name="bug-report" size={20} color="#2196F3" />
            <Text style={styles.secondaryButtonText}>报告问题</Text>
          </TouchableOpacity>
          {isCritical && (
            <TouchableOpacity style={styles.secondaryButton} onPress={this.handleContactSupport}>
              <Icon name="support-agent" size={20} color="#2196F3" />
              <Text style={styles.secondaryButtonText}>联系客服</Text>
            </TouchableOpacity>
          )}
        </View>
        {__DEV__ && (
        <View style={styles.debugInfo}>
            <Text style={styles.debugTitle}>调试信息</Text>
            <Text style={styles.debugText}>错误代码: {error.code}</Text>
            <Text style={styles.debugText}>服务: {error.service || 'unknown'}</Text>
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
  const errorDisplay = formatErrorForDisplay(error);
  const recovery = getRecoveryAdvice(error);
  const isCritical = errorHandler.isCriticalError(error);
  return (
    <View style={[styles.errorDisplay, style]}>
      <View style={styles.errorDisplayHeader}>
        <Icon;
          name={isCritical ? 'error' : 'warning'}
          size={24}
          color={isCritical ? '#f44336' : '#ff9800'}
        />
        <Text style={styles.errorDisplayTitle}>{errorDisplay.title}</Text>
        {onDismiss && (
          <TouchableOpacity onPress={onDismiss}>
            <Icon name="close" size={24} color="#666" />
          </TouchableOpacity>
        )}
      </View>
      <Text style={styles.errorDisplayMessage}>{errorDisplay.message}</Text>
      {(onRetry || recovery.autoRetry) && (
        <View style={styles.errorDisplayActions}>
          <TouchableOpacity;
            style={styles.retryButton}
            onPress={onRetry}
          >
            <Text style={styles.retryButtonText}>重试</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
};
// 样式
const styles = StyleSheet.create({
  errorContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  errorHeader: {,
  alignItems: 'center',
    marginBottom: 20,
  },
  errorTitle: {,
  fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 10,
    textAlign: 'center',
  },
  errorBody: {,
  alignItems: 'center',
    marginBottom: 30,
  },
  errorMessage: {,
  fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 10,
    lineHeight: 24,
  },
  errorId: {,
  fontSize: 12,
    color: '#999',
    marginBottom: 10,
  },
  recoveryMessage: {,
  fontSize: 14,
    color: '#2196F3',
    textAlign: 'center',
    fontStyle: 'italic',
  },
  errorActions: {,
  flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: 10,
  },
  primaryButton: {,
  flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#2196F3',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    gap: 8,
  },
  primaryButtonText: {,
  color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  secondaryButton: {,
  flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: '#2196F3',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    gap: 8,
  },
  secondaryButtonText: {,
  color: '#2196F3',
    fontSize: 16,
    fontWeight: '600',
  },
  debugInfo: {,
  marginTop: 30,
    padding: 15,
    backgroundColor: '#fff',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
    width: '100%',
  },
  debugTitle: {,
  fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  debugText: {,
  fontSize: 12,
    color: '#666',
    marginBottom: 5,
    fontFamily: 'monospace',
  },
  errorDisplay: {,
  backgroundColor: '#fff',
    borderLeftWidth: 4,
    borderLeftColor: '#f44336',
    padding: 15,
    marginVertical: 10,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  errorDisplayHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  errorDisplayTitle: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginLeft: 10,
    flex: 1,
  },
  errorDisplayMessage: {,
  fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 10,
  },
  errorDisplayActions: {,
  flexDirection: 'row',
    justifyContent: 'flex-end',
  },
  retryButton: {,
  backgroundColor: '#2196F3',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 6,
  },
  retryButtonText: {,
  color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
});
// RAG专用错误边界
export const RAGErrorBoundary: React.FC<{ children: ReactNode }> = ({ children }) => {
  const handleRAGError = (error: Error, errorInfo: string) => {// RAG特定的错误处理逻辑;
    console.error('RAG Error:', error);
    // 可以在这里添加错误上报逻辑
    // errorReportingService.report(error, { context: 'RAG', errorInfo });
  };
  const ragFallback = (error: Error, retry: () => void) => (;
    <View style={styles.container}>;
      <View style={styles.errorContainer}>;
        <Text style={styles.errorTitle}>RAG服务暂时不可用</Text>;
        <Text style={styles.errorMessage}>;
          {error.message.includes('网络') ? '请检查网络连接后重试' : '服务正在维护中，请稍后再试'};
        </Text>;
        <TouchableOpacity style={styles.retryButton} onPress={retry}>;
          <Text style={styles.retryButtonText}>重新连接</Text>;
        </TouchableOpacity>;
      </View>;
    </View>;
  );
  return (;
    <ErrorBoundary fallback={ragFallback} onError={handleRAGError}>;
      {children};
    </ErrorBoundary>;
  );
};