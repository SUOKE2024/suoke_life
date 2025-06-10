import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import BenchmarkMonitor from '../BenchmarkMonitor.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('BenchmarkMonitor', () => {

    const { getByTestId } = renderWithProvider(<BenchmarkMonitor />);
    expect(getByTestId('benchmarkmonitor')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <BenchmarkMonitor onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('benchmarkmonitor'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<BenchmarkMonitor {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <BenchmarkMonitor error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <BenchmarkMonitor loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});