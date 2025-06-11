import { createNativeStackNavigator } from "@react-navigation/native-stack"
import React from "react";
import {AuthStackParamList,
ForgotPasswordScreen,
LoginScreen,"
RegisterScreen,";
} fromelcomeScreen'}
} from "../screens/auth"
const AuthStack = createNativeStackNavigator<AuthStackParamList>();
export const AuthNavigator: React.FC = () => {'return (<AuthStack.Navigator;'  />/,)initialRouteName="Welcome"","/g"/;
screenOptions={"headerShown: false,","
animation: 'slide_from_right,'';
gestureEnabled: true,
}
        const gestureDirection = 'horizontal'}
      }
    >'
      <AuthStack.Screen;'  />/,'/g'/;
name="Welcome
component={WelcomeScreen}","
options={ animation: 'fade' }
      />'/;'/g'/;
      <AuthStack.Screen;'  />/,'/g'/;
name="Login
component={LoginScreen}","
options={ animation: 'slide_from_bottom' }
      />'/;'/g'/;
      <AuthStack.Screen;'  />/,'/g'/;
name="Register
component={RegisterScreen}","
options={ animation: 'slide_from_right' }
      />'/;'/g'/;
      <AuthStack.Screen;'  />/,'/g'/;
name="ForgotPassword
component={ForgotPasswordScreen}","
options={ animation: 'slide_from_right' ;}}')'
      />)
    </AuthStack.Navigator>)
  );
};
''