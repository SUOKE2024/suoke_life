const fs = require('fs');
const path = require('path');
// 修复计数器
let fixCount = 0;
let fileCount = 0;
// 特定文件修复规则
const specificFixes = {
  'src/App.tsx': (content) => {
    return content
      .replace(/import.*from\s+['"`][^'"`]*$/gm, (match) => match + ")
      .replace(/(['"`])([^'"`\n]*?)$/gm, '$1$2$1')
      .replace(/export\s+default\s+([^;]+)$/gm, 'export default $1;');
  },
  'src/__mocks__/react-native-device-info.js': (content) => {
    return `module.exports = {
  getUniqueId: () => 'test-device-id',
  getSystemName: () => 'iOS',
  getSystemVersion: () => '14.0',
  getModel: () => 'iPhone',
  getBrand: () => 'Apple',
  getDeviceId: () => 'test-device',
  getVersion: () => '1.0.0',
  getBuildNumber: () => '1',
  getBundleId: () => 'life.suoke.app',
  getApplicationName: () => 'Suoke Life',
  isEmulator: () => Promise.resolve(false),
  hasNotch: () => false,
  hasDynamicIsland: () => false,
  getDeviceType: () => 'Handset',
  isTablet: () => false,
  isPinOrFingerprintSet: () => Promise.resolve(true),
  supportedAbis: () => Promise.resolve(['arm64-v8a']),
  hasSystemFeature: () => Promise.resolve(true),
  getSystemAvailableFeatures: () => Promise.resolve([]),
  getPowerState: () => Promise.resolve({ batteryLevel: 0.8 }),
  getUsedMemory: () => Promise.resolve(1024),
  getTotalMemory: () => Promise.resolve(4096),
  getMaxMemory: () => Promise.resolve(4096),
  getTotalDiskCapacity: () => Promise.resolve(64000),
  getFreeDiskStorage: () => Promise.resolve(32000),
  getBatteryLevel: () => Promise.resolve(0.8),
  isLocationEnabled: () => Promise.resolve(true),
  isHeadphonesConnected: () => Promise.resolve(false),
  getAvailableLocationProviders: () => Promise.resolve(['gps', 'network']),
  getInstallReferrer: () => Promise.resolve(''),
  getInstallerPackageName: () => Promise.resolve(''),
  getFirstInstallTime: () => Promise.resolve(Date.now()),
  getLastUpdateTime: () => Promise.resolve(Date.now()),
  getSerialNumber: () => Promise.resolve(''),
  getAndroidId: () => Promise.resolve(''),
  getIpAddress: () => Promise.resolve('192.168.1.1'),
  getMacAddress: () => Promise.resolve('00:00:00:00:00:00'),
  getCarrier: () => Promise.resolve(''),
  getApiLevel: () => Promise.resolve(30),
  getBootloader: () => Promise.resolve(''),
  getDevice: () => Promise.resolve(''),
  getDisplay: () => Promise.resolve(''),
  getFingerprint: () => Promise.resolve(''),
  getHardware: () => Promise.resolve(''),
  getHost: () => Promise.resolve(''),
  getProduct: () => Promise.resolve(''),
  getTags: () => Promise.resolve(''),
  getType: () => Promise.resolve(''),
  getBaseOs: () => Promise.resolve(''),
  getPreviewSdkInt: () => Promise.resolve(0),
  getSecurityPatch: () => Promise.resolve(''),
  getCodename: () => Promise.resolve(''),
  getIncremental: () => Promise.resolve(''),
  isAirplaneMode: () => Promise.resolve(false),
  isBatteryCharging: () => Promise.resolve(true),
  isLandscape: () => Promise.resolve(false),
  isMouseConnected: () => Promise.resolve(false),
  isKeyboardConnected: () => Promise.resolve(false),
  isCameraPresent: () => Promise.resolve(true),
  getDeviceName: () => Promise.resolve('Test Device'),
  getUserAgent: () => Promise.resolve('Test User Agent'),
  getFontScale: () => Promise.resolve(1.0),
  hasGms: () => Promise.resolve(true),
  hasHms: () => Promise.resolve(false),
  syncUniqueId: () => Promise.resolve('test-sync-id'),
};`;
  },
  'src/__mocks__/react-native-permissions.js': (content) => {
    return `const PERMISSIONS = {
  IOS: {,
  CAMERA: 'ios.permission.CAMERA',
    MICROPHONE: 'ios.permission.MICROPHONE',
    PHOTO_LIBRARY: 'ios.permission.PHOTO_LIBRARY',
    LOCATION_WHEN_IN_USE: 'ios.permission.LOCATION_WHEN_IN_USE',
    LOCATION_ALWAYS: 'ios.permission.LOCATION_ALWAYS',
    CONTACTS: 'ios.permission.CONTACTS',
    CALENDARS: 'ios.permission.CALENDARS',
    REMINDERS: 'ios.permission.REMINDERS',
    BLUETOOTH_PERIPHERAL: 'ios.permission.BLUETOOTH_PERIPHERAL',
    SPEECH_RECOGNITION: 'ios.permission.SPEECH_RECOGNITION',
    NOTIFICATIONS: 'ios.permission.NOTIFICATIONS',
    APP_TRACKING_TRANSPARENCY: 'ios.permission.APP_TRACKING_TRANSPARENCY',
  },
  ANDROID: {,
  CAMERA: 'android.permission.CAMERA',
    RECORD_AUDIO: 'android.permission.RECORD_AUDIO',
    READ_EXTERNAL_STORAGE: 'android.permission.READ_EXTERNAL_STORAGE',
    WRITE_EXTERNAL_STORAGE: 'android.permission.WRITE_EXTERNAL_STORAGE',
    ACCESS_FINE_LOCATION: 'android.permission.ACCESS_FINE_LOCATION',
    ACCESS_COARSE_LOCATION: 'android.permission.ACCESS_COARSE_LOCATION',
    READ_CONTACTS: 'android.permission.READ_CONTACTS',
    WRITE_CONTACTS: 'android.permission.WRITE_CONTACTS',
    READ_CALENDAR: 'android.permission.READ_CALENDAR',
    WRITE_CALENDAR: 'android.permission.WRITE_CALENDAR',
    BLUETOOTH_SCAN: 'android.permission.BLUETOOTH_SCAN',
    BLUETOOTH_CONNECT: 'android.permission.BLUETOOTH_CONNECT',
    BLUETOOTH_ADVERTISE: 'android.permission.BLUETOOTH_ADVERTISE',
    POST_NOTIFICATIONS: 'android.permission.POST_NOTIFICATIONS',
  },
};
const RESULTS = {
  UNAVAILABLE: 'unavailable',
  DENIED: 'denied',
  LIMITED: 'limited',
  GRANTED: 'granted',
  BLOCKED: 'blocked',
};
const check = jest.fn(() => Promise.resolve(RESULTS.GRANTED));
const request = jest.fn(() => Promise.resolve(RESULTS.GRANTED));
const requestMultiple = jest.fn(() => Promise.resolve({}));
const checkMultiple = jest.fn(() => Promise.resolve({}));
const openSettings = jest.fn(() => Promise.resolve());
const checkNotifications = jest.fn(() => Promise.resolve({ status: RESULTS.GRANTED, settings: {} }));
const requestNotifications = jest.fn(() => Promise.resolve({ status: RESULTS.GRANTED, settings: {} }));
module.exports = {
  PERMISSIONS,
  RESULTS,
  check,
  request,
  requestMultiple,
  checkMultiple,
  openSettings,
  checkNotifications,
  requestNotifications,
};`;
  },
  'src/__mocks__/react-native-vector-icons.js': (content) => {
    return `import React from 'react';
import { Text } from 'react-native';
const createIconSet = () => {
  return function Icon(props) {
    return React.createElement(Text, {
      ...props,
      testID: props.testID || 'icon',
    }, props.name || 'icon');
  };
};
const createIconSetFromFontello = createIconSet;
const createIconSetFromIcoMoon = createIconSet;
export default createIconSet();
export {;
  createIconSet,
  createIconSetFromFontello,
  createIconSetFromIcoMoon,
};
// 导出常用图标库
export const AntDesign = createIconSet();
export const Entypo = createIconSet();
export const EvilIcons = createIconSet();
export const Feather = createIconSet();
export const FontAwesome = createIconSet();
export const FontAwesome5 = createIconSet();
export const Fontisto = createIconSet();
export const Foundation = createIconSet();
export const Ionicons = createIconSet();
export const MaterialIcons = createIconSet();
export const MaterialCommunityIcons = createIconSet();
export const Octicons = createIconSet();
export const Zocial = createIconSet();
export const SimpleLineIcons = createIconSet();`;
  }
};
// 通用修复模式
const generalFixes = [
  // 修复未终止的字符串字面量
  {
    pattern: /(['"`])([^'"`\n]*?)$/gm,
    replacement: '$1$2$1',
    description: '修复未终止的字符串字面量'
  },
  // 修复缺少分号的导入语句
  {
    pattern: /import\s+([^;]+)$/gm,
    replacement: 'import $1;',
    description: '修复导入语句缺少分号'
  },
  // 修复缺少分号的导出语句
  {
    pattern: /export\s+([^;]+)$/gm,
    replacement: 'export $1;',
    description: '修复导出语句缺少分号'
  },
  // 修复测试文件的导入
  {
    pattern: /import.*from\s+['"`]@testing-library\/react-native['"`]$/gm,
    replacement: "import { render, fireEvent } from "@testing-library/react-native,"
    description: '修复测试库导入'
  },
  // 修复React导入
  {
    pattern: /import\s+React\s+from\s+['"`]react['"`]$/gm,
    replacement: "import React from "react,"
    description: '修复React导入'
  },
  // 修复未闭合的JSX标签
  {
    pattern: /<(\w+)([^>]*?)$/gm,
    replacement: '<$1$2 />',
    description: '修复JSX标签'
  }
];
function fixFile(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    const originalContent = content;
    let localFixCount = 0;
    // 获取相对路径用于匹配特定修复规则
    const relativePath = path.relative(process.cwd(), filePath);
    // 应用特定文件修复规则
    if (specificFixes[relativePath]) {
      content = specificFixes[relativePath](content);
      localFixCount += 10; // 估算修复数
    }
    // 应用通用修复模式
    generalFixes.forEach(({ pattern, replacement, description }) => {
      const matches = content.match(pattern);
      if (matches) {
        content = content.replace(pattern, replacement);
        localFixCount += matches.length;
      }
    });
    // 如果内容有变化，写回文件
    if (content !== originalContent) {
      fs.writeFileSync(filePath, content, 'utf8');
      fileCount++;
      fixCount += localFixCount;
      console.log(`✅ 修复文件: ${relativePath} (${localFixCount} 个修复)`);
    }
  } catch (error) {
    console.error(`❌ 修复文件失败: ${filePath}`, error.message);
  }
}
// 需要修复的特定文件列表
const filesToFix = [
  'src/App.tsx',
  'src/__mocks__/__tests__/react-native-device-info.test.tsx',
  'src/__mocks__/__tests__/react-native-mmkv.test.tsx',
  'src/__mocks__/__tests__/react-native-permissions.test.tsx',
  'src/__mocks__/__tests__/react-native-vector-icons.test.tsx',
  'src/__mocks__/react-native-device-info.js',
  'src/__mocks__/react-native-permissions.js',
  'src/__mocks__/react-native-vector-icons.js',
  'src/__tests__/AgentEmotionFeedback.test.tsx',
  'src/__tests__/App.test.tsx',
  'src/__tests__/agent_collaboration/agent_collaboration.integration.test.ts',
  'src/__tests__/agents/AgentCoordinator.test.tsx',
  'src/__tests__/components/FiveDiagnosisAgentIntegrationScreen.test.tsx',
  'src/__tests__/components/HomeScreen.test.tsx',
  'src/__tests__/e2e/agent-collaboration.test.tsx'
];
console.log('🚀 开始最终关键修复...');
console.log('='.repeat(50));
// 修复特定文件
filesToFix.forEach(file => {
  const fullPath = path.join(process.cwd(), file);
  if (fs.existsSync(fullPath)) {
    fixFile(fullPath);
  } else {
    console.log(`⚠️  文件不存在: ${file}`);
  }
});
console.log('='.repeat(50));
console.log(`✅ 最终关键修复完成!`);
console.log(`📊 统计信息:`);
console.log(`   - 修复文件数: ${fileCount}`);
console.log(`   - 总修复数: ${fixCount}`);
console.log(`   - 平均每文件修复数: ${fileCount > 0 ? (fixCount / fileCount).toFixed(1) : 0}`); 
