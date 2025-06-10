import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import BlockchainHealthData from '../BlockchainHealthData.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('BlockchainHealthData', () => {

    const { getByTestId } = renderWithProvider(<BlockchainHealthData />);
    expect(getByTestId('blockchainhealthdata')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <BlockchainHealthData onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('blockchainhealthdata'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<BlockchainHealthData {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <BlockchainHealthData error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <BlockchainHealthData loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});