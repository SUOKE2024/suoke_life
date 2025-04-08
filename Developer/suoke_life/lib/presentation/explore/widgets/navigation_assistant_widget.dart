import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/animated_gradient_card.dart';
import '../../../core/widgets/animated_press_button.dart';
import '../../../core/widgets/skeleton_loading.dart';
import '../../../domain/entities/navigation_guidance.dart';
import '../../../data/repositories/navigation_repository_impl.dart';
import '../../../di/providers/navigation_providers.dart';

/// 导航助手组件
class NavigationAssistantWidget extends ConsumerStatefulWidget {
  const NavigationAssistantWidget({Key? key}) : super(key: key);

  @override
  ConsumerState<NavigationAssistantWidget> createState() => _NavigationAssistantWidgetState();
}

class _NavigationAssistantWidgetState extends ConsumerState<NavigationAssistantWidget> {
  bool _isAnalyzingEnvironment = false;
  bool _isProcessingNavigation = false;
  NavigationGuidance? _navigationResult;
  String? _errorMessage;
  
  @override
  Widget build(BuildContext context) {
    final themeData = Theme.of(context);
    
    return AnimatedGradientCard(
      gradientColors: const [
        AppColors.primaryLight,
        AppColors.primaryMedium,
      ],
      borderRadius: BorderRadius.circular(16),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.explore,
                  color: Colors.white.withAlpha(230),
                  size: 24,
                ),
                const SizedBox(width: 8),
                Text(
                  '索克导航助手',
                  style: themeData.textTheme.titleLarge?.copyWith(
                    color: Colors.white.withAlpha(230),
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                if (_isAnalyzingEnvironment || _isProcessingNavigation)
                  const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 16),
            if (_errorMessage != null)
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.red.withAlpha(30),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  _errorMessage!,
                  style: themeData.textTheme.bodyMedium?.copyWith(
                    color: Colors.white.withAlpha(230),
                  ),
                ),
              ),
            if (_navigationResult != null) ...[
              _buildNavigationResult(themeData),
            ] else if (!_isAnalyzingEnvironment && !_isProcessingNavigation) ...[
              _buildDefaultContent(themeData),
            ] else ...[
              _buildLoadingContent(themeData),
            ],
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                Expanded(
                  child: AnimatedPressButton(
                    onPressed: _isAnalyzingEnvironment || _isProcessingNavigation 
                        ? null 
                        : _analyzeEnvironment,
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.camera_alt,
                          color: Colors.white.withAlpha(230),
                          size: 18,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          '环境分析',
                          style: themeData.textTheme.bodyMedium?.copyWith(
                            color: Colors.white.withAlpha(230),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: AnimatedPressButton(
                    onPressed: _isAnalyzingEnvironment || _isProcessingNavigation 
                        ? null 
                        : _getNavigation,
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.navigation,
                          color: Colors.white.withAlpha(230),
                          size: 18,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          '开始导航',
                          style: themeData.textTheme.bodyMedium?.copyWith(
                            color: Colors.white.withAlpha(230),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildDefaultContent(ThemeData themeData) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '导航助手可以帮助您：',
          style: themeData.textTheme.bodyLarge?.copyWith(
            color: Colors.white.withAlpha(230),
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 8),
        _buildFeatureItem(themeData, '识别周围环境和物体'),
        _buildFeatureItem(themeData, '检测人物互动和社交情境'),
        _buildFeatureItem(themeData, '识别中医元素和药用植物'),
        _buildFeatureItem(themeData, '提供个性化导航建议'),
        const SizedBox(height: 8),
        Text(
          '点击下方按钮开始体验！',
          style: themeData.textTheme.bodyMedium?.copyWith(
            color: Colors.white.withAlpha(200),
            fontStyle: FontStyle.italic,
          ),
        ),
      ],
    );
  }
  
  Widget _buildFeatureItem(ThemeData themeData, String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            Icons.check_circle,
            color: Colors.white.withAlpha(230),
            size: 16,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              text,
              style: themeData.textTheme.bodyMedium?.copyWith(
                color: Colors.white.withAlpha(230),
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildLoadingContent(ThemeData themeData) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 8),
        SkeletonLoading(
          height: 20,
          width: MediaQuery.of(context).size.width * 0.7,
          borderRadius: 4,
        ),
        const SizedBox(height: 12),
        SkeletonLoading(
          height: 16,
          width: MediaQuery.of(context).size.width * 0.5,
          borderRadius: 4,
        ),
        const SizedBox(height: 8),
        SkeletonLoading(
          height: 16,
          width: MediaQuery.of(context).size.width * 0.6,
          borderRadius: 4,
        ),
        const SizedBox(height: 8),
        SkeletonLoading(
          height: 16,
          width: MediaQuery.of(context).size.width * 0.55,
          borderRadius: 4,
        ),
        const SizedBox(height: 8),
        SkeletonLoading(
          height: 16,
          width: MediaQuery.of(context).size.width * 0.65,
          borderRadius: 4,
        ),
      ],
    );
  }
  
  Widget _buildNavigationResult(ThemeData themeData) {
    final result = _navigationResult!;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (result.environmentType != null) ...[
          Row(
            children: [
              Icon(
                Icons.place,
                color: Colors.white.withAlpha(230),
                size: 18,
              ),
              const SizedBox(width: 8),
              Text(
                '当前环境：${result.environmentType}',
                style: themeData.textTheme.bodyLarge?.copyWith(
                  color: Colors.white.withAlpha(230),
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
        ],
        
        if (result.objects.isNotEmpty) ...[
          Text(
            '已识别物体：',
            style: themeData.textTheme.bodyMedium?.copyWith(
              color: Colors.white.withAlpha(230),
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 4),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: result.objects.map((object) => _buildObjectChip(object)).toList(),
          ),
          const SizedBox(height: 12),
        ],
        
        if (result.tcmElements.isNotEmpty) ...[
          Text(
            '中医元素：',
            style: themeData.textTheme.bodyMedium?.copyWith(
              color: Colors.white.withAlpha(230),
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 4),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: result.tcmElements.map((element) => _buildTCMElementChip(element)).toList(),
          ),
          const SizedBox(height: 12),
        ],
        
        if (result.recommendation != null) ...[
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(
                Icons.lightbulb,
                color: Colors.amber.withAlpha(230),
                size: 18,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '导航建议：',
                      style: themeData.textTheme.bodyMedium?.copyWith(
                        color: Colors.white.withAlpha(230),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      result.recommendation!,
                      style: themeData.textTheme.bodyMedium?.copyWith(
                        color: Colors.white.withAlpha(230),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ],
    );
  }
  
  Widget _buildObjectChip(String object) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white.withAlpha(50),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.white.withAlpha(100),
          width: 1,
        ),
      ),
      child: Text(
        object,
        style: TextStyle(
          color: Colors.white.withAlpha(230),
          fontSize: 12,
        ),
      ),
    );
  }
  
  Widget _buildTCMElementChip(String element) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: AppColors.tcmAccent.withAlpha(80),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: AppColors.tcmAccent.withAlpha(150),
          width: 1,
        ),
      ),
      child: Text(
        element,
        style: TextStyle(
          color: Colors.white.withAlpha(230),
          fontSize: 12,
        ),
      ),
    );
  }
  
  Future<void> _analyzeEnvironment() async {
    setState(() {
      _isAnalyzingEnvironment = true;
      _errorMessage = null;
    });
    
    try {
      // 使用Riverpod访问导航服务
      final navigationService = ref.read(navigationServiceProvider);
      
      // 获取当前位置（在实际应用中应该使用定位服务）
      final location = {
        'latitude': 30.123456,
        'longitude': 120.123456,
      };
      
      // 获取环境分析结果
      final result = await navigationService.analyzeEnvironment(
        location: location,
        // 在实际应用中，这里应该获取设备相机拍摄的图像
        imageData: 'dummy_image_data',
      );
      
      setState(() {
        _navigationResult = result;
        _isAnalyzingEnvironment = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = '环境分析失败：${e.toString()}';
        _isAnalyzingEnvironment = false;
      });
    }
  }
  
  Future<void> _getNavigation() async {
    setState(() {
      _isProcessingNavigation = true;
      _errorMessage = null;
    });
    
    try {
      // 使用Riverpod访问导航服务
      final navigationService = ref.read(navigationServiceProvider);
      
      // 获取当前位置和目的地（在实际应用中应该使用定位服务和用户选择）
      final location = {
        'latitude': 30.123456,
        'longitude': 120.123456,
      };
      
      final destination = {
        'latitude': 30.124567,
        'longitude': 120.125678,
        'name': '某中医馆',
      };
      
      // 获取导航建议
      final result = await navigationService.getNavigation(
        location: location,
        destination: destination,
        preferences: {
          'avoidCrowds': true,
          'preferQuiet': true,
          'accessibility': 'standard',
          'pace': 'normal',
        },
      );
      
      setState(() {
        _navigationResult = result;
        _isProcessingNavigation = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = '获取导航失败：${e.toString()}';
        _isProcessingNavigation = false;
      });
    }
  }
} 