import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import MessageSubscriber from '../MessageSubscriber.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('MessageSubscriber', () => {

    const { getByTestId } = renderWithProvider(<MessageSubscriber />);
    expect(getByTestId('messagesubscriber')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <MessageSubscriber onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('messagesubscriber'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<MessageSubscriber {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <MessageSubscriber error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <MessageSubscriber loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});