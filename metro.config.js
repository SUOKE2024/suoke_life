const { getDefaultConfig, mergeConfig } = require("@react-native/metro-config");
const path = require("path");

const defaultConfig = getDefaultConfig(__dirname);

const config = {
  // 解析器配置
  resolver: {
    ...defaultConfig.resolver,
    // 添加字体文件和AI模型文件支持
    assetExts: [
      ...defaultConfig.resolver.assetExts,
      "ttf",
      "otf",
      "woff",
      "woff2",
      "eot",
      "onnx",
      "tflite",
      "bin",
      "pb"
    ],
    // 源文件扩展名
    sourceExts: [
      ...defaultConfig.resolver.sourceExts,
      "ts",
      "tsx"
    ],
    // 别名配置
    alias: {
      "@": path.resolve(__dirname, "src"),
      "@components": path.resolve(__dirname, "src/components"),
      "@screens": path.resolve(__dirname, "src/screens"),
      "@services": path.resolve(__dirname, "src/services"),
      "@hooks": path.resolve(__dirname, "src/hooks"),
      "@utils": path.resolve(__dirname, "src/utils"),
      "@types": path.resolve(__dirname, "src/types"),
      "@constants": path.resolve(__dirname, "src/constants"),
      "@store": path.resolve(__dirname, "src/store"),
      "@navigation": path.resolve(__dirname, "src/navigation"),
      "@contexts": path.resolve(__dirname, "src/contexts"),
      "@assets": path.resolve(__dirname, "src/assets"),
      "@ai": path.resolve(__dirname, "src/ai")
    }
  },

  // 转换器配置
  transformer: {
    ...defaultConfig.transformer,
    // 启用内联需要
    inlineRequires: true,
    // 支持新架构
    unstable_allowRequireContext: true,
    getTransformOptions: async () => ({
      transform: {
        experimentalImportSupport: false,
        inlineRequires: true,
      },
    }),
  },

  // 监视器配置
  watchFolders: [
    path.resolve(__dirname, "src")
  ],

  // 新架构支持
  server: {
    enhanceMiddleware: (middleware) => {
      return (req, res, next) => {
        // 添加对AI模型文件的MIME类型支持
        if (req.url.endsWith('.onnx')) {
          res.setHeader('Content-Type', 'application/octet-stream');
        } else if (req.url.endsWith('.tflite')) {
          res.setHeader('Content-Type', 'application/octet-stream');
        }
        return middleware(req, res, next);
      };
    },
  }
};

module.exports = mergeConfig(defaultConfig, config);
