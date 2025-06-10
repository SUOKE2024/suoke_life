import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import KnowledgeNodeModal from '../KnowledgeNodeModal.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('KnowledgeNodeModal', () => {

    const { getByTestId } = renderWithProvider(<KnowledgeNodeModal />);
    expect(getByTestId('knowledgenodemodal')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <KnowledgeNodeModal onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('knowledgenodemodal'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<KnowledgeNodeModal {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <KnowledgeNodeModal error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <KnowledgeNodeModal loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});