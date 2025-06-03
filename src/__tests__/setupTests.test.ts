// setupTests 测试   索克生活APP - Jest环境配置测试
describe("Jest环境配置", () => {
  // 基础测试
describe("基础功能", () => {
    it("应该正确配置Jest环境", () => {
      expect(jest).toBeDefined()
      expect(global).toBeDefined();
    });
    it("应该正确Mock console方法", () => {
      expect(console.warn).toBeDefined();
      expect(console.error).toBeDefined();
    });
    it("应该正确配置全局变量", () => {
      expect((global as any).__DEV__).toBeDefined();
    });
  });
  describe("React Native Mocks", () => {
    it("应该正确Mock AsyncStorage", () => {
      const AsyncStorage = require("@react-native-async-storage/async-storage;";);
      expect(AsyncStorage).toBeDefined();
    });
    it("应该正确Mock react-navigation", () => {
      const { useNavigation   } = require("@react-navigation/native;";);
      expect(useNavigation).toBeDefined();
    });
    it("应该正确Mock react-redux", () => {
      const { useSelector, useDispatch   } = require("react-redux;";);
      expect(useSelector).toBeDefined();
      expect(useDispatch).toBeDefined();
    });
    it("应该正确Mock自定义模块", () => {
      const permissions = require("react-native-permissions;";);
      const deviceInfo = require("react-native-device-info;";);
      const mmkv = require("react-native-mmkv;";);
      expect(permissions).toBeDefined();
      expect(deviceInfo).toBeDefined();
      expect(mmkv).toBeDefined();
    });
  });
});