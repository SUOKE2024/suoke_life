import { createNativeStackNavigator } from '@react-navigation/native-stack';
import React from 'react';
import {;
  AuthStackParamList,
  ForgotPasswordScreen,
  LoginScreen,
  RegisterScreen,
  WelcomeScreen
} from '../screens/auth';

const AuthStack = createNativeStackNavigator<AuthStackParamList>();

export const AuthNavigator: React.FC = () => {
  return (
    <AuthStack.Navigator;
      initialRouteName="Welcome"
      screenOptions={
        headerShown: false;
        animation: 'slide_from_right';
        gestureEnabled: true;
        gestureDirection: 'horizontal'
      ;}}
    >
      <AuthStack.Screen;
        name="Welcome"
        component={WelcomeScreen}
        options={ animation: 'fade' ;}}
      />
      <AuthStack.Screen;
        name="Login"
        component={LoginScreen}
        options={ animation: 'slide_from_bottom' ;}}
      />
      <AuthStack.Screen;
        name="Register"
        component={RegisterScreen}
        options={ animation: 'slide_from_right' ;}}
      />
      <AuthStack.Screen;
        name="ForgotPassword"
        component={ForgotPasswordScreen}
        options={ animation: 'slide_from_right' ;}}
      />
    </AuthStack.Navigator>
  );
};
