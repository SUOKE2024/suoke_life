import 'package:equatable/equatable.dart';
import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';

/// 舌质颜色枚举
enum TongueColor {
  /// 淡白色
  pale,
  
  /// 淡红色（正常）
  lightRed,
  
  /// 红色
  red,
  
  /// 绛红色
  crimson,
  
  /// 紫色
  purple,
  
  /// 青色
  blue,
}

/// 舌苔颜色枚举
enum CoatingColor {
  /// 白色
  white,
  
  /// 淡黄色
  lightYellow,
  
  /// 黄色
  yellow,
  
  /// 灰色
  gray,
  
  /// 黑色
  black,
}

/// 舌苔厚度枚举
enum CoatingThickness {
  /// 无苔
  none,
  
  /// 薄苔
  thin,
  
  /// 厚苔
  thick,
  
  /// 腻苔
  greasy,
}

/// 舌形状态枚举
enum TongueShape {
  /// 正常大小
  normal,
  
  /// 胖大舌（边有齿痕）
  swollen,
  
  /// 瘦薄舌
  thin,
  
  /// 裂纹舌
  cracked,
  
  /// 点刺舌
  thorny,
  
  /// 歪斜舌
  deviated,
}

/// 舌象湿度枚举
enum TongueMoisture {
  /// 正常（微湿润）
  normal,
  
  /// 干燥
  dry,
  
  /// 过度湿润
  wet,
}

/// 舌象颤动状态枚举
enum TongueTremor {
  /// 无颤动
  none,
  
  /// 轻微颤动
  slight,
  
  /// 明显颤动
  obvious,
}

/// 舌象分析模型
class TongueAnalysis extends Equatable {
  /// 分析ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 采集时间
  final DateTime captureTime;
  
  /// 舌象图像路径
  final String imagePath;
  
  /// 舌质颜色
  final TongueColor tongueColor;
  
  /// 舌苔颜色
  final CoatingColor coatingColor;
  
  /// 舌苔厚度
  final CoatingThickness coatingThickness;
  
  /// 舌形状态
  final TongueShape tongueShape;
  
  /// 舌象湿度
  final TongueMoisture moisture;
  
  /// 舌象颤动状态
  final TongueTremor tremor;
  
  /// 分析结果描述
  final String? analysisDescription;
  
  /// 相关体质倾向
  final List<String>? constitutionTendencies;
  
  /// 额外特征标记
  final Map<String, dynamic>? extraFeatures;
  
  /// 备注
  final String? note;

  /// 构造函数
  const TongueAnalysis({
    required this.id,
    required this.userId,
    required this.captureTime,
    required this.imagePath,
    required this.tongueColor,
    required this.coatingColor,
    required this.coatingThickness,
    required this.tongueShape,
    required this.moisture,
    required this.tremor,
    this.analysisDescription,
    this.constitutionTendencies,
    this.extraFeatures,
    this.note,
  });

  /// 创建新的舌象分析记录
  factory TongueAnalysis.create({
    required String userId,
    required String imagePath,
    required TongueColor tongueColor,
    required CoatingColor coatingColor,
    required CoatingThickness coatingThickness,
    required TongueShape tongueShape,
    required TongueMoisture moisture,
    required TongueTremor tremor,
    String? analysisDescription,
    List<String>? constitutionTendencies,
    Map<String, dynamic>? extraFeatures,
    String? note,
  }) {
    return TongueAnalysis(
      id: const Uuid().v4(),
      userId: userId,
      captureTime: DateTime.now(),
      imagePath: imagePath,
      tongueColor: tongueColor,
      coatingColor: coatingColor,
      coatingThickness: coatingThickness,
      tongueShape: tongueShape,
      moisture: moisture,
      tremor: tremor,
      analysisDescription: analysisDescription,
      constitutionTendencies: constitutionTendencies,
      extraFeatures: extraFeatures,
      note: note,
    );
  }

  /// 舌质颜色名称
  String get tongueColorName {
    switch (tongueColor) {
      case TongueColor.pale:
        return '淡白';
      case TongueColor.lightRed:
        return '淡红';
      case TongueColor.red:
        return '红';
      case TongueColor.crimson:
        return '绛红';
      case TongueColor.purple:
        return '紫';
      case TongueColor.blue:
        return '青';
    }
  }

  /// 舌苔颜色名称
  String get coatingColorName {
    switch (coatingColor) {
      case CoatingColor.white:
        return '白';
      case CoatingColor.lightYellow:
        return '淡黄';
      case CoatingColor.yellow:
        return '黄';
      case CoatingColor.gray:
        return '灰';
      case CoatingColor.black:
        return '黑';
    }
  }

  /// 舌苔厚度名称
  String get coatingThicknessName {
    switch (coatingThickness) {
      case CoatingThickness.none:
        return '无苔';
      case CoatingThickness.thin:
        return '薄苔';
      case CoatingThickness.thick:
        return '厚苔';
      case CoatingThickness.greasy:
        return '腻苔';
    }
  }

  /// 舌形状态名称
  String get tongueShapeName {
    switch (tongueShape) {
      case TongueShape.normal:
        return '正常';
      case TongueShape.swollen:
        return '胖大';
      case TongueShape.thin:
        return '瘦薄';
      case TongueShape.cracked:
        return '裂纹';
      case TongueShape.thorny:
        return '点刺';
      case TongueShape.deviated:
        return '歪斜';
    }
  }

  /// 舌象湿度名称
  String get moistureName {
    switch (moisture) {
      case TongueMoisture.normal:
        return '正常';
      case TongueMoisture.dry:
        return '干燥';
      case TongueMoisture.wet:
        return '湿润';
    }
  }

  /// 舌象颤动状态名称
  String get tremorName {
    switch (tremor) {
      case TongueTremor.none:
        return '无颤动';
      case TongueTremor.slight:
        return '轻微颤动';
      case TongueTremor.obvious:
        return '明显颤动';
    }
  }

  /// 获取舌象特征综合描述
  String getFeatureDescription() {
    return '$tongueColorName舌，$coatingColorName色$coatingThicknessName，舌体$tongueShapeName，$moistureName，$tremorName';
  }

  /// 获取舌质颜色对应的实际颜色
  Color getTongueColorValue() {
    switch (tongueColor) {
      case TongueColor.pale:
        return const Color(0xFFF8D0D0);
      case TongueColor.lightRed:
        return const Color(0xFFF08080);
      case TongueColor.red:
        return const Color(0xFFDC143C);
      case TongueColor.crimson:
        return const Color(0xFFB22222);
      case TongueColor.purple:
        return const Color(0xFF800080);
      case TongueColor.blue:
        return const Color(0xFF4169E1);
    }
  }

  /// 复制分析并修改部分属性
  TongueAnalysis copyWith({
    String? id,
    String? userId,
    DateTime? captureTime,
    String? imagePath,
    TongueColor? tongueColor,
    CoatingColor? coatingColor,
    CoatingThickness? coatingThickness,
    TongueShape? tongueShape,
    TongueMoisture? moisture,
    TongueTremor? tremor,
    String? analysisDescription,
    List<String>? constitutionTendencies,
    Map<String, dynamic>? extraFeatures,
    String? note,
  }) {
    return TongueAnalysis(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      captureTime: captureTime ?? this.captureTime,
      imagePath: imagePath ?? this.imagePath,
      tongueColor: tongueColor ?? this.tongueColor,
      coatingColor: coatingColor ?? this.coatingColor,
      coatingThickness: coatingThickness ?? this.coatingThickness,
      tongueShape: tongueShape ?? this.tongueShape,
      moisture: moisture ?? this.moisture,
      tremor: tremor ?? this.tremor,
      analysisDescription: analysisDescription ?? this.analysisDescription,
      constitutionTendencies: constitutionTendencies ?? this.constitutionTendencies,
      extraFeatures: extraFeatures ?? this.extraFeatures,
      note: note ?? this.note,
    );
  }

  /// 从JSON转换为模型
  factory TongueAnalysis.fromJson(Map<String, dynamic> json) {
    return TongueAnalysis(
      id: json['id'],
      userId: json['user_id'],
      captureTime: DateTime.parse(json['capture_time']),
      imagePath: json['image_path'],
      tongueColor: TongueColor.values.byName(json['tongue_color']),
      coatingColor: CoatingColor.values.byName(json['coating_color']),
      coatingThickness: CoatingThickness.values.byName(json['coating_thickness']),
      tongueShape: TongueShape.values.byName(json['tongue_shape']),
      moisture: TongueMoisture.values.byName(json['moisture']),
      tremor: TongueTremor.values.byName(json['tremor']),
      analysisDescription: json['analysis_description'],
      constitutionTendencies: json['constitution_tendencies'] != null
          ? List<String>.from(json['constitution_tendencies'])
          : null,
      extraFeatures: json['extra_features'],
      note: json['note'],
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'capture_time': captureTime.toIso8601String(),
      'image_path': imagePath,
      'tongue_color': tongueColor.name,
      'coating_color': coatingColor.name,
      'coating_thickness': coatingThickness.name,
      'tongue_shape': tongueShape.name,
      'moisture': moisture.name,
      'tremor': tremor.name,
      'analysis_description': analysisDescription,
      'constitution_tendencies': constitutionTendencies,
      'extra_features': extraFeatures,
      'note': note,
    };
  }

  @override
  List<Object?> get props => [
    id,
    userId,
    captureTime,
    imagePath,
    tongueColor,
    coatingColor,
    coatingThickness,
    tongueShape,
    moisture,
    tremor,
    analysisDescription,
    constitutionTendencies,
    extraFeatures,
    note,
  ];
} 