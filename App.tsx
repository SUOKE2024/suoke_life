import React from 'react';
import { StatusBar } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { PaperProvider } from 'react-native-paper';
import { Provider } from 'react-redux';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { I18nextProvider } from 'react-i18next';
import { store } from './src/store';
import AppNavigator from './src/navigation/AppNavigator';
import { lightTheme } from './src/config/theme';
import i18n from './src/config/i18n';

const App: React.FC = () => {
  console.log('索克生活App启动成功');
  
  return (
    <Provider store={store}>
      <SafeAreaProvider>
        <PaperProvider theme={lightTheme}>
          <I18nextProvider i18n={i18n}>
            <NavigationContainer>
              <StatusBar
                barStyle="dark-content"
                backgroundColor={lightTheme.colors.surface}
                translucent={false}
              />
              <AppNavigator />
            </NavigationContainer>
          </I18nextProvider>
        </PaperProvider>
      </SafeAreaProvider>
    </Provider>
  );
};

export default App;