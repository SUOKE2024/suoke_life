const React = require('react');

const MockIcon = (props) => {
  return React.createElement('Text', props, props.name || 'icon');
};

MockIcon.getImageSource = jest.fn(() => Promise.resolve({ uri: 'mock-icon' }));
MockIcon.getImageSourceSync = jest.fn(() => ({ uri: 'mock-icon' }));
MockIcon.loadFont = jest.fn(() => Promise.resolve());

module.exports = MockIcon;
