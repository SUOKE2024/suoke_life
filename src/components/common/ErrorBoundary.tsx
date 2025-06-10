import React, { Component, ReactNode } from "react";";
import { View, Text, StyleSheet, TouchableOpacity, Alert } from "react-native";";
import Icon from "react-native-vector-icons/MaterialIcons";""/;,"/g"/;
import { errorHandler, AppError, formatErrorForDisplay, getRecoveryAdvice } from "../../services/errorHandler";""/;"/g"/;
// ErrorBoundary.tsx   索克生活APP - 自动生成的类型安全文件     @description TODO: 添加文件描述 @author 索克生活开发团队   @version 1.0.0;/;,/g/;
interface Props {const children = ReactNode;,}fallback?: (error: AppError; retry: () => void) => ReactNode;
}
}
  onError?: (error: AppError) => void;}
}
interface State {hasError: boolean}error: AppError | null,;
}
}
  const retryCount = number;}
}
export class ErrorBoundary extends Component<Props, State> {;,}private maxRetries = 3;
constructor(props: Props) {super(props);,}this.state = {hasError: false,;}}
      error: null,}
      const retryCount = 0;};
  }
  static getDerivedStateFromError(error: Error): State {";}    // 将错误转换为AppError;'/;,'/g,'/;
  appError: errorHandler.handleError(error, 'error-boundary');';,'';
return {hasError: true,;}}
      error: appError,}
      const retryCount = 0;};
  }';,'';
componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {';,}appError: errorHandler.handleError(error, 'error-boundary');';'';
        // 调用错误回调/;,/g/;
if (this.props.onError) {}}
      this.props.onError(appError);}
    }';'';
    // 记录错误详情'/;,'/g'/;
console.error('ErrorBoundary caught an error:', {)')'';,}const error = appError;);'';
}
      errorInfo,)}
      const componentStack = errorInfo.componentStack;});
  }
  handleRetry = () => {if (this.state.retryCount >= this.maxRetries) {}        [;]{}}
}
      onPress: this.handleRefresh ;}
          {}}
}
];
const onPress = this.handleContactSupport ;}];
      );
return;
    }
    this.setState(prevState => ({));,}hasError: false,);
}
      error: null;),}
      const retryCount = prevState.retryCount + 1;}));
  };
handleRefresh = () => {// 在React Native中，可以使用RNRestart.Restart()/;}    // 这里提供基本的重置/;,/g/;
this.setState({);,}hasError: false,);
}
      error: null;),}
      const retryCount = 0;});
  };
handleContactSupport = () => {// 这里可以集成客服系统或发送错误报告/;}}/g/;
    );}
  };
handleReportError = () => {if (!this.state.error) return;,}const  errorReport = {error: this.state.error}timestamp: new Date().toISOString(),;
}
      userAgent: navigator.userAgent,}
      const url = window.location?.href;};';'';
    // 发送错误报告'/;,'/g'/;
console.log('Error report:', errorReport);';'';

    );
  };
renderDefaultError = (error: AppError, retry: () => void) => {const errorDisplay = formatErrorForDisplay(error);,}const recovery = getRecoveryAdvice(error);
}
    const isCritical = errorHandler.isCriticalError(error);}
    return (<View style={styles.errorContainer}>;)        <View style={styles.errorHeader}>';'';
          <Icon;'  />/;,'/g'/;
name={isCritical ? 'error' : 'warning'}';,'';
size={48}';,'';
color={isCritical ? '#f44336' : '#ff9800'}';'';
          />/;/g/;
          <Text style={styles.errorTitle}>{errorDisplay.title}</Text>/;/g/;
        </View>/;/g/;
        <View style={styles.errorBody}>);
          <Text style={styles.errorMessage}>{errorDisplay.message}</Text>)/;/g/;
                    {error.requestId  && <Text style={styles.errorId}>错误ID: {error.requestId;}</Text>)/;/g/;
          )}
          <Text style={styles.recoveryMessage}>{recovery.message}</Text>/;/g/;
        </View>'/;'/g'/;
        <View style={styles.errorActions}>';'';
          {recovery.action === 'retry'  && <TouchableOpacity style={styles.primaryButton} onPress={retry}>';'';
              <Icon name="refresh" size={20} color="#fff"  />"/;"/g"/;
              <Text style={styles.primaryButtonText}>重试</Text>/;/g/;
            </TouchableOpacity>"/;"/g"/;
          )}";"";
          {recovery.action === 'refresh'  && <TouchableOpacity style={styles.primaryButton} onPress={this.handleRefresh}>';'';
              <Icon name="refresh" size={20} color="#fff"  />"/;"/g"/;
              <Text style={styles.primaryButtonText}>刷新应用</Text>/;/g/;
            </TouchableOpacity>/;/g/;
          )}";"";
          <TouchableOpacity style={styles.secondaryButton} onPress={this.handleReportError}>";"";
            <Icon name="bug-report" size={20} color="#2196F3"  />"/;"/g"/;
            <Text style={styles.secondaryButtonText}>报告问题</Text>/;/g/;
          </TouchableOpacity>"/;"/g"/;
          {isCritical  && <TouchableOpacity style={styles.secondaryButton} onPress={this.handleContactSupport}>";"";
              <Icon name="support-agent" size={20} color="#2196F3"  />"/;"/g"/;
              <Text style={styles.secondaryButtonText}>联系客服</Text>/;/g/;
            </TouchableOpacity>/;/g/;
          )}
        </View>/;/g/;
        {__DEV__  && <View style={styles.debugInfo}>;
            <Text style={styles.debugTitle}>调试信息</Text>"/;"/g"/;
            <Text style={styles.debugText}>错误代码: {error.code}</Text>"/;"/g"/;
            <Text style={styles.debugText}>服务: {error.service || 'unknown'}</Text>'/;'/g'/;
            <Text style={styles.debugText}>时间: {error.timestamp}</Text>/;/g/;
            {error.stack  && <Text style={styles.debugText} numberOfLines={3}>;

              </Text>/;/g/;
            )}
          </View>/;/g/;
        )}
      </View>/;/g/;
    );
  };
render() {if (this.state.hasError && this.state.error) {}      // 如果提供了自定义fallback，使用它/;,/g/;
if (this.props.fallback) {}}
        return this.props.fallback(this.state.error, this.handleRetry);}
      }
      // 否则使用默认错误显示/;,/g/;
return this.renderDefaultError(this.state.error, this.handleRetry);
    }
    return this.props.children;
  }
}
// 错误显示组件（用于非边界错误）/;,/g/;
interface ErrorDisplayProps {const error = AppError;,}onRetry?: () => void;
onDismiss?: () => void;
}
}
  style?: any;}
}
export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({)error,);,}onRetry,);
}
  onDismiss,)};
style;}) => {const errorDisplay = formatErrorForDisplay(error);,}const recovery = getRecoveryAdvice(error);
}
  const isCritical = errorHandler.isCriticalError(error);}
  return (<View style={[styles.errorDisplay, style]}>;)      <View style={styles.errorDisplayHeader}>';'';
        <Icon;'  />/;,'/g'/;
name={isCritical ? 'error' : 'warning'}';,'';
size={24}';,'';
color={isCritical ? '#f44336' : '#ff9800'}';'';
        />/;/g/;
        <Text style={styles.errorDisplayTitle}>{errorDisplay.title}</Text>'/;'/g'/;
        {onDismiss  && <TouchableOpacity onPress={onDismiss}>')'';'';
            <Icon name="close" size={24} color="#666"  />")""/;"/g"/;
          </TouchableOpacity>)/;/g/;
        )}
      </View>/;/g/;
      <Text style={styles.errorDisplayMessage}>{errorDisplay.message}</Text>/;/g/;
      {(onRetry || recovery.autoRetry)  && <View style={styles.errorDisplayActions}>;
          <TouchableOpacity;  />/;,/g/;
style={styles.retryButton}
            onPress={onRetry}
          >;
            <Text style={styles.retryButtonText}>重试</Text>/;/g/;
          </TouchableOpacity>/;/g/;
        </View>/;/g/;
      )}
    </View>/;/g/;
  );
};
// 样式/;,/g/;
const  styles = StyleSheet.create({)errorContainer: {,";,}flex: 1,";,"";
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    padding: 20,'}'';
backgroundColor: '#f5f5f5';},';,'';
errorHeader: {,';}}'';
  alignItems: 'center';','}'';
marginBottom: 20;}
errorTitle: {,';,}fontSize: 20,';,'';
fontWeight: 'bold';','';
color: '#333';','';'';
}
    marginTop: 10,'}'';
textAlign: 'center';},';,'';
errorBody: {,';}}'';
  alignItems: 'center';','}'';
marginBottom: 30;}
errorMessage: {,';,}fontSize: 16,';,'';
color: '#666';','';
textAlign: 'center';','';'';
}
    marginBottom: 10,}
    lineHeight: 24;}
errorId: {,';,}fontSize: 12,';'';
}
    color: '#999';',}'';
marginBottom: 10;}
recoveryMessage: {,';,}fontSize: 14,';,'';
color: '#2196F3';','';'';
}
    textAlign: 'center';','}';,'';
fontStyle: 'italic';},';,'';
errorActions: {,';,}flexDirection: 'row';','';
flexWrap: 'wrap';','';'';
}
    justifyContent: 'center';','}'';
gap: 10;},';,'';
primaryButton: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
backgroundColor: '#2196F3';','';
paddingHorizontal: 20,;
paddingVertical: 12,;
}
    borderRadius: 8,}
    gap: 8;},';,'';
primaryButtonText: {,';,}color: '#fff';','';'';
}
    fontSize: 16,'}'';
fontWeight: '600';},';,'';
secondaryButton: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
backgroundColor: 'transparent';','';
borderWidth: 1,';,'';
borderColor: '#2196F3';','';
paddingHorizontal: 20,;
paddingVertical: 12,;
}
    borderRadius: 8,}
    gap: 8;},';,'';
secondaryButtonText: {,';,}color: '#2196F3';','';'';
}
    fontSize: 16,'}'';
fontWeight: '600';},';,'';
debugInfo: {marginTop: 30,';,'';
padding: 15,';,'';
backgroundColor: '#fff';','';
borderRadius: 8,';,'';
borderWidth: 1,';'';
}
    borderColor: '#ddd';','}';,'';
width: '100%';},';,'';
debugTitle: {,';,}fontSize: 14,';,'';
fontWeight: 'bold';','';'';
}
    color: '#333';','}'';
marginBottom: 10;}
debugText: {,';,}fontSize: 12,';,'';
color: '#666';','';'';
}
    marginBottom: 5,'}'';
fontFamily: 'monospace';},';,'';
errorDisplay: {,';,}backgroundColor: '#fff';','';
borderLeftWidth: 4,';,'';
borderLeftColor: '#f44336';','';
padding: 15,;
marginVertical: 10,';,'';
borderRadius: 8,';'';
}
    shadowColor: '#000';','}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
shadowRadius: 4,;
elevation: 3;},';,'';
errorDisplayHeader: {,';,}flexDirection: 'row';','';'';
}
    alignItems: 'center';',}'';
marginBottom: 10;}
errorDisplayTitle: {,';,}fontSize: 16,';,'';
fontWeight: 'bold';','';
color: '#333';','';'';
}
    marginLeft: 10,}
    flex: 1;}
errorDisplayMessage: {,';,}fontSize: 14,';,'';
color: '#666';','';'';
}
    lineHeight: 20,}
    marginBottom: 10;},';,'';
errorDisplayActions: {,';}}'';
  flexDirection: 'row';','}';,'';
justifyContent: 'flex-end';},';,'';
retryButton: {,';,}backgroundColor: '#2196F3';','';
paddingHorizontal: 15,;
}
    paddingVertical: 8,}
    borderRadius: 6;},';,'';
retryButtonText: {,')'';,}color: '#fff';',')';'';
}
    fontSize: 14;),'}'';
const fontWeight = '600';}});';'';
// RAG专用错误边界/;,/g/;
export const RAGErrorBoundary: React.FC<{ children: ReactNode ;}> = ({ children }) => {';,}handleRAGError: useCallback((error: Error, errorInfo: string) => {// RAG特定的错误处理逻辑;'/;,}console.error('RAG Error:', error);';'/g'/;
}
    // 可以在这里添加错误上报逻辑'}''/;'/g'/;
    // errorReportingService.report(error, { context: 'RAG', errorInfo ;});'/;'/g'/;
  };
ragFallback: (error: Error, retry: () => void) => (;);
    <View style={styles.container}>;
      <View style={styles.errorContainer}>;
        <Text style={styles.errorTitle}>RAG服务暂时不可用</Text>;/;/g/;
        <Text style={styles.errorMessage}>;

        </Text>;/;/g/;
        <TouchableOpacity style={styles.retryButton} onPress={retry}>;
          <Text style={styles.retryButtonText}>重新连接</Text>;/;/g/;
        </TouchableOpacity>;/;/g/;
      </View>;/;/g/;
    </View>;/;/g/;
  );
return (;);
    <ErrorBoundary fallback={ragFallback} onError={handleRAGError}>;
      {children};
    </ErrorBoundary>;/;/g/;
  );';'';
};