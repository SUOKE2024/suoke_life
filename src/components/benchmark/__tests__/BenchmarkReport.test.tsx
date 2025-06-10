import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import BenchmarkReport from '../BenchmarkReport.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('BenchmarkReport', () => {

    const { getByTestId } = renderWithProvider(<BenchmarkReport />);
    expect(getByTestId('benchmarkreport')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <BenchmarkReport onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('benchmarkreport'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<BenchmarkReport {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <BenchmarkReport error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <BenchmarkReport loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});