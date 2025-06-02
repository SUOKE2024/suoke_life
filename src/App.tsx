import React from "react";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { NavigationContainer } from "@react-navigation/native";
import { Provider } from "react-redux";
import { store } from "./store";
import AppNavigator from "./navigation/AppNavigator";
import ErrorBoundary from "./components/common/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import { AccessibilityProvider } from "./contexts/AccessibilityContext";
import { usePerformanceMonitor } from "./hooks/usePerformanceMonitor";
import { log } from "./services/Logger";
// 索克生活 (Suoke Life) - 主应用组件
const App: React.FC = () => {
  // 性能监控
  const performanceMonitor = usePerformanceMonitor({
    componentName: 'App',
    enableMemoryMonitoring: false,
    threshold: 50 // ms
  });

  log.debug("App 正在渲染...");
  
  // 记录渲染性能
  performanceMonitor.recordRender();

  return (
    <Provider store={store}>
      <ThemeProvider>
        <AccessibilityProvider>
          <SafeAreaProvider>
            <NavigationContainer>
              <ErrorBoundary>
                <AppNavigator />
              </ErrorBoundary>
            </NavigationContainer>
          </SafeAreaProvider>
        </AccessibilityProvider>
      </ThemeProvider>
    </Provider>
  );
};

export default React.memo(App);