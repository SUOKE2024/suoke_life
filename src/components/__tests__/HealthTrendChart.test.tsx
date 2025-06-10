import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import HealthTrendChart from '../HealthTrendChart.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('HealthTrendChart', () => {

    const { getByTestId } = renderWithProvider(<HealthTrendChart />);
    expect(getByTestId('healthtrendchart')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <HealthTrendChart onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('healthtrendchart'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<HealthTrendChart {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <HealthTrendChart error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <HealthTrendChart loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});