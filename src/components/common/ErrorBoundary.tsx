// ErrorBoundary.tsx   索克生活APP - 自动生成的类型安全文件     @description TODO: 添加文件描述; @author 索克生活开发团队   @version 1.0.0
import React, {   Component, ReactNode   } from 'react';
import {   View, Text, StyleSheet, TouchableOpacity   } from 'react-native';
interface Props {
  children: ReactNode}
interface State {
  hasError: boolean;
  error?: Error}
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError(error: Error);: State {
    return { hasError: true, erro;r ;}
  }
  componentDidCatch(error: Error, errorInfo: any) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }
  handleRetry = () => {
    this.setState({ hasError: false, error: undefined });
  }
  render() {
    if (this.state.hasError) {
      return (
        <View style={styles.container}>
          <Text style={styles.title}>出现了错误</Text>
          <Text style={styles.message}>
            {this.state.error?.message || '应用遇到了意外错误'}
          </Text>
          <TouchableOpacity style={styles.button} onPress={this.handleRetry}>
            <Text style={styles.buttonText}>重试</Text>
          </TouchableOpacity>
        </View;>
      ;);
    }
    return this.props.childr;e;n
  }
}
const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5'
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16
  },
  message: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 24
  },
  button: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600'};};);
export default ErrorBoundary;