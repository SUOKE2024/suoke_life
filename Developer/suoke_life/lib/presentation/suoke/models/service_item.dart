import 'package:flutter/material.dart';

/// 服务项目模型
class ServiceItem {
  /// 服务ID
  final String id;

  /// 服务名称
  final String name;

  /// 服务描述
  final String description;

  /// 服务图标
  final IconData iconData;

  /// 服务颜色
  final Color color;

  /// 服务价格
  final String? price;

  /// 服务评分
  final double? rating;

  /// 服务图片URL
  final String? imageUrl;

  /// 路由路径
  final String? routePath;

  const ServiceItem({
    required this.id,
    required this.name,
    required this.description,
    required this.iconData,
    required this.color,
    this.price,
    this.rating,
    this.imageUrl,
    this.routePath,
  });
}
