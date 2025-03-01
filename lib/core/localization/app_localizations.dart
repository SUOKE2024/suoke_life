import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';

/// 应用程序本地化
class AppLocalizations {
  final Locale locale;

  AppLocalizations(this.locale);

  /// 支持的语言区域
  static const List<Locale> supportedLocales = [
    Locale('zh', 'CN'), // 中文(中国)
    Locale('en', 'US'), // 英文(美国)
  ];

  /// 本地化委托
  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// 获取当前区域的本地化实例
  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }

  /// 本地化字符串映射
  static final Map<String, Map<String, String>> _localizedValues = {
    'zh_CN': {
      'appName': '索克生活',
      'welcome': '欢迎',
      'loading': '正在加载...',
      'ready': '准备就绪',
      'loadFailed': '加载失败，请稍后重试',
      'retry': '重试',
      'login': '登录',
      'logout': '退出登录',
      'home': '首页',
      'suoke': 'SUOKE',
      'explore': '探索',
      'life': 'LIFE',
      'profile': '我的',
      'createAccount': '创建账号',
      'phoneNumber': '手机号码',
      'verificationCode': '验证码',
      'sendCode': '发送验证码',
      'next': '下一步',
      'nickname': '昵称',
      'gender': '性别',
      'male': '男',
      'female': '女',
      'birthday': '生日',
      'complete': '完成',
      'skip': '跳过',
      'health': '健康',
      'knowledge': '知识',
      'service': '服务',
      'settings': '设置',
      'sleepAnalysis': '睡眠分析',
      'exerciseTracking': '运动追踪',
      'nutritionBalance': '营养均衡',
      'mentalWellbeing': '心理健康',
      'tcmDiagnosis': '中医诊断',
      'healthReport': '健康报告',
      'userAgreement': '用户协议',
      'privacyPolicy': '隐私政策',
      'tcmKnowledge': '中医知识',
      'nutritionKnowledge': '营养知识',
      'exerciseKnowledge': '运动知识',
    },
    'en_US': {
      'appName': 'Suoke Life',
      'welcome': 'Welcome',
      'loading': 'Loading...',
      'ready': 'Ready',
      'loadFailed': 'Load failed, please try again later',
      'retry': 'Retry',
      'login': 'Login',
      'logout': 'Logout',
      'home': 'Home',
      'suoke': 'SUOKE',
      'explore': 'Explore',
      'life': 'LIFE',
      'profile': 'Profile',
      'createAccount': 'Create Account',
      'phoneNumber': 'Phone Number',
      'verificationCode': 'Verification Code',
      'sendCode': 'Send Code',
      'next': 'Next',
      'nickname': 'Nickname',
      'gender': 'Gender',
      'male': 'Male',
      'female': 'Female',
      'birthday': 'Birthday',
      'complete': 'Complete',
      'skip': 'Skip',
      'health': 'Health',
      'knowledge': 'Knowledge',
      'service': 'Service',
      'settings': 'Settings',
      'sleepAnalysis': 'Sleep Analysis',
      'exerciseTracking': 'Exercise Tracking',
      'nutritionBalance': 'Nutrition Balance',
      'mentalWellbeing': 'Mental Wellbeing',
      'tcmDiagnosis': 'TCM Diagnosis',
      'healthReport': 'Health Report',
      'userAgreement': 'User Agreement',
      'privacyPolicy': 'Privacy Policy',
      'tcmKnowledge': 'TCM Knowledge',
      'nutritionKnowledge': 'Nutrition Knowledge',
      'exerciseKnowledge': 'Exercise Knowledge',
    },
  };

  /// 获取本地化字符串
  String translate(String key) {
    final localeKey = '${locale.languageCode}_${locale.countryCode}';
    return _localizedValues[localeKey]?[key] ?? key;
  }

  /// 应用名称
  String get appName => translate('appName');

  /// 欢迎
  String get welcome => translate('welcome');

  /// 加载中
  String get loading => translate('loading');

  /// 准备就绪
  String get ready => translate('ready');

  /// 加载失败
  String get loadFailed => translate('loadFailed');

  /// 重试
  String get retry => translate('retry');

  /// 登录
  String get login => translate('login');

  /// 退出登录
  String get logout => translate('logout');

  /// 首页
  String get home => translate('home');

  /// SUOKE
  String get suoke => translate('suoke');

  /// 探索
  String get explore => translate('explore');

  /// LIFE
  String get life => translate('life');

  /// 我的
  String get profile => translate('profile');

  /// 创建账号
  String get createAccount => translate('createAccount');

  /// 手机号码
  String get phoneNumber => translate('phoneNumber');

  /// 验证码
  String get verificationCode => translate('verificationCode');

  /// 发送验证码
  String get sendCode => translate('sendCode');

  /// 下一步
  String get next => translate('next');

  /// 昵称
  String get nickname => translate('nickname');

  /// 性别
  String get gender => translate('gender');

  /// 男
  String get male => translate('male');

  /// 女
  String get female => translate('female');

  /// 生日
  String get birthday => translate('birthday');

  /// 完成
  String get complete => translate('complete');

  /// 跳过
  String get skip => translate('skip');

  /// 健康
  String get health => translate('health');

  /// 知识
  String get knowledge => translate('knowledge');

  /// 服务
  String get service => translate('service');

  /// 设置
  String get settings => translate('settings');

  /// 睡眠分析
  String get sleepAnalysis => translate('sleepAnalysis');

  /// 运动追踪
  String get exerciseTracking => translate('exerciseTracking');

  /// 营养均衡
  String get nutritionBalance => translate('nutritionBalance');

  /// 心理健康
  String get mentalWellbeing => translate('mentalWellbeing');

  /// 中医诊断
  String get tcmDiagnosis => translate('tcmDiagnosis');

  /// 健康报告
  String get healthReport => translate('healthReport');

  /// 用户协议
  String get userAgreement => translate('userAgreement');

  /// 隐私政策
  String get privacyPolicy => translate('privacyPolicy');

  /// 中医知识
  String get tcmKnowledge => translate('tcmKnowledge');

  /// 营养知识
  String get nutritionKnowledge => translate('nutritionKnowledge');

  /// 运动知识
  String get exerciseKnowledge => translate('exerciseKnowledge');
}

/// 本地化委托
class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    return ['zh', 'en'].contains(locale.languageCode);
  }

  @override
  Future<AppLocalizations> load(Locale locale) async {
    return AppLocalizations(locale);
  }

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

/// 便捷的本地化设置
class AppLocalizationsSetup {
  static const Locale defaultLocale = Locale('zh', 'CN');

  /// 获取支持的本地化
  static Iterable<Locale> supportedLocales() =>
      AppLocalizations.supportedLocales;

  /// 获取本地化委托
  static Iterable<LocalizationsDelegate<dynamic>> localizationsDelegates() {
    return [
      AppLocalizations.delegate,
      GlobalMaterialLocalizations.delegate,
      GlobalWidgetsLocalizations.delegate,
      GlobalCupertinoLocalizations.delegate,
    ];
  }

  /// 本地化解析回调
  static Locale? localeResolutionCallback(
    Locale? locale,
    Iterable<Locale> supportedLocales,
  ) {
    if (locale == null) {
      return defaultLocale;
    }

    // 检查是否支持完整的locale（语言+国家）
    for (final supportedLocale in supportedLocales) {
      if (supportedLocale.languageCode == locale.languageCode &&
          supportedLocale.countryCode == locale.countryCode) {
        return supportedLocale;
      }
    }

    // 如果找不到完全匹配，则检查语言匹配
    for (final supportedLocale in supportedLocales) {
      if (supportedLocale.languageCode == locale.languageCode) {
        return supportedLocale;
      }
    }

    // 如果找不到任何匹配，则返回默认locale
    return defaultLocale;
  }
}
