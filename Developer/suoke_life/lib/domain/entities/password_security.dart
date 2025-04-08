/// 密码安全性级别
enum PasswordSecurityLevel {
  /// 低安全性
  low,
  
  /// 中等安全性
  medium,
  
  /// 高安全性
  high,
  
  /// 非常高的安全性
  veryHigh,
}

/// 密码安全性检查结果
class PasswordSecurityResult {
  /// 安全性级别
  final PasswordSecurityLevel level;
  
  /// 安全性评分 (0-100)
  final int score;
  
  /// 密码是否已泄露
  final bool isCompromised;
  
  /// 建议和提示
  final List<String> suggestions;
  
  /// 密码强度信息
  final Map<String, bool> strengthInfo;
  
  PasswordSecurityResult({
    required this.level,
    required this.score,
    this.isCompromised = false,
    this.suggestions = const [],
    this.strengthInfo = const {},
  });
  
  /// 创建低安全性结果
  factory PasswordSecurityResult.low({
    int score = 20,
    bool isCompromised = false,
    List<String> suggestions = const ['增加密码长度', '添加大小写字母', '添加数字和特殊字符'],
  }) {
    return PasswordSecurityResult(
      level: PasswordSecurityLevel.low,
      score: score,
      isCompromised: isCompromised,
      suggestions: suggestions,
      strengthInfo: {
        '长度': false,
        '复杂性': false,
        '唯一性': !isCompromised,
      },
    );
  }
  
  /// 创建中等安全性结果
  factory PasswordSecurityResult.medium({
    int score = 50,
    bool isCompromised = false,
    List<String> suggestions = const ['添加更多特殊字符', '避免使用连续的数字或字母'],
  }) {
    return PasswordSecurityResult(
      level: PasswordSecurityLevel.medium,
      score: score,
      isCompromised: isCompromised,
      suggestions: suggestions,
      strengthInfo: {
        '长度': true,
        '复杂性': false,
        '唯一性': !isCompromised,
      },
    );
  }
  
  /// 创建高安全性结果
  factory PasswordSecurityResult.high({
    int score = 80,
    bool isCompromised = false,
    List<String> suggestions = const ['定期更换密码', '不要在多个网站使用相同密码'],
  }) {
    return PasswordSecurityResult(
      level: PasswordSecurityLevel.high,
      score: score,
      isCompromised: isCompromised,
      suggestions: suggestions,
      strengthInfo: {
        '长度': true,
        '复杂性': true,
        '唯一性': !isCompromised,
      },
    );
  }
  
  /// 创建非常高安全性结果
  factory PasswordSecurityResult.veryHigh({
    int score = 100,
    bool isCompromised = false,
  }) {
    return PasswordSecurityResult(
      level: PasswordSecurityLevel.veryHigh,
      score: score,
      isCompromised: isCompromised,
      suggestions: const ['继续保持良好的密码习惯'],
      strengthInfo: {
        '长度': true,
        '复杂性': true,
        '唯一性': !isCompromised,
      },
    );
  }
} 