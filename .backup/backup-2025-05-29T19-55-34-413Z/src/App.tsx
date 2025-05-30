import { SafeAreaProvider } from "react-native-safe-area-context";
import { NavigationContainer } from "@react-navigation/native";
import { Provider } from "react-redux";
import { store } from "./store";
import { AppNavigator } from "./navigation/AppNavigator";
import ErrorBoundary from "./components/common/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import { AccessibilityProvider } from "./contexts/AccessibilityContext";
import React from "react";

/**
 * 索克生活 (Suoke Life) - 主应用组件
 */

const App: React.FC = () => {
  console.log("App 正在渲染...");

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

export default App;
