const { getDefaultConfig } = require('metro-config');

module.exports = (async () => {
  const {
    resolver: { sourceExts, assetExts },
    transformer,
    ...config
  } = await getDefaultConfig();

  return {
    ...config,
    transformer: {
      ...transformer,
      babelTransformerPath: require.resolve('react-native-svg-transformer'),
      minifierConfig: {
        mangle: {
          keep_fnames: true,
        },
        output: {
          ascii_only: true,
          quote_style: 3,
          wrap_iife: true,
        },
        sourceMap: {
          includeSources: false,
        },
        toplevel: false,
        warnings: false,
        ie8: false,
        keep_fnames: true,
      },
    },
    resolver: {
      ...config.resolver,
      assetExts: assetExts.filter(ext => ext !== 'svg'),
      sourceExts: [...sourceExts, 'svg'],
    },
    serializer: {
      ...config.serializer,
      customSerializer: require('metro-minify-terser'),
    },
  };
})();
