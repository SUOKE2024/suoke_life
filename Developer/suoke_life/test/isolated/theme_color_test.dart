import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life/core/theme/app_colors.dart';

/// 模拟聊天屏幕中的获取智能体主题色方法
Color getAgentThemeColor(String? agentId) {
  if (agentId == null) return AppColors.primaryColor;
  
  switch (agentId) {
    case 'xiaoke-service':
      return Colors.blue.shade600;
    case 'xiaoai-service':
      return AppColors.primaryColor;
    case 'soer-service':
      return Colors.purple.shade600;
    case 'laoke-service':
      return Colors.amber.shade800;
    default:
      return AppColors.primaryColor;
  }
}

void main() {
  group('智能体主题色测试', () {
    test('每个智能体应该有特定的主题色', () {
      // 小柯智能体应该使用蓝色
      final xiaokeColor = getAgentThemeColor('xiaoke-service');
      expect(xiaokeColor, Colors.blue.shade600);
      
      // 小艾智能体应该使用索克主题色
      final xiaoaiColor = getAgentThemeColor('xiaoai-service');
      expect(xiaoaiColor, AppColors.primaryColor);
      
      // 索尔智能体应该使用紫色
      final soerColor = getAgentThemeColor('soer-service');
      expect(soerColor, Colors.purple.shade600);
      
      // 老柯智能体应该使用琥珀色
      final laokeColor = getAgentThemeColor('laoke-service');
      expect(laokeColor, Colors.amber.shade800);
    });
    
    test('未知智能体应该使用默认主题色', () {
      final unknownColor = getAgentThemeColor('unknown-service');
      expect(unknownColor, AppColors.primaryColor);
    });
    
    test('空智能体ID应该使用默认主题色', () {
      final nullColor = getAgentThemeColor(null);
      expect(nullColor, AppColors.primaryColor);
    });
  });
} 