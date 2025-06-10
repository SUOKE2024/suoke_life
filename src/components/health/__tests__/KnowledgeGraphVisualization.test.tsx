import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import KnowledgeGraphVisualization from '../KnowledgeGraphVisualization.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('KnowledgeGraphVisualization', () => {

    const { getByTestId } = renderWithProvider(<KnowledgeGraphVisualization />);
    expect(getByTestId('knowledgegraphvisualization')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <KnowledgeGraphVisualization onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('knowledgegraphvisualization'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<KnowledgeGraphVisualization {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <KnowledgeGraphVisualization error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <KnowledgeGraphVisualization loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});