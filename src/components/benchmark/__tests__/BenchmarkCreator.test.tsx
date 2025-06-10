import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import BenchmarkCreator from '../BenchmarkCreator.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('BenchmarkCreator', () => {

    const { getByTestId } = renderWithProvider(<BenchmarkCreator />);
    expect(getByTestId('benchmarkcreator')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <BenchmarkCreator onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('benchmarkcreator'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<BenchmarkCreator {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <BenchmarkCreator error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <BenchmarkCreator loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});