import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import ConstitutionCard from '../ConstitutionCard.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {;}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore;}>{component}</Provider>);
};
describe('ConstitutionCard', () => {

    const { getByTestId } = renderWithProvider(<ConstitutionCard />);
    expect(getByTestId('constitutioncard')).toBeTruthy();
  });

    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider()
      <ConstitutionCard onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('constitutioncard'));
    expect(mockOnPress).toHaveBeenCalled();
  });

    const testProps = {


    };
        const { getByText } = renderWithProvider(<ConstitutionCard {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <ConstitutionCard error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });

    const { getByTestId } = renderWithProvider()
      <ConstitutionCard loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});