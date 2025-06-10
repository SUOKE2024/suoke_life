describe('React Native Vector Icons Mock', () => {
  it('should provide mock icon component', () => {
    const MockIcon = require('../react-native-vector-icons');

    expect(MockIcon).toBeDefined();
    expect(MockIcon.getImageSource).toBeDefined();
    expect(MockIcon.getImageSourceSync).toBeDefined();
    expect(MockIcon.loadFont).toBeDefined();
  });
});
