import { useCallback } from 'react';
import { useNavigation } from '@react-navigation/native';
import { Alert } from 'react-native';

export interface UseScreenNavigationReturn {
  goBack: () => void;
  goToHome: () => void;
  goToProfile: () => void;
  goToSettings: () => void;
  goToLogin: () => void;
  goToRegister: () => void;
  showAlert: (title: string, message: string, onConfirm?: () => void) => void;
  showConfirm: (title: string, message: string, onConfirm: () => void, onCancel?: () => void) => void;
}

export const useScreenNavigation = (): UseScreenNavigationReturn => {
  const navigation = useNavigation();

  const goBack = useCallback(() => {
    if (navigation.canGoBack()) {
      navigation.goBack();
    }
  }, [navigation]);

  const goToHome = useCallback(() => {
    navigation.navigate('Home' as never);
  }, [navigation]);

  const goToProfile = useCallback(() => {
    navigation.navigate('Profile' as never);
  }, [navigation]);

  const goToSettings = useCallback(() => {
    navigation.navigate('Settings' as never);
  }, [navigation]);

  const goToLogin = useCallback(() => {
    navigation.navigate('Login' as never);
  }, [navigation]);

  const goToRegister = useCallback(() => {
    navigation.navigate('Register' as never);
  }, [navigation]);

  const showAlert = useCallback((
    title: string, 
    message: string, 
    onConfirm?: () => void
  ) => {
    Alert.alert(
      title,
      message,
      [
        {
          text: '确定',
          onPress: onConfirm,
        },
      ]
    );
  }, []);

  const showConfirm = useCallback((
    title: string,
    message: string,
    onConfirm: () => void,
    onCancel?: () => void
  ) => {
    Alert.alert(
      title,
      message,
      [
        {
          text: '取消',
          style: 'cancel',
          onPress: onCancel,
        },
        {
          text: '确定',
          onPress: onConfirm,
        },
      ]
    );
  }, []);

  return {
    goBack,
    goToHome,
    goToProfile,
    goToSettings,
    goToLogin,
    goToRegister,
    showAlert,
    showConfirm,
  };
};