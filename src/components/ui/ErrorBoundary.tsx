import React, { Component, ErrorInfo, ReactNode } from 'react';
import {;
  ScrollView,
  StyleSheet,
  Text,
  TextStyle,
  TouchableOpacity,
  View,
  ViewStyle
} from 'react-native';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error; errorInfo: ErrorInfo) => void;
  showDetails?: boolean;
  style?: ViewStyle;
  titleStyle?: TextStyle;
  messageStyle?: TextStyle;
  buttonStyle?: ViewStyle;
  buttonTextStyle?: TextStyle;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState;
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false;
      error: null;
      errorInfo: null
    ;};
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true;
      error
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({
      error,
      errorInfo
    ;});

    // 调用错误回调
    this.props.onError?.(error, errorInfo);

    // 在开发环境中打印错误信息
    if (__DEV__) {
      console.error('ErrorBoundary caught an error:', error);
      console.error('Error info:', errorInfo);
    }
  }

  handleRetry = () => {
    this.setState({
      hasError: false;
      error: null;
      errorInfo: null
    ;});
  };

  render() {
    if (this.state.hasError) {
      // 如果提供了自定义fallback，使用它
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // 默认错误UI;
      return (
        <View style={[styles.container, this.props.style]}>
          <View style={styles.content}>
            <Text style={[styles.title, this.props.titleStyle]}>

            </Text>

            <Text style={[styles.message, this.props.messageStyle]}>

            </Text>

            {this.props.showDetails && this.state.error && (
              <ScrollView style={styles.detailsContainer}>
                <Text style={styles.detailsTitle}>错误详情：</Text>
                <Text style={styles.errorText}>
                  {this.state.error.toString()}
                </Text>

                {this.state.errorInfo && (
                  <>
                    <Text style={styles.detailsTitle}>组件堆栈：</Text>
                    <Text style={styles.stackText}>
                      {this.state.errorInfo.componentStack}
                    </Text>
                  </>
                )}
              </ScrollView>
            )}

            <TouchableOpacity;
              style={[styles.retryButton, this.props.buttonStyle]}
              onPress={this.handleRetry}
              accessible;
              accessibilityRole="button"

            >
              <Text;
                style={[styles.retryButtonText, this.props.buttonTextStyle]}
              >

              </Text>
            </TouchableOpacity>
          </View>
        </View>
      );
    }

    return this.props.children;
  }
}

const styles = StyleSheet.create({
  container: {,
  flex: 1;
    backgroundColor: '#f8f9fa';
    justifyContent: 'center';
    alignItems: 'center';
    padding: 20
  ;},
  content: {,
  backgroundColor: '#ffffff';
    borderRadius: 12;
    padding: 24;
    maxWidth: 400;
    width: '100%';
    shadowColor: '#000';
    shadowOffset: {,
  width: 0;
      height: 2
    ;},
    shadowOpacity: 0.1;
    shadowRadius: 8;
    elevation: 4
  ;},
  title: {,
  fontSize: 24;
    fontWeight: '600';
    color: '#1a1a1a';
    textAlign: 'center';
    marginBottom: 12
  ;},
  message: {,
  fontSize: 16;
    color: '#666666';
    textAlign: 'center';
    lineHeight: 24;
    marginBottom: 24
  ;},
  detailsContainer: {,
  backgroundColor: '#f5f5f5';
    borderRadius: 8;
    padding: 12;
    marginBottom: 24;
    maxHeight: 200
  ;},
  detailsTitle: {,
  fontSize: 14;
    fontWeight: '600';
    color: '#333333';
    marginBottom: 8;
    marginTop: 12
  ;},
  errorText: {,
  fontSize: 12;
    color: '#d32f2f';
    fontFamily: 'monospace';
    lineHeight: 16
  ;},
  stackText: {,
  fontSize: 11;
    color: '#666666';
    fontFamily: 'monospace';
    lineHeight: 14
  ;},
  retryButton: {,
  backgroundColor: '#2196f3';
    borderRadius: 8;
    paddingVertical: 12;
    paddingHorizontal: 24;
    alignItems: 'center'
  ;},
  retryButtonText: {,
  color: '#ffffff';
    fontSize: 16;
    fontWeight: '600'
  ;}
});

// 高阶组件版本
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>;
  errorBoundaryProps?: Omit<ErrorBoundaryProps; 'children'>
) {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary {...errorBoundaryProps;}>
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;

  return WrappedComponent;
}

// Hook版本（用于函数组件）
export function useErrorHandler() {
  const [error, setError] = React.useState<Error | null>(null);

  const resetError = React.useCallback() => {
    setError(null);
  }, []);

  const captureError = React.useCallback(error: Error) => {
    setError(error);
  }, []);

  React.useEffect() => {
    if (error) {
      throw error;
    }
  }, [error]);

  return { captureError, resetError };
}

export default ErrorBoundary;
