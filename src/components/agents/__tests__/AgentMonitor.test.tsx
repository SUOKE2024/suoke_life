import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import AgentMonitor from '../AgentMonitor.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('AgentMonitor', () => {

    const { getByTestId } = renderWithProvider(<AgentMonitor />);
    expect(getByTestId('agentmonitor')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <AgentMonitor onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('agentmonitor'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<AgentMonitor {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <AgentMonitor error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <AgentMonitor loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});