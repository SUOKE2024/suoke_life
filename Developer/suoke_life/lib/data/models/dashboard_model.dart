import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:json_annotation/json_annotation.dart';
import '../../domain/entities/app_dashboard.dart';

part 'dashboard_model.freezed.dart';
part 'dashboard_model.g.dart';

@freezed
class AppDashboardModel with _$AppDashboardModel {
  const factory AppDashboardModel({
    required String id,
    required String userId,
    required List<DashboardItemModel> items,
    required int rows,
    required int columns,
    required DateTime updatedAt,
    String? name,
    String? description,
    @Default(false) bool isDefault,
  }) = _AppDashboardModel;

  factory AppDashboardModel.fromJson(Map<String, dynamic> json) =>
      _$AppDashboardModelFromJson(json);

  // 从领域实体转换
  factory AppDashboardModel.fromEntity(AppDashboard entity) {
    return AppDashboardModel(
      id: entity.id,
      userId: entity.userId,
      items: entity.items.map((item) => DashboardItemModel.fromEntity(item)).toList(),
      rows: entity.rows,
      columns: entity.columns,
      updatedAt: entity.updatedAt,
      name: entity.name,
      description: entity.description,
      isDefault: entity.isDefault,
    );
  }
}

extension AppDashboardModelX on AppDashboardModel {
  // 转换为领域实体
  AppDashboard toEntity() {
    return AppDashboard(
      id: id,
      userId: userId,
      items: items.map((item) => item.toEntity()).toList(),
      rows: rows,
      columns: columns,
      updatedAt: updatedAt,
      name: name,
      description: description,
      isDefault: isDefault,
    );
  }
}

@freezed
class DashboardItemModel with _$DashboardItemModel {
  const factory DashboardItemModel({
    required String id,
    required AppWidgetModel widget,
    required int row,
    required int column,
    @Default(1) int rowSpan,
    @Default(1) int columnSpan,
    String? customTitle,
    Map<String, dynamic>? settings,
    @Default(false) bool isStatic,
  }) = _DashboardItemModel;

  factory DashboardItemModel.fromJson(Map<String, dynamic> json) =>
      _$DashboardItemModelFromJson(json);

  // 从领域实体转换
  factory DashboardItemModel.fromEntity(DashboardItem entity) {
    return DashboardItemModel(
      id: entity.id,
      widget: AppWidgetModel.fromEntity(entity.widget),
      row: entity.row,
      column: entity.column,
      rowSpan: entity.rowSpan,
      columnSpan: entity.columnSpan,
      customTitle: entity.customTitle,
      settings: entity.settings,
      isStatic: entity.isStatic,
    );
  }
}

extension DashboardItemModelX on DashboardItemModel {
  // 转换为领域实体
  DashboardItem toEntity() {
    return DashboardItem(
      id: id,
      widget: widget.toEntity(),
      row: row,
      column: column,
      rowSpan: rowSpan,
      columnSpan: columnSpan,
      customTitle: customTitle,
      settings: settings,
      isStatic: isStatic,
    );
  }
}

@freezed
class AppWidgetModel with _$AppWidgetModel {
  const factory AppWidgetModel({
    required String id,
    required String title,
    required String description,
    required String type,
    required String iconName,
    String? route,
    String? categoryId,
    @Default(false) bool isPremium,
    Map<String, dynamic>? defaultSettings,
    @Default(false) bool isFeatured,
  }) = _AppWidgetModel;

  factory AppWidgetModel.fromJson(Map<String, dynamic> json) =>
      _$AppWidgetModelFromJson(json);

  // 从领域实体转换
  factory AppWidgetModel.fromEntity(AppWidget entity) {
    return AppWidgetModel(
      id: entity.id,
      title: entity.title,
      description: entity.description,
      type: entity.type,
      iconName: entity.iconName,
      route: entity.route,
      categoryId: entity.categoryId,
      isPremium: entity.isPremium,
      defaultSettings: entity.defaultSettings,
      isFeatured: entity.isFeatured,
    );
  }
}

extension AppWidgetModelX on AppWidgetModel {
  // 转换为领域实体
  AppWidget toEntity() {
    return AppWidget(
      id: id,
      title: title,
      description: description,
      type: type,
      iconName: iconName,
      route: route,
      categoryId: categoryId,
      isPremium: isPremium,
      defaultSettings: defaultSettings,
      isFeatured: isFeatured,
    );
  }
}

@freezed
class AppCategoryModel with _$AppCategoryModel {
  const factory AppCategoryModel({
    required String id,
    required String name,
    required String description,
    required String iconName,
    int? displayOrder,
    @Default(false) bool isPremium,
  }) = _AppCategoryModel;

  factory AppCategoryModel.fromJson(Map<String, dynamic> json) =>
      _$AppCategoryModelFromJson(json);

  // 从领域实体转换
  factory AppCategoryModel.fromEntity(AppCategory entity) {
    return AppCategoryModel(
      id: entity.id,
      name: entity.name,
      description: entity.description,
      iconName: entity.iconName,
      displayOrder: entity.displayOrder,
      isPremium: entity.isPremium,
    );
  }
}

extension AppCategoryModelX on AppCategoryModel {
  // 转换为领域实体
  AppCategory toEntity() {
    return AppCategory(
      id: id,
      name: name,
      description: description,
      iconName: iconName,
      displayOrder: displayOrder,
      isPremium: isPremium,
    );
  }
}

@freezed
class SavedLayoutModel with _$SavedLayoutModel {
  const factory SavedLayoutModel({
    required String id,
    required String name,
    required DateTime createdAt,
    required AppDashboardModel dashboard,
  }) = _SavedLayoutModel;

  factory SavedLayoutModel.fromJson(Map<String, dynamic> json) =>
      _$SavedLayoutModelFromJson(json);

  // 从领域实体转换
  factory SavedLayoutModel.fromEntity(SavedLayout entity) {
    return SavedLayoutModel(
      id: entity.id,
      name: entity.name,
      createdAt: entity.createdAt,
      dashboard: AppDashboardModel.fromEntity(entity.dashboard),
    );
  }
}

extension SavedLayoutModelX on SavedLayoutModel {
  // 转换为领域实体
  SavedLayout toEntity() {
    return SavedLayout(
      id: id,
      name: name,
      createdAt: createdAt,
      dashboard: dashboard.toEntity(),
    );
  }
}