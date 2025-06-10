import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import BenchmarkDashboard from '../BenchmarkDashboard.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('BenchmarkDashboard', () => {

    const { getByTestId } = renderWithProvider(<BenchmarkDashboard />);
    expect(getByTestId('benchmarkdashboard')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <BenchmarkDashboard onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('benchmarkdashboard'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<BenchmarkDashboard {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <BenchmarkDashboard error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <BenchmarkDashboard loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});