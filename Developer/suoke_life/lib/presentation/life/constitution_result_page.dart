import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/domain/entities/constitution_data.dart';
import 'package:suoke_life/domain/entities/constitution_type.dart';
import 'package:suoke_life/presentation/common/widgets/custom_app_bar.dart';

@RoutePage()
class ConstitutionResultPage extends ConsumerWidget {
  final ConstitutionData constitutionData;

  const ConstitutionResultPage({
    Key? key,
    required this.constitutionData,
  }) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final primaryType = constitutionData.primaryType;
    if (primaryType == null) {
      return const Scaffold(
        body: Center(
          child: Text('未找到体质数据'),
        ),
      );
    }

    return Scaffold(
      appBar: const CustomAppBar(
        title: Text('体质辨识结果'),
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 主体质卡片
            _buildMainConstitutionCard(context, primaryType),

            // 体质综合评分
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Text(
                '体质评分详情',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
            ),

            // 体质评分列表
            _buildConstitutionScoreList(context),

            // 体质相关知识板块
            _buildConstitutionKnowledgeSection(context),

            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  // 构建主体质卡片
  Widget _buildMainConstitutionCard(
      BuildContext context, ConstitutionType type) {
    return Container(
      margin: const EdgeInsets.all(16.0),
      decoration: BoxDecoration(
        color: _getConstitutionColor(type).withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16.0),
            decoration: BoxDecoration(
              color: _getConstitutionColor(type),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(16),
                topRight: Radius.circular(16),
              ),
            ),
            child: Column(
              children: [
                Text(
                  '您的主体质类型',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: Colors.white,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  type.name,
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 4),
                Text(
                  '得分: ${constitutionData.getScoreForType(type).toInt()}',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        color: Colors.white70,
                      ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '主要特征',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  _getConstitutionDescription(type),
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                const SizedBox(height: 16),
                const Divider(),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        icon: const Icon(Icons.search),
                        label: const Text('查询调理方法'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _getConstitutionColor(type),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 12),
                        ),
                        onPressed: () {
                          context.router.push(
                            RagSearchRoute(
                              initialQuery: '${type.name}体质如何调理',
                              searchType: 'constitution',
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // 构建体质评分列表
  Widget _buildConstitutionScoreList(BuildContext context) {
    // 按分数降序排列
    final sortedTypes = ConstitutionType.values.toList()
      ..sort((a, b) => constitutionData
          .getScoreForType(b)
          .compareTo(constitutionData.getScoreForType(a)));

    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      itemCount: sortedTypes.length,
      itemBuilder: (context, index) {
        final type = sortedTypes[index];
        final score = constitutionData.getScoreForType(type);

        return Card(
          margin: const EdgeInsets.only(bottom: 8.0),
          child: Padding(
            padding: const EdgeInsets.all(12.0),
            child: Row(
              children: [
                Container(
                  width: 8,
                  height: 36,
                  decoration: BoxDecoration(
                    color: _getConstitutionColor(type),
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  type.name,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const Spacer(),
                Text(
                  '${score.toInt()}',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        color: _getScoreColor(score),
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  // 构建体质相关知识板块
  Widget _buildConstitutionKnowledgeSection(BuildContext context) {
    final primaryType = constitutionData.primaryType!;

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${primaryType.name}体质相关知识',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 16),
          _buildKnowledgeCard(
            context,
            title: '饮食调养',
            icon: Icons.restaurant,
            onTap: () {
              context.router.push(
                RagSearchRoute(
                  initialQuery: '${primaryType.name}体质饮食调养',
                  searchType: 'regimen',
                ),
              );
            },
          ),
          const SizedBox(height: 12),
          _buildKnowledgeCard(
            context,
            title: '运动调养',
            icon: Icons.directions_run,
            onTap: () {
              context.router.push(
                RagSearchRoute(
                  initialQuery: '${primaryType.name}体质适合的运动',
                  searchType: 'regimen',
                ),
              );
            },
          ),
          const SizedBox(height: 12),
          _buildKnowledgeCard(
            context,
            title: '情志调养',
            icon: Icons.mood,
            onTap: () {
              context.router.push(
                RagSearchRoute(
                  initialQuery: '${primaryType.name}体质情志调养',
                  searchType: 'regimen',
                ),
              );
            },
          ),
          const SizedBox(height: 12),
          _buildKnowledgeCard(
            context,
            title: '穴位按摩',
            icon: Icons.healing,
            onTap: () {
              context.router.push(
                RagSearchRoute(
                  initialQuery: '${primaryType.name}体质适合按摩的穴位',
                  searchType: 'meridians',
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  // 构建知识卡片
  Widget _buildKnowledgeCard(
    BuildContext context, {
    required String title,
    required IconData icon,
    required VoidCallback onTap,
  }) {
    return Card(
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: [
              Icon(
                icon,
                size: 28,
                color: AppColors.brandPrimary,
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ),
              const Icon(Icons.arrow_forward_ios, size: 16),
            ],
          ),
        ),
      ),
    );
  }

  // 获取体质颜色
  Color _getConstitutionColor(ConstitutionType type) {
    switch (type) {
      case ConstitutionType.balanced:
        return Colors.green[700]!;
      case ConstitutionType.qiDeficient:
        return Colors.orange[700]!;
      case ConstitutionType.yangDeficient:
        return Colors.blue[700]!;
      case ConstitutionType.yinDeficient:
        return Colors.red[700]!;
      case ConstitutionType.phlegmDamp:
        return Colors.teal[700]!;
      case ConstitutionType.dampHeat:
        return Colors.deepOrange[700]!;
      case ConstitutionType.bloodStasis:
        return Colors.purple[700]!;
      case ConstitutionType.qiStagnation:
        return Colors.indigo[700]!;
      case ConstitutionType.specialConstitution:
        return Colors.grey[700]!;
    }
  }

  // 获取分数颜色
  Color _getScoreColor(double score) {
    if (score >= 80) return Colors.red;
    if (score >= 60) return Colors.orange;
    if (score >= 40) return Colors.green;
    return Colors.blue;
  }

  // 获取体质描述
  String _getConstitutionDescription(ConstitutionType type) {
    switch (type) {
      case ConstitutionType.balanced:
        return '平和体质是人体阴阳气血调和、脏腑功能正常的一种体质状态。表现为精力充沛、面色红润、适应能力强、不易生病。';
      case ConstitutionType.qiDeficient:
        return '气虚体质的人表现为气短乏力、易出汗、声音低弱、易疲劳，常感到精神不振，易患感冒等疾病。';
      case ConstitutionType.yangDeficient:
        return '阳虚体质的人表现为怕冷、手脚冰凉、面色苍白、大便溏薄，易患风寒感冒、哮喘、脾胃功能紊乱等疾病。';
      case ConstitutionType.yinDeficient:
        return '阴虚体质的人表现为手足心热、口干舌燥、眼睛干涩、失眠多梦，易患口腔溃疡、咽喉炎、皮肤瘙痒等疾病。';
      case ConstitutionType.phlegmDamp:
        return '痰湿体质的人表现为体形肥胖、胸闷多痰、口黏腻、大便黏腻不畅，易患高脂血症、高血压、糖尿病等疾病。';
      case ConstitutionType.dampHeat:
        return '湿热体质的人表现为面垢油光、口苦黏腻、大便黏滞不畅、小便黄浊，易患痤疮、口腔炎症、结膜炎等疾病。';
      case ConstitutionType.bloodStasis:
        return '血瘀体质的人表现为面色晦暗、唇色紫暗、肌肤粗糙、口唇干、舌质紫暗有瘀点，易患冠心病、痛经、静脉曲张等疾病。';
      case ConstitutionType.qiStagnation:
        return '气郁体质的人表现为情绪不稳定、易紧张焦虑、烦闷不乐、胸胁胀闷、常无缘无故地叹气，易患神经衰弱、抑郁症等疾病。';
      case ConstitutionType.specialConstitution:
        return '特禀体质的人表现为特殊反应性强，对药物、食物、气味等特定物质过敏，易患哮喘、荨麻疹、过敏性鼻炎等疾病。';
    }
  }
}
