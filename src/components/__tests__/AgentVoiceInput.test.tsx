import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import AgentVoiceInput from '../AgentVoiceInput.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('AgentVoiceInput', () => {

    const { getByTestId } = renderWithProvider(<AgentVoiceInput />);
    expect(getByTestId('agentvoiceinput')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <AgentVoiceInput onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('agentvoiceinput'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<AgentVoiceInput {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <AgentVoiceInput error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <AgentVoiceInput loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});