import 'package:equatable/equatable.dart';

/// 用户偏好设置实体类
class UserPreferences extends Equatable {
  /// 用户ID
  final String userId;
  
  /// 主题模式：light, dark, system
  final String themeMode;
  
  /// 语言设置
  final String language;
  
  /// 是否启用通知
  final bool notificationsEnabled;
  
  /// 是否同意数据收集
  final bool dataCollectionConsent;
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 更新时间
  final DateTime updatedAt;

  /// 构造函数
  const UserPreferences({
    required this.userId,
    this.themeMode = 'system',
    this.language = 'zh',
    this.notificationsEnabled = true,
    this.dataCollectionConsent = false,
    required this.createdAt,
    required this.updatedAt,
  });

  @override
  List<Object?> get props => [
        userId, 
        themeMode, 
        language, 
        notificationsEnabled, 
        dataCollectionConsent,
        createdAt,
        updatedAt,
      ];
  
  /// 创建具有更新属性的UserPreferences副本
  UserPreferences copyWith({
    String? userId,
    String? themeMode,
    String? language,
    bool? notificationsEnabled,
    bool? dataCollectionConsent,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return UserPreferences(
      userId: userId ?? this.userId,
      themeMode: themeMode ?? this.themeMode,
      language: language ?? this.language,
      notificationsEnabled: notificationsEnabled ?? this.notificationsEnabled,
      dataCollectionConsent: dataCollectionConsent ?? this.dataCollectionConsent,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is UserPreferences &&
          runtimeType == other.runtimeType &&
          userId == other.userId;

  @override
  int get hashCode => userId.hashCode;

  @override
  String toString() {
    return 'UserPreferences{userId: $userId, themeMode: $themeMode, language: $language}';
  }
} 