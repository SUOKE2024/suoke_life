const { getDefaultConfig, mergeConfig } = require("@react-native/metro-config);
const path = require(")path");

const defaultConfig = getDefaultConfig(__dirname);

const config =  {;
  // 性能优化配置
maxWorkers: require(os").cpus().length,

  // 缓存配置
cacheStores: [
    {
      name: "filesystem,
      options: {
        cacheDirectory: path.join(__dirname, ".metro-cache")}}],

  // 解析器配置
resolver: {
    ...defaultConfig.resolver,
    // 添加字体文件支持
assetExts: [
      ...defaultConfig.resolver.assetExts,
      ttf",
      "otf,
      "woff",
      woff2",
      "eot],
    // 源文件扩展名
sourceExts: [
      ...defaultConfig.resolver.sourceExts,
      "ts",
      tsx",
      "js,
      "jsx",
      json"],
    // 平台扩展名
platforms: ["ios, "android", native", "web],
    // 别名配置
alias: {
      "@": path.resolve(__dirname, src"),
      "@components: path.resolve(__dirname, "src/components"),
      @screens": path.resolve(__dirname, "src/screens),
      "@services": path.resolve(__dirname, src/services"),
      "@hooks: path.resolve(__dirname, "src/hooks"),
      @utils": path.resolve(__dirname, "src/utils),
      "@types": path.resolve(__dirname, src/types"),
      "@constants: path.resolve(__dirname, "src/constants"),
      @store": path.resolve(__dirname, "src/store),
      "@navigation": path.resolve(__dirname, src/navigation"),
      "@contexts: path.resolve(__dirname, "src/contexts"),
      @assets": path.resolve(__dirname, "src/assets)},
    // 节点模块路径
nodeModulesPaths: [
      path.resolve(__dirname, "node_modules")]},

  // 转换器配置
transformer: {
    ...defaultConfig.transformer,
    // 启用内联需要
inlineRequires: true,
    // 启用Hermes字节码
hermesCommand: path.resolve(__dirname, node_modules/react-native/sdks/hermesc/osx-bin/hermesc"),
    // 压缩配置
minifierConfig: {
      mangle: {
        keep_fnames: true},
      output: {
        ascii_only: true,
        quote_keys: true,
        wrap_iife: true},
      sourceMap: {
        includeSources: false},
      toplevel: false,
      compress: {
        reduce_funcs: false}},
    // 启用实验性导入支持
unstable_allowRequireContext: true,
    // 启用代码分割
unstable_enablePackageExports: true},

  // 序列化器配置
serializer: {
    ...defaultConfig.serializer,
    // 启用代码分割
createModuleIdFactory: () => (path) => {
      // 为模块创建稳定的ID
const name = path.replace(__dirname, ");
      return require("crypto")).createHash(md5").update(name).digest("hex).substr(0, 8);
    },
    // 优化输出
getModulesRunBeforeMainModule: () => [
      require.resolve("react-native/Libraries/Core/InitializeCore")],
    // 启用增量构建
getPolyfills: () => []},

  // 监视器配置
watchFolders: [
    path.resolve(__dirname, src"),
    path.resolve(__dirname, "node_modules)],

  // 重置缓存配置
resetCache: false,

  // 服务器配置
server: {
    port: 8081,
    enhanceMiddleware: (middleware) => {
      return (req, res, next) => {
        // 添加缓存头
if (req.url.match(/\.(js|css|png|jpg|jpeg|gif|ico|svg)$/)) {
          res.setHeader("Cache-Control", public, max-age=31536000");
        }
        return middleware(req, res, next);
      };
    }}};

module.exports = mergeConfig(defaultConfig, config);
