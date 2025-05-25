/**
 * 索克生活 (Suoke Life) - 主应用组件
 * @format
 */

import React from 'react';
import { StatusBar, useColorScheme } from 'react-native';
import { Provider as PaperProvider, DefaultTheme, MD3DarkTheme } from 'react-native-paper';
import { NavigationContainer } from '@react-navigation/native';
import { Provider as ReduxProvider } from 'react-redux';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { enableScreens } from 'react-native-screens';

// Store
import { store } from './store';

// Navigation
import { AppNavigator } from './navigation/AppNavigator';

// Theme
import { colors } from './constants/theme';

// 启用屏幕优化
enableScreens();

/**
 * 索克生活 (Suoke Life) - 主应用组件
 * 负责初始化全局提供者和配置
 */
const App: React.FC = () => {
  const colorScheme = useColorScheme();
  const isDarkMode = colorScheme === 'dark';

  // 配置主题
  const paperTheme = isDarkMode 
    ? { 
        ...MD3DarkTheme, 
        colors: { 
          ...MD3DarkTheme.colors, 
          primary: colors.primary,
          accent: colors.secondary,
        } 
      } 
    : { 
        ...DefaultTheme, 
        colors: { 
          ...DefaultTheme.colors, 
          primary: colors.primary,
          accent: colors.secondary,
        } 
      };

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <ReduxProvider store={store}>
          <PaperProvider theme={paperTheme}>
            <NavigationContainer>
              <StatusBar 
                barStyle={isDarkMode ? 'light-content' : 'dark-content'}
                backgroundColor={paperTheme.colors.surface}
                translucent={true}
              />
              <AppNavigator />
            </NavigationContainer>
          </PaperProvider>
        </ReduxProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
};

export default App;
