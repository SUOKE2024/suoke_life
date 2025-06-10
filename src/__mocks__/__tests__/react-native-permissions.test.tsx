describe('React Native Permissions Mock', () => {
  it('should provide mock permission functions', () => {
    const mockPermissions = require('../react-native-permissions');

    expect(mockPermissions.PERMISSIONS).toBeDefined();
    expect(mockPermissions.RESULTS).toBeDefined();
    expect(mockPermissions.check).toBeDefined();
    expect(mockPermissions.request).toBeDefined();
    expect(mockPermissions.checkMultiple).toBeDefined();
    expect(mockPermissions.requestMultiple).toBeDefined();
  });
});
