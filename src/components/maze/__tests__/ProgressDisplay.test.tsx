import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import ProgressDisplay from '../ProgressDisplay.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('ProgressDisplay', () => {

    const { getByTestId } = renderWithProvider(<ProgressDisplay />);
    expect(getByTestId('progressdisplay')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <ProgressDisplay onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('progressdisplay'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<ProgressDisplay {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <ProgressDisplay error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <ProgressDisplay loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});