class AssetConstants {
  // 头像路径
  static const String defaultAvatar = 'assets/images/default_avatar.png';
  static const String xiaoaiAvatar = 'assets/images/xiaoai_avatar.png';
  static const String laokeAvatar = 'assets/images/laoke_avatar.png';
  static const String xiaokeAvatar = 'assets/images/xiaoke_avatar.png';

  // 获取模型头像
  static String getModelAvatar(String model) {
    switch (model) {
      case 'xiaoai':
        return xiaoaiAvatar;
      case 'laoke':
        return laokeAvatar;
      case 'xiaoke':
        return xiaokeAvatar;
      default:
        return defaultAvatar;
    }
  }
} 