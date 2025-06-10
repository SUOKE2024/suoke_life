import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import BenchmarkResultDetail from '../BenchmarkResultDetail.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('BenchmarkResultDetail', () => {

    const { getByTestId } = renderWithProvider(<BenchmarkResultDetail />);
    expect(getByTestId('benchmarkresultdetail')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <BenchmarkResultDetail onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('benchmarkresultdetail'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<BenchmarkResultDetail {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <BenchmarkResultDetail error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <BenchmarkResultDetail loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});