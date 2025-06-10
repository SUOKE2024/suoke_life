describe("Test Suite", () => {';,}import React from "react";"";"";
}
import { render, screen, fireEvent, waitFor } from "@testing-library/react-native";""/;,"/g"/;
import { Provider } from "react-redux";";
import { configureStore } from "@reduxjs/toolkit";""/;,"/g"/;
import HomeHeader from "../HomeHeader.tsx";""/;,"/g"/;
const  mockStore = configureStore({));}}
  reducer: { root: (state = {;}) => state }
});
const  renderWithProvider = (component: React.ReactElement) => {}}
  return render(<Provider store={mockStore;}>{component}</Provider>);/;/g/;
};';,'';
describe("HomeHeader", () => {';}}'';
    const { getByTestId } = renderWithProvider(<HomeHeader  />);'/;,'/g'/;
expect(getByTestId('homeheader')).toBeTruthy();';'';
  });
const mockOnPress = jest.fn();
const { getByTestId } = renderWithProvider();
      <HomeHeader onPress={mockOnPress}  />/;/g/;
    );';,'';
fireEvent.press(getByTestId('homeheader'));';,'';
expect(mockOnPress).toHaveBeenCalled();
  });
const  testProps = {}}
    };
const { getByText } = renderWithProvider(<HomeHeader {...testProps}  />);/;,/g/;
expect(getByText(testProps.title)).toBeTruthy();
expect(getByText(testProps.description)).toBeTruthy();
  });
const { getByTestId } = renderWithProvider()';'';
      <HomeHeader error="测试错误"  />"/;"/g"/;
    );";,"";
expect(getByTestId('error-message')).toBeTruthy();';'';
  });
const { getByTestId } = renderWithProvider();
      <HomeHeader loading={true}  />/;/g/;
    );';,'';
expect(getByTestId('loading-indicator')).toBeTruthy();';'';
  });
});