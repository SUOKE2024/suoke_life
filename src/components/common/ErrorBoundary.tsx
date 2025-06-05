//////     ErrorBoundary.tsx   索克生活APP - 自动生成的类型安全文件     @description TODO: 添加文件描述 @author 索克生活开发团队   @version 1.0.0;
import React, { Component, ReactNode } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: string | null;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: (error: Error, retry: () => void) => ReactNode;
  onError?: (error: Error, errorInfo: string) => void;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({
      errorInfo: errorInfo.componentStack,
    });

    // 调用错误回调
    this.props.onError?.(error, errorInfo.componentStack);

    // 记录错误到日志服务
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      // 如果提供了自定义fallback，使用它
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.handleRetry);
      }

      // 默认错误UI
      return (
        <View style={styles.container}>
          <View style={styles.errorContainer}>
            <Text style={styles.errorTitle}>出现了一些问题</Text>
            <Text style={styles.errorMessage}>
              {this.state.error.message || '未知错误'}
            </Text>
            
            <TouchableOpacity style={styles.retryButton} onPress={this.handleRetry}>
              <Text style={styles.retryButtonText}>重试</Text>
            </TouchableOpacity>
            
            {__DEV__ && this.state.errorInfo && (
              <View style={styles.debugContainer}>
                <Text style={styles.debugTitle}>调试信息:</Text>
                <Text style={styles.debugText}>{this.state.errorInfo}</Text>
              </View>
            )}
          </View>
        </View>
      );
    }

    return this.props.children;
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  errorContainer: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
    maxWidth: '90%',
  },
  errorTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#d32f2f',
    marginBottom: 10,
    textAlign: 'center',
  },
  errorMessage: {
    fontSize: 14,
    color: '#666',
    marginBottom: 20,
    textAlign: 'center',
    lineHeight: 20,
  },
  retryButton: {
    backgroundColor: '#2196f3',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 5,
    alignSelf: 'center',
  },
  retryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  debugContainer: {
    marginTop: 20,
    padding: 10,
    backgroundColor: '#f5f5f5',
    borderRadius: 5,
  },
  debugTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  debugText: {
    fontSize: 10,
    color: '#666',
    fontFamily: 'monospace',
  },
});

// RAG专用错误边界
export const RAGErrorBoundary: React.FC<{ children: ReactNode }> = ({ children }) => {
  const handleRAGError = (error: Error, errorInfo: string) => {
    // RAG特定的错误处理逻辑
    console.error('RAG Error:', error);
    
    // 可以在这里添加错误上报逻辑
    // errorReportingService.report(error, { context: 'RAG', errorInfo });
  };

  const ragFallback = (error: Error, retry: () => void) => (
    <View style={styles.container}>
      <View style={styles.errorContainer}>
        <Text style={styles.errorTitle}>RAG服务暂时不可用</Text>
        <Text style={styles.errorMessage}>
          {error.message.includes('网络') 
            ? '请检查网络连接后重试' 
            : '服务正在维护中，请稍后再试'}
        </Text>
        
        <TouchableOpacity style={styles.retryButton} onPress={retry}>
          <Text style={styles.retryButtonText}>重新连接</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <ErrorBoundary fallback={ragFallback} onError={handleRAGError}>
      {children}
    </ErrorBoundary>
  );
};