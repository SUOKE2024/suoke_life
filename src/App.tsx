import React from 'react';
import { StatusBar, useColorScheme } from 'react-native';
import { Provider as PaperProvider, MD3LightTheme, MD3DarkTheme } from 'react-native-paper';
import { NavigationContainer } from '@react-navigation/native';
import { Provider as ReduxProvider } from 'react-redux';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { I18nextProvider } from 'react-i18next';

import AppNavigator from './navigation/AppNavigator';
import { store } from './store';
import i18n from './config/i18n';
import { lightTheme, darkTheme } from './config/theme';

/**
 * 索克生活APP入口组件
 * 负责初始化全局提供者和配置
 */
const App: React.FC = () => {
  const colorScheme = useColorScheme();
  const isDarkMode = colorScheme === 'dark';

  // 合并 React Native Paper 主题与自定义主题
  const paperTheme = isDarkMode 
    ? { ...MD3DarkTheme, ...darkTheme } 
    : { ...MD3LightTheme, ...lightTheme };

  return (
    <SafeAreaProvider>
      <ReduxProvider store={store}>
        <I18nextProvider i18n={i18n}>
          <PaperProvider theme={paperTheme}>
            <NavigationContainer>
              <StatusBar 
                barStyle={isDarkMode ? 'light-content' : 'dark-content'}
                backgroundColor={paperTheme.colors.background}
              />
              <AppNavigator />
            </NavigationContainer>
          </PaperProvider>
        </I18nextProvider>
      </ReduxProvider>
    </SafeAreaProvider>
  );
};

export default App;
