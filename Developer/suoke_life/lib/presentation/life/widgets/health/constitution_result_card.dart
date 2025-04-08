import 'package:flutter/material.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/domain/entities/constitution_type.dart';
import 'package:suoke_life/domain/repositories/constitution_repository.dart';
import 'package:intl/intl.dart';

/// 体质识别结果卡片
///
/// 展示用户体质识别结果，包括体质类型、评分、结论等信息
class ConstitutionResultCard extends StatelessWidget {
  /// 体质识别结果
  final ConstitutionTypeResult result;
  
  /// 点击回调
  final VoidCallback? onTap;
  
  /// 创建体质识别结果卡片
  const ConstitutionResultCard({
    Key? key,
    required this.result,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final dateFormatter = DateFormat('yyyy年MM月dd日');
    
    final formattedDate = dateFormatter.format(result.assessmentDate);
    
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 标题和日期
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '体质测评结果',
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    formattedDate,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: Colors.grey,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 16),
              
              // 主要体质类型
              _buildMainConstitutionType(theme),
              
              const SizedBox(height: 12),
              
              // 次要体质类型
              if (result.secondaryTypes != null && result.secondaryTypes!.isNotEmpty)
                _buildSecondaryConstitutionTypes(theme),
              
              const SizedBox(height: 16),
              
              // 体质评分
              _buildConstitutionScores(theme),
              
              const SizedBox(height: 16),
              
              // 结论
              Text(
                '测评结论',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                result.conclusion,
                style: theme.textTheme.bodyMedium,
              ),
              
              // 改善建议
              if (result.improvementSuggestions != null && result.improvementSuggestions!.isNotEmpty) ...[
                const SizedBox(height: 12),
                Text(
                  '改善建议',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  result.improvementSuggestions!,
                  style: theme.textTheme.bodyMedium,
                ),
              ],
              
              // 操作按钮
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  OutlinedButton(
                    onPressed: () {
                      // TODO: 实现查看详情功能
                    },
                    child: const Text('查看详情'),
                  ),
                  const SizedBox(width: 12),
                  ElevatedButton(
                    onPressed: () {
                      // TODO: 实现生成调理方案功能
                    },
                    child: const Text('生成调理方案'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  /// 构建主要体质类型显示
  Widget _buildMainConstitutionType(ThemeData theme) {
    final typeName = _getConstitutionTypeName(result.primaryType);
    final typeColor = _getConstitutionTypeColor(result.primaryType);
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: typeColor.withAlpha(30),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: typeColor),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.account_circle,
            color: typeColor,
            size: 20,
          ),
          const SizedBox(width: 8),
          Text(
            '主要体质: $typeName',
            style: theme.textTheme.titleMedium?.copyWith(
              color: typeColor,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
  
  /// 构建次要体质类型显示
  Widget _buildSecondaryConstitutionTypes(ThemeData theme) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: result.secondaryTypes!.map((type) {
        final typeName = _getConstitutionTypeName(type);
        final typeColor = _getConstitutionTypeColor(type);
        
        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: typeColor.withAlpha(20),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: typeColor.withAlpha(100)),
          ),
          child: Text(
            typeName,
            style: theme.textTheme.bodySmall?.copyWith(
              color: typeColor,
            ),
          ),
        );
      }).toList(),
    );
  }
  
  /// 构建体质评分显示
  Widget _buildConstitutionScores(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '体质评分',
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        _buildScoreBar('平和体质', result.balancedScore, AppColors.balancedTypeColor),
        _buildScoreBar('气虚体质', result.qiDeficiencyScore, AppColors.qiDeficiencyTypeColor),
        _buildScoreBar('阳虚体质', result.yangDeficiencyScore, AppColors.yangDeficiencyTypeColor),
        _buildScoreBar('阴虚体质', result.yinDeficiencyScore, AppColors.yinDeficiencyTypeColor),
        _buildScoreBar('痰湿体质', result.phlegmDampnessScore, AppColors.phlegmDampnessTypeColor),
        _buildScoreBar('湿热体质', result.dampnessHeatScore, AppColors.dampnessHeatTypeColor),
        _buildScoreBar('血瘀体质', result.bloodStasisScore, AppColors.bloodStasisTypeColor),
        _buildScoreBar('气郁体质', result.qiStagnationScore, AppColors.qiStagnationTypeColor),
        _buildScoreBar('特禀体质', result.specialConstitutionScore, AppColors.specialTypeColor),
      ],
    );
  }
  
  /// 构建单个分数条
  Widget _buildScoreBar(String name, int score, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(
            width: 80,
            child: Text(
              name,
              style: const TextStyle(fontSize: 14),
            ),
          ),
          Expanded(
            child: LinearProgressIndicator(
              value: score / 100,
              backgroundColor: Colors.grey.withAlpha(30),
              valueColor: AlwaysStoppedAnimation<Color>(color),
              minHeight: 8,
              borderRadius: BorderRadius.circular(4),
            ),
          ),
          const SizedBox(width: 8),
          Text(
            '$score',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
  
  /// 获取体质类型名称
  String _getConstitutionTypeName(ConstitutionType type) {
    switch (type) {
      case ConstitutionType.balanced:
        return '平和体质';
      case ConstitutionType.qiDeficiency:
        return '气虚体质';
      case ConstitutionType.yangDeficiency:
        return '阳虚体质';
      case ConstitutionType.yinDeficiency:
        return '阴虚体质';
      case ConstitutionType.phlegmDampness:
        return '痰湿体质';
      case ConstitutionType.dampnessHeat:
        return '湿热体质';
      case ConstitutionType.bloodStasis:
        return '血瘀体质';
      case ConstitutionType.qiStagnation:
        return '气郁体质';
      case ConstitutionType.specialConstitution:
        return '特禀体质';
    }
  }
  
  /// 获取体质类型对应的颜色
  Color _getConstitutionTypeColor(ConstitutionType type) {
    switch (type) {
      case ConstitutionType.balanced:
        return AppColors.balancedTypeColor;
      case ConstitutionType.qiDeficiency:
        return AppColors.qiDeficiencyTypeColor;
      case ConstitutionType.yangDeficiency:
        return AppColors.yangDeficiencyTypeColor;
      case ConstitutionType.yinDeficiency:
        return AppColors.yinDeficiencyTypeColor;
      case ConstitutionType.phlegmDampness:
        return AppColors.phlegmDampnessTypeColor;
      case ConstitutionType.dampnessHeat:
        return AppColors.dampnessHeatTypeColor;
      case ConstitutionType.bloodStasis:
        return AppColors.bloodStasisTypeColor;
      case ConstitutionType.qiStagnation:
        return AppColors.qiStagnationTypeColor;
      case ConstitutionType.specialConstitution:
        return AppColors.specialTypeColor;
    }
  }
} 