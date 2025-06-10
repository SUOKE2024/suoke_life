import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import AgentChatBubble from '../AgentChatBubble.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('AgentChatBubble', () => {

    const { getByTestId } = renderWithProvider(<AgentChatBubble />);
    expect(getByTestId('agentchatbubble')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <AgentChatBubble onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('agentchatbubble'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<AgentChatBubble {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <AgentChatBubble error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <AgentChatBubble loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});