import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/domain/entities/constitution_type.dart';
import 'package:suoke_life/domain/usecases/get_user_constitution.dart';
import 'package:suoke_life/domain/usecases/generate_health_regimen_usecase.dart';

/// 体质类型详情页面
///
/// 展示特定体质类型的详细信息、特征和调理建议
class ConstitutionTypeDetailView extends ConsumerStatefulWidget {
  /// 体质类型
  final ConstitutionType constitutionType;
  
  /// 用户ID，可选（如果提供，则可以生成个性化的调理方案）
  final String? userId;
  
  /// 创建体质类型详情页面
  const ConstitutionTypeDetailView({
    Key? key,
    required this.constitutionType,
    this.userId,
  }) : super(key: key);

  @override
  ConsumerState<ConstitutionTypeDetailView> createState() => _ConstitutionTypeDetailViewState();
}

class _ConstitutionTypeDetailViewState extends ConsumerState<ConstitutionTypeDetailView> with SingleTickerProviderStateMixin {
  /// 是否正在加载
  bool _isLoading = true;
  
  /// 体质特征
  ConstitutionTraits? _traits;
  
  /// 适宜食物
  List<String> _suitableFoods = [];
  
  /// 不适宜食物
  List<String> _unsuitableFoods = [];
  
  /// 标签控制器
  late TabController _tabController;
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadData();
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }
  
  /// 加载数据
  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
    });
    
    try {
      final getUserConstitutionUseCase = ref.read(getUserConstitutionUseCaseProvider);
      
      // 获取体质特征
      final traits = await getUserConstitutionUseCase.getTraits(widget.constitutionType);
      
      // 获取适宜食物
      final suitableFoods = await getUserConstitutionUseCase.getSuitableFoods(widget.constitutionType);
      
      // 获取不适宜食物
      final unsuitableFoods = await getUserConstitutionUseCase.getUnsuitableFoods(widget.constitutionType);
      
      setState(() {
        _traits = traits;
        _suitableFoods = suitableFoods;
        _unsuitableFoods = unsuitableFoods;
        _isLoading = false;
      });
    } catch (e) {
      // 处理错误
      setState(() {
        _isLoading = false;
      });
      
      // 显示错误提示
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('加载体质类型详情失败: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
  
  @override
  Widget build(BuildContext context) {
    final typeColor = _getConstitutionTypeColor(widget.constitutionType);
    final typeName = _getConstitutionTypeName(widget.constitutionType);
    
    return Scaffold(
      appBar: AppBar(
        title: Text(typeName),
        backgroundColor: typeColor.withAlpha(50),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: typeColor,
          labelColor: typeColor,
          tabs: const [
            Tab(text: '基本特征'),
            Tab(text: '调理建议'),
            Tab(text: '食物指南'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildContent(typeColor),
      floatingActionButton: widget.userId != null
          ? FloatingActionButton.extended(
              onPressed: _generateRegimen,
              icon: const Icon(Icons.add_chart),
              label: const Text('生成调理方案'),
              backgroundColor: typeColor,
            )
          : null,
    );
  }
  
  /// 构建页面内容
  Widget _buildContent(Color typeColor) {
    if (_traits == null) {
      return const Center(
        child: Text('未找到体质类型信息'),
      );
    }
    
    return TabBarView(
      controller: _tabController,
      children: [
        // 基本特征
        _buildBasicInfoTab(typeColor),
        
        // 调理建议
        _buildSuggestionsTab(typeColor),
        
        // 食物指南
        _buildFoodGuideTab(typeColor),
      ],
    );
  }
  
  /// 构建基本特征标签页
  Widget _buildBasicInfoTab(Color typeColor) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 体质描述
          _buildSection(
            title: '体质描述',
            content: _traits!.description,
            icon: Icons.info_outline,
            color: typeColor,
          ),
          
          const SizedBox(height: 24),
          
          // 主要特征
          _buildSection(
            title: '主要特征',
            content: '',
            icon: Icons.checklist,
            color: typeColor,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: _traits!.mainFeatures.map((feature) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        Icons.fiber_manual_record,
                        size: 12,
                        color: typeColor,
                      ),
                      const SizedBox(width: 8),
                      Expanded(child: Text(feature)),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
          
          const SizedBox(height: 24),
          
          // 相关疾病风险
          _buildSection(
            title: '相关疾病风险',
            content: '',
            icon: Icons.medical_services_outlined,
            color: typeColor,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: _traits!.relatedDiseaseRisks.map((risk) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        Icons.warning_amber_outlined,
                        size: 16,
                        color: Colors.amber,
                      ),
                      const SizedBox(width: 8),
                      Expanded(child: Text(risk)),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
          
          const SizedBox(height: 24),
          
          // 诊断要点
          _buildSection(
            title: '诊断要点',
            content: '',
            icon: Icons.assignment,
            color: typeColor,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: _traits!.diagnosticPoints.map((point) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        Icons.check_circle_outline,
                        size: 16,
                        color: typeColor,
                      ),
                      const SizedBox(width: 8),
                      Expanded(child: Text(point)),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }
  
  /// 构建调理建议标签页
  Widget _buildSuggestionsTab(Color typeColor) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 调理原则
          _buildSection(
            title: '调理原则',
            content: _traits!.regulationPrinciple,
            icon: Icons.healing,
            color: typeColor,
          ),
          
          const SizedBox(height: 24),
          
          // 饮食建议
          _buildSection(
            title: '饮食建议',
            content: '',
            icon: Icons.restaurant,
            color: typeColor,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: _traits!.dietarySuggestions.map((suggestion) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        Icons.arrow_right,
                        size: 16,
                        color: typeColor,
                      ),
                      const SizedBox(width: 8),
                      Expanded(child: Text(suggestion)),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
          
          const SizedBox(height: 24),
          
          // 生活习惯建议
          _buildSection(
            title: '生活习惯建议',
            content: '',
            icon: Icons.home,
            color: typeColor,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: _traits!.lifestyleSuggestions.map((suggestion) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        Icons.arrow_right,
                        size: 16,
                        color: typeColor,
                      ),
                      const SizedBox(width: 8),
                      Expanded(child: Text(suggestion)),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
          
          const SizedBox(height: 24),
          
          // 心理调节建议
          _buildSection(
            title: '心理调节建议',
            content: '',
            icon: Icons.psychology,
            color: typeColor,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: _traits!.psychologicalSuggestions.map((suggestion) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        Icons.arrow_right,
                        size: 16,
                        color: typeColor,
                      ),
                      const SizedBox(width: 8),
                      Expanded(child: Text(suggestion)),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
          
          const SizedBox(height: 24),
          
          // 运动建议
          _buildSection(
            title: '运动建议',
            content: '',
            icon: Icons.directions_run,
            color: typeColor,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: _traits!.exerciseSuggestions.map((suggestion) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        Icons.arrow_right,
                        size: 16,
                        color: typeColor,
                      ),
                      const SizedBox(width: 8),
                      Expanded(child: Text(suggestion)),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }
  
  /// 构建食物指南标签页
  Widget _buildFoodGuideTab(Color typeColor) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 适宜食物
          _buildSection(
            title: '适宜食物',
            content: '',
            icon: Icons.thumb_up,
            color: Colors.green,
            child: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _suitableFoods.map((food) {
                return Chip(
                  label: Text(food),
                  backgroundColor: Colors.green.withAlpha(30),
                  side: BorderSide(color: Colors.green.withAlpha(100)),
                );
              }).toList(),
            ),
          ),
          
          const SizedBox(height: 24),
          
          // 不适宜食物
          _buildSection(
            title: '不适宜食物',
            content: '',
            icon: Icons.thumb_down,
            color: Colors.red,
            child: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _unsuitableFoods.map((food) {
                return Chip(
                  label: Text(food),
                  backgroundColor: Colors.red.withAlpha(30),
                  side: BorderSide(color: Colors.red.withAlpha(100)),
                );
              }).toList(),
            ),
          ),
          
          const SizedBox(height: 24),
          
          // 饮食原则
          _buildSection(
            title: '饮食原则',
            content: '根据本体质特点，饮食应遵循"${_getConstitutionFoodPrinciple(widget.constitutionType)}"的原则。',
            icon: Icons.food_bank,
            color: typeColor,
          ),
        ],
      ),
    );
  }
  
  /// 构建部分
  Widget _buildSection({
    required String title,
    required String content,
    required IconData icon,
    required Color color,
    Widget? child,
  }) {
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: color.withAlpha(50)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  icon,
                  color: color,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (content.isNotEmpty) Text(content),
            if (child != null) child,
          ],
        ),
      ),
    );
  }
  
  /// 生成调理方案
  void _generateRegimen() async {
    if (widget.userId == null) return;
    
    try {
      final generateRegimenUseCase = ref.read(generateHealthRegimenUseCaseProvider);
      
      // 显示加载对话框
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => const AlertDialog(
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text('正在生成个性化调理方案...'),
            ],
          ),
        ),
      );
      
      // 生成调理方案
      final regimen = await generateRegimenUseCase.generateByConstitution(
        widget.userId!,
        widget.constitutionType,
      );
      
      // 关闭加载对话框
      Navigator.of(context).pop();
      
      // 跳转到调理方案详情页
      // Navigator.of(context).push(
      //   MaterialPageRoute(
      //     builder: (context) => HealthRegimenDetailView(regimenId: regimen.id),
      //   ),
      // );
      
      // 临时显示提示
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('调理方案已生成，请前往调理方案页面查看')),
      );
    } catch (e) {
      // 关闭加载对话框
      Navigator.of(context).pop();
      
      // 显示错误提示
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('生成调理方案失败: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
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
  
  /// 获取体质饮食原则
  String _getConstitutionFoodPrinciple(ConstitutionType type) {
    switch (type) {
      case ConstitutionType.balanced:
        return '均衡饮食，四季有常';
      case ConstitutionType.qiDeficiency:
        return '温补益气，滋养脾胃';
      case ConstitutionType.yangDeficiency:
        return '温补阳气，避寒就温';
      case ConstitutionType.yinDeficiency:
        return '滋阴润燥，清热养阴';
      case ConstitutionType.phlegmDampness:
        return '健脾利湿，化痰消滞';
      case ConstitutionType.dampnessHeat:
        return '清热利湿，清淡醒脾';
      case ConstitutionType.bloodStasis:
        return '活血化瘀，温通经络';
      case ConstitutionType.qiStagnation:
        return '疏肝解郁，理气和胃';
      case ConstitutionType.specialConstitution:
        return '辨证施膳，避免过敏';
    }
  }
} 