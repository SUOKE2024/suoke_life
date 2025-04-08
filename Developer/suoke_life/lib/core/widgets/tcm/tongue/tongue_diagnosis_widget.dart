import 'dart:async';
import 'dart:io';
import 'dart:math' as math;

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/core/widgets/tcm/models/tongue_diagnosis_data.dart';
import 'package:suoke_life/core/widgets/tcm/tongue/tongue_image_processor.dart';
import 'package:suoke_life/core/widgets/tcm/tongue/tongue_diagnosis_state.dart';
import 'package:suoke_life/core/widgets/tcm/tongue/tongue_diagnosis_notifier.dart';

/// 舌诊分析Widget组件
class TongueDiagnosisWidget extends ConsumerStatefulWidget {
  /// 初始图片路径
  final String? initialImagePath;

  /// 创建舌诊组件
  const TongueDiagnosisWidget({super.key, this.initialImagePath});

  @override
  ConsumerState<TongueDiagnosisWidget> createState() =>
      _TongueDiagnosisWidgetState();
}

class _TongueDiagnosisWidgetState extends ConsumerState<TongueDiagnosisWidget>
    with WidgetsBindingObserver {
  // 是否首次构建
  bool _isFirstBuild = true;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);

    // 如果有初始图片路径，延迟加载图片
    if (widget.initialImagePath != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _loadInitialImage();
      });
    }
  }

  /// 加载初始图片
  Future<void> _loadInitialImage() async {
    try {
      final notifier = ref.read(tongueDiagnosisStateProvider.notifier);
      await notifier.loadImageFromPath(widget.initialImagePath!);
    } catch (e) {
      debugPrint('加载初始图片失败: $e');
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    // 停止分析
    final notifier = ref.read(tongueDiagnosisStateProvider.notifier);
    notifier.stopAnalysis();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.paused ||
        state == AppLifecycleState.inactive) {
      // 停止分析当应用进入后台
      ref.read(tongueDiagnosisStateProvider.notifier).stopAnalysis();
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(tongueDiagnosisStateProvider);
    final notifier = ref.read(tongueDiagnosisStateProvider.notifier);

    // 首次构建时初始化相机
    if (_isFirstBuild) {
      _isFirstBuild = false;
      // 使用Future.microtask避免在构建过程中调用setState
      Future.microtask(() {
        ref.read(tongueDiagnosisStateProvider.notifier).initializeCamera();
      });
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('舌诊分析'),
        backgroundColor: AppColors.primaryColor,
      ),
      body: _buildBody(state),
      floatingActionButton: _buildActionButton(state),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
    );
  }

  /// 构建主体内容
  Widget _buildBody(TongueDiagnosisState state) {
    if (state.isInitializing) {
      return _buildLoadingView('正在初始化相机...');
    }

    if (state.errorMessage != null) {
      return _buildErrorView(state.errorMessage!);
    }

    if (state.result != null) {
      return _buildResultView(state);
    }

    return _buildCameraView(state);
  }

  /// 构建加载视图
  Widget _buildLoadingView(String message) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(),
          const SizedBox(height: 16),
          Text(message, style: const TextStyle(fontSize: 16)),
        ],
      ),
    );
  }

  /// 构建错误视图
  Widget _buildErrorView(String errorMessage) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 48, color: Colors.red),
          const SizedBox(height: 16),
          Text(errorMessage, style: const TextStyle(fontSize: 16)),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () {
              ref
                  .read(tongueDiagnosisStateProvider.notifier)
                  .initializeCamera();
            },
            child: const Text('重试'),
          ),
        ],
      ),
    );
  }

  /// 构建相机视图
  Widget _buildCameraView(TongueDiagnosisState state) {
    if (state.cameraController == null ||
        !state.cameraController!.value.isInitialized) {
      return _buildLoadingView('相机初始化中...');
    }

    return Column(
      children: [
        Expanded(
          child: Stack(
            alignment: Alignment.center,
            children: [
              // 相机预览
              _buildCameraPreview(state),

              // 引导覆盖层
              _buildGuidanceOverlay(state),
            ],
          ),
        ),

        // 底部指导区域
        _buildGuidanceText(state),

        // 底部间距（为FloatingActionButton留出空间）
        const SizedBox(height: 80),
      ],
    );
  }

  /// 构建相机预览
  Widget _buildCameraPreview(TongueDiagnosisState state) {
    final size = MediaQuery.of(context).size;
    final deviceRatio = size.width / size.height;

    // 计算预览尺寸
    final scale = 1 / (state.cameraController!.value.aspectRatio * deviceRatio);

    return Transform.scale(
      scale: scale,
      alignment: Alignment.center,
      child: CameraPreview(state.cameraController!),
    );
  }

  /// 构建引导覆盖层
  Widget _buildGuidanceOverlay(TongueDiagnosisState state) {
    final screenWidth = MediaQuery.of(context).size.width;
    final boxWidth = screenWidth * 0.8;
    final boxHeight = boxWidth * 0.6;

    return Stack(
      alignment: Alignment.center,
      children: [
        // 辅助线 - 增强用户视觉引导
        CustomPaint(
          size: Size(screenWidth, boxHeight + 40),
          painter: GuidanceOverlayPainter(
            isAnalyzing: state.isAnalyzing,
          ),
        ),

        // 舌头检测区域框
        Container(
          decoration: BoxDecoration(
            border: Border.all(
              color: state.isAnalyzing ? Colors.green : Colors.white70,
              width: 2,
            ),
            borderRadius: BorderRadius.circular(16),
          ),
          width: boxWidth,
          height: boxHeight,
          child: Stack(
            alignment: Alignment.center,
            children: [
              // 中心舌头示意图
              if (!state.isAnalyzing)
                Opacity(
                  opacity: 0.4,
                  child: Icon(
                    Icons.accessibility_new,
                    color: Colors.white,
                    size: boxWidth * 0.2,
                  ),
                ),

              // 分析中指示器
              if (state.isAnalyzing)
                const CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),

              // 角落标记 - 增强视觉引导
              Positioned(
                top: 8,
                left: 8,
                child: Container(
                  width: 16,
                  height: 16,
                  decoration: BoxDecoration(
                    color: Colors.transparent,
                    border: Border(
                      top: BorderSide(color: Colors.white70, width: 2),
                      left: BorderSide(color: Colors.white70, width: 2),
                    ),
                  ),
                ),
              ),
              Positioned(
                top: 8,
                right: 8,
                child: Container(
                  width: 16,
                  height: 16,
                  decoration: BoxDecoration(
                    color: Colors.transparent,
                    border: Border(
                      top: BorderSide(color: Colors.white70, width: 2),
                      right: BorderSide(color: Colors.white70, width: 2),
                    ),
                  ),
                ),
              ),
              Positioned(
                bottom: 8,
                left: 8,
                child: Container(
                  width: 16,
                  height: 16,
                  decoration: BoxDecoration(
                    color: Colors.transparent,
                    border: Border(
                      bottom: BorderSide(color: Colors.white70, width: 2),
                      left: BorderSide(color: Colors.white70, width: 2),
                    ),
                  ),
                ),
              ),
              Positioned(
                bottom: 8,
                right: 8,
                child: Container(
                  width: 16,
                  height: 16,
                  decoration: BoxDecoration(
                    color: Colors.transparent,
                    border: Border(
                      bottom: BorderSide(color: Colors.white70, width: 2),
                      right: BorderSide(color: Colors.white70, width: 2),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  /// 构建底部指导区域
  Widget _buildGuidanceText(TongueDiagnosisState state) {
    return Container(
      padding: const EdgeInsets.all(16),
      color: Colors.black87,
      width: double.infinity,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            state.isAnalyzing ? Icons.check_circle : Icons.info_outline,
            color: state.isAnalyzing ? Colors.green : Colors.blue,
            size: 24,
          ),
          const SizedBox(height: 8),
          Text(
            state.guidanceText ?? '请将舌头伸出并对准屏幕中央区域',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          Text(
            state.isAnalyzing ? '正在分析中，请保持不动...' : '提示: 保持充足光线，将舌头完全伸出并填满中央区域',
            style: TextStyle(
              color: Colors.white.withAlpha(180),
              fontSize: 14,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  /// 构建结果视图
  Widget _buildResultView(TongueDiagnosisState state) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 结果卡片
          _buildResultCard(state),

          const SizedBox(height: 16),

          // 特征详情
          _buildFeaturesDetail(state),

          const SizedBox(height: 16),

          // 建议
          _buildSuggestions(state),

          const SizedBox(height: 80), // 为底部按钮留空间
        ],
      ),
    );
  }

  /// 构建结果卡片
  Widget _buildResultCard(TongueDiagnosisState state) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '舌诊结果',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const Divider(),
            const SizedBox(height: 8),
            Text(
              state.result?.analysisText ?? '无法生成分析结果',
              style: const TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 16),
            _buildResultChips(state),
          ],
        ),
      ),
    );
  }

  /// 构建结果标签
  Widget _buildResultChips(TongueDiagnosisState state) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        if (state.result?.syndromes.isNotEmpty ?? false)
          ...state.result!.syndromes.map((syndrome) => Chip(
                label: Text(syndrome),
                backgroundColor: AppColors.primaryColor.withAlpha(50),
              )),
        if (state.result?.constitutions.isNotEmpty ?? false)
          ...state.result!.constitutions.map((constitution) => Chip(
                label: Text(constitution),
                backgroundColor: AppColors.secondaryColor.withAlpha(50),
              )),
      ],
    );
  }

  /// 构建特征详情
  Widget _buildFeaturesDetail(TongueDiagnosisState state) {
    if (state.features == null) return const SizedBox.shrink();

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '舌诊特征',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const Divider(),
            const SizedBox(height: 8),
            _buildFeatureItem(
              '舌质',
              TongueDiagnosisFeatures.getBodyFeatureDescription(
                  state.features!.bodyFeature),
              state.features!.bodyConfidence,
              Color(state.regionColors?['body'] ?? 0xFFFFFFFF),
            ),
            _buildFeatureItem(
              '舌苔',
              TongueDiagnosisFeatures.getCoatingFeatureDescription(
                  state.features!.coatingFeature),
              state.features!.coatingConfidence,
              Color(state.regionColors?['coating'] ?? 0xFFFFFFFF),
            ),
            _buildFeatureItem(
              '舌形',
              TongueDiagnosisFeatures.getShapeFeatureDescription(
                  state.features!.shapeFeature),
              state.features!.shapeConfidence,
              AppColors.primaryColor.withAlpha(50),
            ),
            _buildFeatureItem(
              '舌下络脉',
              TongueDiagnosisFeatures.getVeinFeatureDescription(
                  state.features!.veinFeature),
              state.features!.veinConfidence,
              Color(state.regionColors?['vein'] ?? 0xFFFFFFFF),
            ),
          ],
        ),
      ),
    );
  }

  /// 构建特征项
  Widget _buildFeatureItem(
      String title, String description, double confidence, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 24,
            height: 24,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
              border: Border.all(color: Colors.grey.shade300),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '$title: $description',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                LinearProgressIndicator(
                  value: confidence,
                  backgroundColor: Colors.grey.shade200,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    _getConfidenceColor(confidence),
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  '可信度: ${(confidence * 100).toStringAsFixed(0)}%',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey.shade600,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 获取可信度颜色
  Color _getConfidenceColor(double confidence) {
    if (confidence > 0.8) {
      return Colors.green;
    } else if (confidence > 0.6) {
      return Colors.orange;
    } else {
      return Colors.red;
    }
  }

  /// 构建建议
  Widget _buildSuggestions(TongueDiagnosisState state) {
    if (state.result?.suggestions.isEmpty ?? true)
      return const SizedBox.shrink();

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '调理建议',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const Divider(),
            const SizedBox(height: 8),
            ...state.result!.suggestions.map((suggestion) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(Icons.check_circle,
                          color: AppColors.primaryColor, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          suggestion,
                          style: const TextStyle(fontSize: 16),
                        ),
                      ),
                    ],
                  ),
                )),
          ],
        ),
      ),
    );
  }

  /// 构建动作按钮
  Widget _buildActionButton(TongueDiagnosisState state) {
    if (state.result != null) {
      // 显示分析结果时的按钮
      return Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          FloatingActionButton.extended(
            heroTag: 'save_btn',
            onPressed: () {
              ref.read(tongueDiagnosisStateProvider.notifier).saveResult();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('舌诊结果已保存')),
              );
            },
            icon: const Icon(Icons.save),
            label: const Text('保存结果'),
            backgroundColor: AppColors.primaryColor,
          ),
          const SizedBox(width: 16),
          FloatingActionButton.extended(
            heroTag: 'restart_btn',
            onPressed: () {
              ref
                  .read(tongueDiagnosisStateProvider.notifier)
                  .initializeCamera();
            },
            icon: const Icon(Icons.refresh),
            label: const Text('重新检测'),
            backgroundColor: Colors.grey.shade700,
          ),
        ],
      );
    } else {
      // 相机预览时的按钮
      return FloatingActionButton.extended(
        onPressed: state.isAnalyzing
            ? () =>
                ref.read(tongueDiagnosisStateProvider.notifier).stopAnalysis()
            : () =>
                ref.read(tongueDiagnosisStateProvider.notifier).startAnalysis(),
        icon: Icon(state.isAnalyzing ? Icons.stop : Icons.camera_alt),
        label: Text(state.isAnalyzing ? '停止分析' : '开始分析'),
        backgroundColor:
            state.isAnalyzing ? Colors.red : AppColors.primaryColor,
      );
    }
  }
}

/// 引导覆盖画笔
class GuidanceOverlayPainter extends CustomPainter {
  final bool isAnalyzing;

  GuidanceOverlayPainter({required this.isAnalyzing});

  @override
  void paint(Canvas canvas, Size size) {
    final width = size.width;
    final height = size.height;
    final centerX = width / 2;
    final centerY = height / 2;

    final paint = Paint()
      ..color =
          isAnalyzing ? Colors.green.withAlpha(100) : Colors.white.withAlpha(70)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5;

    // 绘制中心十字线
    canvas.drawLine(
        Offset(centerX - 20, centerY), Offset(centerX + 20, centerY), paint);
    canvas.drawLine(
        Offset(centerX, centerY - 20), Offset(centerX, centerY + 20), paint);

    // 绘制舌头轮廓参考线（椭圆形）
    final ellipseRect = Rect.fromCenter(
      center: Offset(centerX, centerY),
      width: width * 0.4,
      height: height * 0.5,
    );
    canvas.drawOval(ellipseRect, paint..style = PaintingStyle.stroke);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
