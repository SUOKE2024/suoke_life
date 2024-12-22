class DouBaoConfig {
  static const String baseUrl = 'https://api.doubao.com';
  static const String apiKey = 'your_api_key_here';
  
  // 模型配置
  static const Map<String, String> models = {
    'xiaoai': '小艾',
    'laoke': '老克', 
    'xiaoke': '小克',
  };
  
  // 助手类型配置
  static const Map<String, String> assistants = {
    'xiaoai': 'assistant-xiaoai-v1',
    'laoke': 'assistant-laoke-v1',
    'xiaoke': 'assistant-xiaoke-v1',
  };

  // 系统提示语配置
  static const Map<String, String> systemPrompts = {
    'xiaoai': '你是一个生活管家，帮助用户解决日常生活问题。',
    'laoke': '你是一个知识顾问，帮助用户解答学习和工作中的问题。',
    'xiaoke': '你是一个商务助手，帮助用户处理商务相关事务。',
  };
  
  // 默认模型
  static const String defaultModel = 'xiaoai';
} 