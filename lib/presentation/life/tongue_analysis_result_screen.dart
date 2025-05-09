import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/models/tongue_analysis_model.dart';
import 'package:suoke_life/domain/repositories/diagnosis_repository.dart';

/// 舌象分析结果状态提供者
final tongueAnalysisProvider = FutureProvider.autoDispose.family<TongueAnalysis, String>(
  (ref, imagePath) async {
    // 模拟舌象分析过程
    // TODO: 实现实际的舌象图像分析算法
    await Future.delayed(const Duration(seconds: 2));
    
    // 创建舌象分析结果
    return TongueAnalysis.create(
      userId: 'current_user',
      imagePath: imagePath,
      tongueColor: TongueColor.lightRed,
      coatingColor: CoatingColor.white,
      coatingThickness: CoatingThickness.thin,
      tongueShape: TongueShape.normal,
      moisture: TongueMoisture.normal,
      tremor: TongueTremor.none,
    );
  },
);

/// 舌象分析描述提供者
final tongueAnalysisDescriptionProvider = FutureProvider.autoDispose.family<String, TongueAnalysis>(
  (ref, analysis) async {
    final repository = ref.watch(diagnosisRepositoryProvider);
    return repository.generateTongueAnalysisDescription(analysis);
  },
);

/// 舌象体质推断提供者
final constitutionInferenceProvider = FutureProvider.autoDispose.family<List<String>, TongueAnalysis>(
  (ref, analysis) async {
    final repository = ref.watch(diagnosisRepositoryProvider);
    return repository.inferConstitutionFromTongueAnalysis(analysis);
  },
);

/// 诊断仓库提供者
final diagnosisRepositoryProvider = Provider<DiagnosisRepository>((ref) {
  // TODO: 从依赖注入中获取实际的仓库实例
  throw UnimplementedError('需要在主应用中提供仓库实例');
});

/// 舌象分析结果页面
class TongueAnalysisResultScreen extends ConsumerWidget {
  /// 舌象图像路径
  final String imagePath;

  /// 构造函数
  const TongueAnalysisResultScreen({
    super.key,
    required this.imagePath,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final analysisAsync = ref.watch(tongueAnalysisProvider(imagePath));
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('舌象分析结果'),
        elevation: 0,
      ),
      body: analysisAsync.when(
        loading: () => const Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text('正在进行舌象特征识别与分析...')
            ],
          ),
        ),
        error: (error, stackTrace) => Center(
          child: Text('分析出错: $error'),
        ),
        data: (analysis) => _buildAnalysisResult(context, ref, analysis),
      ),
    );
  }
  
  /// 构建分析结果视图
  Widget _buildAnalysisResult(BuildContext context, WidgetRef ref, TongueAnalysis analysis) {
    final descriptionAsync = ref.watch(tongueAnalysisDescriptionProvider(analysis));
    final constitutionsAsync = ref.watch(constitutionInferenceProvider(analysis));
    
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 舌象图像
          ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: Image.file(
              File(imagePath),
              width: double.infinity,
              height: 250,
              fit: BoxFit.cover,
            ),
          ),
          
          const SizedBox(height: 24),
          
          // 特征总结
          const Text(
            '舌象特征',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          
          const SizedBox(height: 8),
          
          // 舌质特征卡片
          _buildFeatureCard(
            title: '舌质',
            color: analysis.getTongueColorValue(),
            features: [
              '颜色: ${analysis.tongueColorName}',
              '形态: ${analysis.tongueShapeName}',
              '湿度: ${analysis.moistureName}',
              '颤动: ${analysis.tremorName}',
            ],
          ),
          
          const SizedBox(height: 16),
          
          // 舌苔特征卡片
          _buildFeatureCard(
            title: '舌苔',
            color: _getCoatingColor(analysis.coatingColor),
            features: [
              '颜色: ${analysis.coatingColorName}',
              '厚度: ${analysis.coatingThicknessName}',
            ],
          ),
          
          const SizedBox(height: 24),
          
          // 分析描述
          const Text(
            '分析结果',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          
          const SizedBox(height: 8),
          
          descriptionAsync.when(
            loading: () => const Center(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: CircularProgressIndicator(),
              ),
            ),
            error: (error, stackTrace) => Text('无法生成分析: $error'),
            data: (description) => Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.grey.withOpacity(0.2),
                    spreadRadius: 1,
                    blurRadius: 6,
                    offset: const Offset(0, 3),
                  ),
                ],
              ),
              child: Text(
                description,
                style: const TextStyle(fontSize: 16, height: 1.5),
              ),
            ),
          ),
          
          const SizedBox(height: 24),
          
          // 体质倾向
          const Text(
            '体质倾向',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          
          const SizedBox(height: 8),
          
          constitutionsAsync.when(
            loading: () => const Center(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: CircularProgressIndicator(),
              ),
            ),
            error: (error, stackTrace) => Text('无法推断体质: $error'),
            data: (constitutions) => constitutions.isEmpty
                ? const Text('无明显体质倾向')
                : Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: constitutions
                        .map((constitution) => Chip(
                              label: Text(constitution),
                              backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                            ))
                        .toList(),
                  ),
          ),
          
          const SizedBox(height: 32),
          
          // 注意事项
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.amber.withOpacity(0.2),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.amber),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '注意事项',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.amber,
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  '舌象只是中医四诊中的一部分，完整的体质分析需要结合望、闻、问、切四诊综合判断。建议进行完整的四诊采集，以获得更准确的健康评估。',
                  style: TextStyle(fontSize: 15, height: 1.5),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 24),
          
          // 继续四诊按钮
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                // TODO: 导航到四诊主流程
                Navigator.of(context).pop();
              },
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
              child: const Text('继续完成四诊'),
            ),
          ),
        ],
      ),
    );
  }
  
  /// 构建特征卡片
  Widget _buildFeatureCard({
    required String title,
    required Color color,
    required List<String> features,
  }) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.2),
            spreadRadius: 1,
            blurRadius: 6,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Row(
        children: [
          // 颜色示例
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
              border: Border.all(color: Colors.grey.withOpacity(0.3)),
            ),
          ),
          
          const SizedBox(width: 16),
          
          // 特征列表
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                ...features.map((feature) => Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Text(feature),
                    )),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  /// 获取舌苔颜色对应的实际颜色
  Color _getCoatingColor(CoatingColor color) {
    switch (color) {
      case CoatingColor.white:
        return const Color(0xFFF5F5F5);
      case CoatingColor.lightYellow:
        return const Color(0xFFFFF9C4);
      case CoatingColor.yellow:
        return const Color(0xFFFFEB3B);
      case CoatingColor.gray:
        return const Color(0xFFBDBDBD);
      case CoatingColor.black:
        return const Color(0xFF424242);
    }
  }
} 