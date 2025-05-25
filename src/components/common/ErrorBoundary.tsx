import React, { Component, ReactNode } from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { Button } from 'react-native-paper';
import { colors, fonts, spacing } from '../../constants/theme';

interface Props {
  children: ReactNode;
  fallback?: (error: Error, errorInfo: string) => ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: string;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({
      error,
      errorInfo: errorInfo?.componentStack || '',
    });

    // 这里可以添加错误日志报告
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // TODO: 发送错误报告到服务器
    // this.reportErrorToService(error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      // 使用自定义回退UI（如果提供）
      if (this.props.fallback && this.state.error) {
        return this.props.fallback(
          this.state.error,
          this.state.errorInfo || ''
        );
      }

      // 默认错误UI
      return (
        <View style={styles.container}>
          <View style={styles.content}>
            <Text style={styles.title}>应用出现错误</Text>
            <Text style={styles.message}>
              抱歉，应用遇到了一个意外错误。我们正在努力修复这个问题。
            </Text>

            <Button
              mode="contained"
              onPress={this.handleReset}
              style={styles.button}
              labelStyle={styles.buttonText}
            >
              重新加载
            </Button>

            {__DEV__ && this.state.error && (
              <ScrollView style={styles.errorDetails}>
                <Text style={styles.errorTitle}>错误详情（开发模式）:</Text>
                <Text style={styles.errorText}>
                  {this.state.error.name}: {this.state.error.message}
                </Text>
                {this.state.errorInfo && (
                  <>
                    <Text style={styles.errorTitle}>组件堆栈:</Text>
                    <Text style={styles.errorText}>{this.state.errorInfo}</Text>
                  </>
                )}
                {this.state.error.stack && (
                  <>
                    <Text style={styles.errorTitle}>错误堆栈:</Text>
                    <Text style={styles.errorText}>
                      {this.state.error.stack}
                    </Text>
                  </>
                )}
              </ScrollView>
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
    backgroundColor: colors.background,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.lg,
  },
  content: {
    maxWidth: 400,
    width: '100%',
    alignItems: 'center',
  },
  title: {
    fontSize: fonts.size.title,
    fontWeight: 'bold',
    color: colors.error,
    textAlign: 'center',
    marginBottom: spacing.md,
  },
  message: {
    fontSize: fonts.size.md,
    color: colors.text,
    textAlign: 'center',
    lineHeight: fonts.lineHeight.md,
    marginBottom: spacing.xl,
  },
  button: {
    marginBottom: spacing.lg,
    paddingHorizontal: spacing.lg,
  },
  buttonText: {
    fontSize: fonts.size.md,
    fontWeight: '600',
  },
  errorDetails: {
    maxHeight: 300,
    width: '100%',
    backgroundColor: colors.surface,
    borderRadius: 8,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  errorTitle: {
    fontSize: fonts.size.sm,
    fontWeight: 'bold',
    color: colors.error,
    marginTop: spacing.sm,
    marginBottom: spacing.xs,
  },
  errorText: {
    fontSize: fonts.size.xs,
    color: colors.textSecondary,
    fontFamily: 'monospace',
    lineHeight: fonts.lineHeight.xs,
  },
});

export default ErrorBoundary;
