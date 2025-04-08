import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:flutter/material.dart';

part 'app_dashboard.freezed.dart';

@freezed
class AppWidget with _$AppWidget {
  const factory AppWidget({
    required String id,
    required String name,
    required String type,
    required String iconPath,
    @Default(1) int columnSpan,
    @Default(1) int rowSpan,
    @Default({}) Map<String, dynamic> configuration,
    @Default(false) bool isDraggable,
    @Default(false) bool isResizable,
    @Default(false) bool isStatic,
  }) = _AppWidget;

  factory AppWidget.health() => const AppWidget(
        id: 'health_stats',
        name: '健康数据',
        type: 'health_stats',
        iconPath: 'assets/icons/health_stats.png',
        columnSpan: 2,
        rowSpan: 2,
        configuration: {
          'showVitalSigns': true,
          'showActivityData': true,
          'showSleepData': true,
          'refreshInterval': 60,
        },
      );

  factory AppWidget.tcmConstitution() => const AppWidget(
        id: 'tcm_constitution',
        name: '体质报告',
        type: 'tcm_constitution',
        iconPath: 'assets/icons/tcm_constitution.png',
        columnSpan: 2,
        rowSpan: 1,
        configuration: {
          'showMainTypes': true,
          'showSecondaryTypes': false,
          'showTips': true,
        },
      );

  factory AppWidget.dailyRecommendation() => const AppWidget(
        id: 'daily_recommendation',
        name: '每日建议',
        type: 'daily_recommendation',
        iconPath: 'assets/icons/daily_recommendation.png',
        columnSpan: 2,
        rowSpan: 1,
        configuration: {
          'includeNutrition': true,
          'includeActivity': true,
          'includeMindfulness': true,
        },
      );

  factory AppWidget.points() => const AppWidget(
        id: 'points_summary',
        name: '积分概况',
        type: 'points_summary',
        iconPath: 'assets/icons/points_summary.png',
        columnSpan: 1,
        rowSpan: 1,
        configuration: {
          'showPoints': true,
          'showCoins': true,
          'showVouchers': true,
        },
      );

  factory AppWidget.subscription() => const AppWidget(
        id: 'subscription_status',
        name: '订阅状态',
        type: 'subscription_status',
        iconPath: 'assets/icons/subscription_status.png',
        columnSpan: 1,
        rowSpan: 1,
        configuration: {
          'showExpiryDate': true,
          'showBenefits': true,
        },
      );

  factory AppWidget.recentActivity() => const AppWidget(
        id: 'recent_activity',
        name: '最近活动',
        type: 'recent_activity',
        iconPath: 'assets/icons/recent_activity.png',
        columnSpan: 2,
        rowSpan: 1,
        configuration: {
          'activityCount': 5,
          'includeSystemActivity': true,
          'includeUserActivity': true,
        },
      );

  factory AppWidget.seasonal() => const AppWidget(
        id: 'seasonal_advice',
        name: '时令养生',
        type: 'seasonal_advice',
        iconPath: 'assets/icons/seasonal_advice.png',
        columnSpan: 2,
        rowSpan: 1,
        configuration: {
          'includeFood': true,
          'includeHerbs': true,
          'includeActivities': true,
          'useLocationData': true,
        },
      );
}

@freezed
class AppDashboard with _$AppDashboard {
  const factory AppDashboard({
    required String userId,
    required List<DashboardItem> items,
    @Default('grid') String layoutType,
    @Default(24) int maxAppsPerScreen,
    @Default(true) bool allowCustomization,
    DateTime? lastModified,
  }) = _AppDashboard;
}

@freezed
class DashboardItem with _$DashboardItem {
  const factory DashboardItem({
    required String id,
    required AppWidget widget,
    @Default(0) int row,
    @Default(0) int column,
    @Default(1) int columnSpan,
    @Default(1) int rowSpan,
    @Default({}) Map<String, dynamic> userConfiguration,
  }) = _DashboardItem;
}

@freezed
class AppCategory with _$AppCategory {
  const factory AppCategory({
    required String id,
    required String name,
    required String iconPath,
    required Color color,
    required List<AppWidget> widgets,
    String? description,
  }) = _AppCategory;

  factory AppCategory.health() => AppCategory(
        id: 'health',
        name: '健康',
        iconPath: 'assets/icons/categories/health.png',
        color: const Color(0xFF35BB78),
        widgets: [
          AppWidget.health(),
          AppWidget.tcmConstitution(),
          AppWidget.dailyRecommendation(),
        ],
        description: '健康数据监测与分析',
      );

  factory AppCategory.tcm() => AppCategory(
        id: 'tcm',
        name: '中医',
        iconPath: 'assets/icons/categories/tcm.png',
        color: const Color(0xFFFF6800),
        widgets: [
          AppWidget.tcmConstitution(),
          AppWidget.seasonal(),
        ],
        description: '中医体质与养生理念',
      );

  factory AppCategory.shopping() => AppCategory(
        id: 'shopping',
        name: '商城',
        iconPath: 'assets/icons/categories/shopping.png',
        color: const Color(0xFFB3570A),
        widgets: [],
        description: '健康养生好物购买',
      );

  factory AppCategory.community() => AppCategory(
        id: 'community',
        name: '社区',
        iconPath: 'assets/icons/categories/community.png',
        color: const Color(0xFF5D6BB3),
        widgets: [
          AppWidget.recentActivity(),
        ],
        description: '健康社区交流与分享',
      );
} 