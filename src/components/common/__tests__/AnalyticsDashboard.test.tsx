import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import AnalyticsDashboard from '../AnalyticsDashboard.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('AnalyticsDashboard', () => {

    const { getByTestId } = renderWithProvider(<AnalyticsDashboard />);
    expect(getByTestId('analyticsdashboard')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <AnalyticsDashboard onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('analyticsdashboard'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<AnalyticsDashboard {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <AnalyticsDashboard error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <AnalyticsDashboard loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});