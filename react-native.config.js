module.exports = {
  dependencies: {
    // 完全禁用 sqlite-storage 的自动链接，避免配置警告
    "react-native-sqlite-storage": {
      platforms: {
        android: null,
        ios: null
      }
    },
    "react-native-mmkv": {
      platforms: {
        ios: null, // 暂时禁用以避免网络问题
        android: null
      }
    }
  },
  assets: ["./src/assets/fonts/"]
};
