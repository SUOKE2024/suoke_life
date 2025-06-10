import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import KnowledgeSearchBar from '../KnowledgeSearchBar.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('KnowledgeSearchBar', () => {

    const { getByTestId } = renderWithProvider(<KnowledgeSearchBar />);
    expect(getByTestId('knowledgesearchbar')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <KnowledgeSearchBar onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('knowledgesearchbar'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<KnowledgeSearchBar {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <KnowledgeSearchBar error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <KnowledgeSearchBar loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});