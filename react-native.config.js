module.exports = {
  dependencies: {
    'react-native-sqlite-storage': {
      platforms: {
        android: {
          sourceDir:
            '../node_modules/react-native-sqlite-storage/platforms/android',
          packageImportPath: 'import org.pgsqlite.SQLitePluginPackage;',
        },
        ios: null, // disable iOS platform, other platforms will still autolink if provided
      },
    },
    'react-native-mmkv': {
      platforms: {
        ios: null, // 暂时禁用以避免网络问题
        android: null,
      },
    },
  },
  assets: ['./src/assets/fonts/'],
};
