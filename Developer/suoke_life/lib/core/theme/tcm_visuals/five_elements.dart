import 'package:flutter/material.dart';

/// 五行元素类型
enum ElementType {
  /// 木
  wood,

  /// 火
  fire,

  /// 土
  earth,

  /// 金
  metal,

  /// 水
  water,
}

/// 五行元素工具类
class FiveElements {
  /// 获取元素颜色
  static Color getElementColor(ElementType type) {
    switch (type) {
      case ElementType.wood:
        return const Color(0xFF4CAF50);  // 绿色代表木
      case ElementType.fire:
        return const Color(0xFFE53935);  // 红色代表火
      case ElementType.earth:
        return const Color(0xFFFFB300);  // 黄色代表土
      case ElementType.metal:
        return const Color(0xFFBDBDBD);  // 银灰色代表金
      case ElementType.water:
        return const Color(0xFF2196F3);  // 蓝色代表水
    }
  }

  /// 获取元素名称
  static String getElementName(ElementType type) {
    switch (type) {
      case ElementType.wood:
        return '木';
      case ElementType.fire:
        return '火';
      case ElementType.earth:
        return '土';
      case ElementType.metal:
        return '金';
      case ElementType.water:
        return '水';
    }
  }

  /// 获取相生关系
  static ElementType getGeneratesElement(ElementType type) {
    switch (type) {
      case ElementType.wood:
        return ElementType.fire;   // 木生火
      case ElementType.fire:
        return ElementType.earth;  // 火生土
      case ElementType.earth:
        return ElementType.metal;  // 土生金
      case ElementType.metal:
        return ElementType.water;  // 金生水
      case ElementType.water:
        return ElementType.wood;   // 水生木
    }
  }

  /// 获取相克关系
  static ElementType getControlsElement(ElementType type) {
    switch (type) {
      case ElementType.wood:
        return ElementType.earth;  // 木克土
      case ElementType.fire:
        return ElementType.metal;  // 火克金
      case ElementType.earth:
        return ElementType.water;  // 土克水
      case ElementType.metal:
        return ElementType.wood;   // 金克木
      case ElementType.water:
        return ElementType.fire;   // 水克火
    }
  }
} 