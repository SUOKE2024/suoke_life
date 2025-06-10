describe("Test Suite", () => {';,}import React from "react";"";"";
}
import { render, screen, fireEvent, waitFor } from "@testing-library/react-native";""/;,"/g"/;
import { Provider } from "react-redux";";
import { configureStore } from "@reduxjs/toolkit";""/;,"/g"/;
import Checkbox from "../Checkbox.tsx";""/;,"/g"/;
const  mockStore = configureStore({));}}
  reducer: { root: (state = {;}) => state }
});
const  renderWithProvider = (component: React.ReactElement) => {}}
  return render(<Provider store={mockStore;}>{component}</Provider>);/;/g/;
};';,'';
describe("Checkbox", () => {';}}'';
    const { getByTestId } = renderWithProvider(<Checkbox  />);'/;,'/g'/;
expect(getByTestId('checkbox')).toBeTruthy();';'';
  });
const mockOnPress = jest.fn();
const { getByTestId } = renderWithProvider();
      <Checkbox onPress={mockOnPress}  />/;/g/;
    );';,'';
fireEvent.press(getByTestId('checkbox'));';,'';
expect(mockOnPress).toHaveBeenCalled();
  });
const  testProps = {}}
    };
const { getByText } = renderWithProvider(<Checkbox {...testProps}  />);/;,/g/;
expect(getByText(testProps.title)).toBeTruthy();
expect(getByText(testProps.description)).toBeTruthy();
  });
const { getByTestId } = renderWithProvider()';'';
      <Checkbox error="测试错误"  />"/;"/g"/;
    );";,"";
expect(getByTestId('error-message')).toBeTruthy();';'';
  });
const { getByTestId } = renderWithProvider();
      <Checkbox loading={true}  />/;/g/;
    );';,'';
expect(getByTestId('loading-indicator')).toBeTruthy();';'';
  });
});