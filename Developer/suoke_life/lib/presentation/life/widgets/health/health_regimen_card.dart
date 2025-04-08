import 'package:flutter/material.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/domain/entities/constitution_type.dart';
import 'package:suoke_life/domain/entities/health_regimen.dart';
import 'package:intl/intl.dart';

/// 健康调理方案卡片
///
/// 展示健康调理方案的基本信息，包括体质类型、诊断结论、调理原则等
class HealthRegimenCard extends StatelessWidget {
  /// 健康调理方案
  final HealthRegimen regimen;
  
  /// 点击回调
  final VoidCallback? onTap;
  
  /// 是否显示详细信息
  final bool showDetails;
  
  /// 创建健康调理方案卡片
  const HealthRegimenCard({
    Key? key,
    required this.regimen,
    this.onTap,
    this.showDetails = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final dateFormatter = DateFormat('yyyy年MM月dd日');
    
    final formattedDate = dateFormatter.format(regimen.createdTime);
    
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
                    '健康调理方案',
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
              
              // 体质类型
              _buildConstitutionType(theme),
              
              const SizedBox(height: 16),
              
              // 诊断结论
              Text(
                '诊断结论',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                regimen.diagnosis,
                style: theme.textTheme.bodyMedium,
                maxLines: showDetails ? null : 2,
                overflow: showDetails ? null : TextOverflow.ellipsis,
              ),
              
              const SizedBox(height: 16),
              
              // 调理原则
              Text(
                '调理原则',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                regimen.regimenPrinciple,
                style: theme.textTheme.bodyMedium,
                maxLines: showDetails ? null : 3,
                overflow: showDetails ? null : TextOverflow.ellipsis,
              ),
              
              // 详细调理建议
              if (showDetails) ...[
                const SizedBox(height: 16),
                _buildDetailedSuggestions(theme),
              ],
              
              // 操作按钮
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  if (!showDetails)
                    OutlinedButton(
                      onPressed: onTap,
                      child: const Text('查看详情'),
                    )
                  else ...[
                    OutlinedButton(
                      onPressed: () {
                        // TODO: 实现反馈功能
                      },
                      child: const Text('提供反馈'),
                    ),
                    const SizedBox(width: 12),
                    ElevatedButton(
                      onPressed: () {
                        // TODO: 实现保存功能
                      },
                      child: const Text('保存方案'),
                    ),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  /// 构建体质类型显示
  Widget _buildConstitutionType(ThemeData theme) {
    final typeName = _getConstitutionTypeName(regimen.constitutionType);
    final typeColor = _getConstitutionTypeColor(regimen.constitutionType);
    
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
            '体质类型: $typeName',
            style: theme.textTheme.titleMedium?.copyWith(
              color: typeColor,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
  
  /// 构建详细调理建议
  Widget _buildDetailedSuggestions(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 饮食调理
        _buildSectionHeader('饮食调理', Icons.restaurant, theme),
        const SizedBox(height: 8),
        _buildSectionItem('调理原则', regimen.dietary.principle, theme),
        const SizedBox(height: 4),
        _buildSectionItem('推荐食物', regimen.dietary.recommendedFoods.join('、'), theme),
        const SizedBox(height: 4),
        _buildSectionItem('限制食物', regimen.dietary.restrictedFoods.join('、'), theme),
        const SizedBox(height: 4),
        _buildSectionItem('禁忌食物', regimen.dietary.forbiddenFoods.join('、'), theme),
        
        const SizedBox(height: 16),
        
        // 情志调理
        _buildSectionHeader('情志调理', Icons.psychology, theme),
        const SizedBox(height: 8),
        _buildSectionItem('调理原则', regimen.emotional.principle, theme),
        const SizedBox(height: 4),
        _buildSectionItem('情绪风险', regimen.emotional.emotionalRisks.join('、'), theme),
        const SizedBox(height: 4),
        _buildSectionItem('调理建议', regimen.emotional.suggestions.join('、'), theme),
        
        const SizedBox(height: 16),
        
        // 起居调理
        _buildSectionHeader('起居调理', Icons.hotel, theme),
        const SizedBox(height: 8),
        _buildSectionItem('调理原则', regimen.lifestyle.principle, theme),
        const SizedBox(height: 4),
        _buildSectionItem('作息建议', regimen.lifestyle.schedule, theme),
        const SizedBox(height: 4),
        _buildSectionItem('睡眠建议', regimen.lifestyle.sleepSuggestions.join('、'), theme),
        
        const SizedBox(height: 16),
        
        // 运动调理
        _buildSectionHeader('运动调理', Icons.directions_run, theme),
        const SizedBox(height: 8),
        _buildSectionItem('调理原则', regimen.exercise.principle, theme),
        const SizedBox(height: 4),
        _buildSectionItem('推荐运动', regimen.exercise.recommendedExercises.join('、'), theme),
        const SizedBox(height: 4),
        _buildSectionItem('运动强度', regimen.exercise.intensity, theme),
        const SizedBox(height: 4),
        _buildSectionItem('运动频率', regimen.exercise.frequency, theme),
        
        // 穴位保健
        if (regimen.acupoint != null) ...[
          const SizedBox(height: 16),
          _buildSectionHeader('穴位保健', Icons.touch_app, theme),
          const SizedBox(height: 8),
          _buildSectionItem('调理原则', regimen.acupoint!.principle, theme),
          const SizedBox(height: 4),
          _buildSectionItem('推荐穴位', regimen.acupoint!.recommendations.map((e) => e.name).join('、'), theme),
        ],
        
        // 中药调理
        if (regimen.herbal != null) ...[
          const SizedBox(height: 16),
          _buildSectionHeader('中药调理', Icons.healing, theme),
          const SizedBox(height: 8),
          _buildSectionItem('调理原则', regimen.herbal!.principle, theme),
          const SizedBox(height: 4),
          _buildSectionItem('推荐方剂', regimen.herbal!.formulas.map((e) => e.name).join('、'), theme),
        ],
      ],
    );
  }
  
  /// 构建小节标题
  Widget _buildSectionHeader(String title, IconData icon, ThemeData theme) {
    return Row(
      children: [
        Icon(
          icon,
          color: AppColors.primary,
          size: 18,
        ),
        const SizedBox(width: 8),
        Text(
          title,
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: AppColors.primary,
          ),
        ),
      ],
    );
  }
  
  /// 构建项目内容
  Widget _buildSectionItem(String label, String content, ThemeData theme) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 80,
          child: Text(
            label,
            style: theme.textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        Expanded(
          child: Text(
            content,
            style: theme.textTheme.bodyMedium,
          ),
        ),
      ],
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