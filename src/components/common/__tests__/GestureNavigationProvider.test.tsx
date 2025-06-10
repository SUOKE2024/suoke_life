import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import GestureNavigationProvider from '../GestureNavigationProvider.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('GestureNavigationProvider', () => {

    const { getByTestId } = renderWithProvider(<GestureNavigationProvider />);
    expect(getByTestId('gesturenavigationprovider')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <GestureNavigationProvider onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('gesturenavigationprovider'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<GestureNavigationProvider {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <GestureNavigationProvider error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <GestureNavigationProvider loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});