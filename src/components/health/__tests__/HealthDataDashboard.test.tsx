import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import HealthDataDashboard from '../HealthDataDashboard.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('HealthDataDashboard', () => {

    const { getByTestId } = renderWithProvider(<HealthDataDashboard />);
    expect(getByTestId('healthdatadashboard')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <HealthDataDashboard onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('healthdatadashboard'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<HealthDataDashboard {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <HealthDataDashboard error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <HealthDataDashboard loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});