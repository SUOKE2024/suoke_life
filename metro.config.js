const { getDefaultConfig, mergeConfig } = require('@react-native/metro-config');

/**
 * Metro配置文件
 * @type {import('metro-config').MetroConfig}
 */
const config = {
  transformer: {
    getTransformOptions: async () => ({
      transform: {
        experimentalImportSupport: false,
        inlineRequires: true,
      },
    }),
  },
  resolver: {
    alias: {
      '@': './src',
      '@components': './src/components',
      '@screens': './src/screens',
      '@navigation': './src/navigation',
      '@services': './src/services',
      '@store': './src/store',
      '@types': './src/types',
      '@constants': './src/constants',
      '@contexts': './src/contexts',
      '@i18n': './src/i18n',
      '@assets': './src/assets',
    },
    // 添加对.json文件的支持
    assetExts: ['bin', 'txt', 'jpg', 'png', 'json', 'mp4', 'mp3', 'wav'],
    sourceExts: ['js', 'json', 'ts', 'tsx', 'jsx'],
  },
};

module.exports = mergeConfig(getDefaultConfig(__dirname), config); 