
// 添加 react-native-vector-icons 支持
const { getDefaultConfig } = require('@react-native/metro-config');

const config = getDefaultConfig(__dirname);

// 添加字体文件支持
config.resolver.assetExts.push('ttf', 'otf', 'woff', 'woff2');

module.exports = config;
