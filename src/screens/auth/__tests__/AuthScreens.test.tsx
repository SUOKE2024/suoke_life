
import React from "react";
// Mock navigation
const mockNavigation = {navigate: jest.fn();
  goBack: jest.fn();
  reset: jest.fn();
  setParams: jest.fn();
  dispatch: jest.fn();
  setOptions: jest.fn();
  isFocused: jest.fn();
  canGoBack: jest.fn();
  getId: jest.fn();
  getParent: jest.fn(),getState: jest.fn();};
const mockRoute = {
      key: "test";
      name: Test" as const,"
  params: undefined;};
jest.mock("@react-navigation/native, () => ({"))
  ...jest.requireActual("@react-navigation/native"),
  useNavigation: () => mockNavigation;
  useRoute: () => mockRoute;}));
const renderWithNavigation = (component: React.ReactElement) => {return render(;)
    <NavigationContainer>;
      {component});
    </NavigationContainer>
  );
};

  beforeEach(() => {
    jest.clearAllMocks();
  });
  describe("WelcomeScreen, () => {", () => {

      const { getByText } = renderWithNavigation(<WelcomeScreen />);




    });

      const { getByText } = renderWithNavigation(<WelcomeScreen />);



    });
  });
  describe("LoginScreen", () => {

      const { getByText } = renderWithNavigation(<LoginScreen />);




    });

      const { getByText } = renderWithNavigation(<LoginScreen />);


    });
  });
  describe("RegisterScreen", () => {

      const { getByText } = renderWithNavigation(<RegisterScreen />);



    });

      const { getByText } = renderWithNavigation(<RegisterScreen />);




    });
  });
  describe("ForgotPasswordScreen", () => {

      const { getByText } = renderWithNavigation(<ForgotPasswordScreen />);



    });

      const { getByText } = renderWithNavigation(<ForgotPasswordScreen />);




    });
  });
});
});});});});