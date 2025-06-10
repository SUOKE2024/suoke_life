import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import HealthDataManager from '../HealthDataManager.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('HealthDataManager', () => {

    const { getByTestId } = renderWithProvider(<HealthDataManager />);
    expect(getByTestId('healthdatamanager')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <HealthDataManager onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('healthdatamanager'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<HealthDataManager {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <HealthDataManager error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <HealthDataManager loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});