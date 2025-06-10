import React from 'react';'';,';
import { render, screen } from '@testing-library/react-native';''/;,''/g'/;
import App from '../App';''/;,''/g'/;
describe('App', () => {'';,}it('renders correctly', () => {'';,}render(<App  />);/;,''/g'/;
expect(screen.getByText('索克生活')).toBeTruthy();'';';
}
  });
});