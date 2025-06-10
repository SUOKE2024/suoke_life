import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import ChallengeModal from '../ChallengeModal.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('ChallengeModal', () => {

    const { getByTestId } = renderWithProvider(<ChallengeModal />);
    expect(getByTestId('challengemodal')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <ChallengeModal onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('challengemodal'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<ChallengeModal {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <ChallengeModal error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <ChallengeModal loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});