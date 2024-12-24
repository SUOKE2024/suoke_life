part of 'app_pages.dart';

abstract class Routes {
  // 主页面
  static const HOME = '/';
  static const SUOKE = '/suoke';
  static const EXPLORE = '/explore'; 
  static const LIFE = '/life';
  static const PROFILE = '/profile';

  // 设置相关
  static const SETTINGS = '/settings';
  static const DEVICE_SETTINGS = '/settings/device';
  static const PRIVACY_SETTINGS = '/settings/privacy';
  static const NOTIFICATION_SETTINGS = '/settings/notification';
  static const LANGUAGE_SETTINGS = '/settings/language';
  static const AI_SETTINGS = '/settings/ai';
  static const VOICE_SETTINGS = '/settings/voice';

  // 系统管理
  static const ADMIN = '/admin';
  static const ADMIN_EXPERTS = '/admin/experts';  // 专家审核
  static const ADMIN_SERVICES = '/admin/services'; // 服务审核
  static const ADMIN_PRODUCTS = '/admin/products'; // 产品审核
  static const ADMIN_AI = '/admin/ai';  // AI模型管理
  static const ADMIN_API = '/admin/api'; // 第三方API管理

  // 功能页面
  static const HEALTH_SURVEY = '/health/survey';
  static const LIFE_RECORD = '/life/record';
  static const FEEDBACK = '/feedback';
} 