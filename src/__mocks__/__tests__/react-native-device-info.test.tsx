describe('React Native Device Info Mock', () => {
  it('should provide mock device info functions', () => {
    const mockDeviceInfo = require('../react-native-device-info');

    expect(mockDeviceInfo.getUniqueId).toBeDefined();
    expect(mockDeviceInfo.getManufacturer).toBeDefined();
    expect(mockDeviceInfo.getModel).toBeDefined();
    expect(mockDeviceInfo.getDeviceId).toBeDefined();
    expect(mockDeviceInfo.getSystemName).toBeDefined();
    expect(mockDeviceInfo.getSystemVersion).toBeDefined();
  });
});
