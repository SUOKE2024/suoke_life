class DouBaoConfig {
  static const String baseUrl = 'https://ark.cn-beijing.volces.com/api/v3';
  static const String defaultModel = 'xiaoai';

  static const Map<String, String> models = {
    'xiaoai': '小艾 (128K)',
    'laoke': '老克 (Embedding)',
    'xiaoke': '小克 (32K)',
  };

  static const Map<String, String> systemPrompts = {
    'xiaoai': '你是小艾，一个生活管家助手。',
    'laoke': '你是老克，一个知识顾问助手。',
    'xiaoke': '你是小克，一个商务助手。',
  };

  static const Map<String, String> modelEndpoints = {
    'xiaoai': 'ep-20241212093835-bl92q',  // 128K
    'laoke': 'ep-20241207124339-rh46z',   // Embedding
    'xiaoke': 'ep-20241024122905-r8xsl',  // 32K
  };
} 