import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/domain/entities/health_regimen.dart';
import 'package:suoke_life/domain/usecases/manage_health_regimen_usecase.dart';
import 'package:suoke_life/presentation/life/widgets/health/health_regimen_card.dart';

/// 健康调理方案详情页面
///
/// 展示健康调理方案的详细信息
class HealthRegimenDetailView extends ConsumerStatefulWidget {
  /// 方案ID
  final String regimenId;
  
  /// 创建健康调理方案详情页面
  const HealthRegimenDetailView({
    Key? key,
    required this.regimenId,
  }) : super(key: key);

  @override
  ConsumerState<HealthRegimenDetailView> createState() => _HealthRegimenDetailViewState();
}

class _HealthRegimenDetailViewState extends ConsumerState<HealthRegimenDetailView> {
  /// 是否正在加载
  bool _isLoading = true;
  
  /// 健康调理方案
  HealthRegimen? _regimen;
  
  /// 用户反馈内容
  final TextEditingController _feedbackController = TextEditingController();
  
  /// 用户评分
  int _rating = 5;
  
  @override
  void initState() {
    super.initState();
    _loadData();
  }
  
  @override
  void dispose() {
    _feedbackController.dispose();
    super.dispose();
  }
  
  /// 加载数据
  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
    });
    
    try {
      final useCase = ref.read(manageHealthRegimenUseCaseProvider);
      final regimen = await useCase.getRegimenById(widget.regimenId);
      
      setState(() {
        _regimen = regimen;
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
          content: Text('加载调理方案失败: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('调理方案详情'),
        actions: [
          PopupMenuButton<String>(
            onSelected: _handleMenuAction,
            itemBuilder: (BuildContext context) {
              return [
                const PopupMenuItem<String>(
                  value: 'share',
                  child: Row(
                    children: [
                      Icon(Icons.share, size: 20),
                      SizedBox(width: 8),
                      Text('分享方案'),
                    ],
                  ),
                ),
                const PopupMenuItem<String>(
                  value: 'download',
                  child: Row(
                    children: [
                      Icon(Icons.download, size: 20),
                      SizedBox(width: 8),
                      Text('下载方案'),
                    ],
                  ),
                ),
                const PopupMenuItem<String>(
                  value: 'feedback',
                  child: Row(
                    children: [
                      Icon(Icons.feedback, size: 20),
                      SizedBox(width: 8),
                      Text('提供反馈'),
                    ],
                  ),
                ),
              ];
            },
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildContent(),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _createRegimenAdherencePlan,
        icon: const Icon(Icons.calendar_today),
        label: const Text('制定执行计划'),
        backgroundColor: AppColors.primary,
      ),
    );
  }
  
  /// 处理菜单操作
  void _handleMenuAction(String action) {
    switch (action) {
      case 'share':
        _shareRegimen();
        break;
      case 'download':
        _downloadRegimen();
        break;
      case 'feedback':
        _showFeedbackDialog();
        break;
    }
  }
  
  /// 构建页面内容
  Widget _buildContent() {
    if (_regimen == null) {
      return const Center(
        child: Text('未找到调理方案'),
      );
    }
    
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 健康调理方案卡片（显示详细信息）
          HealthRegimenCard(
            regimen: _regimen!,
            showDetails: true,
          ),
          
          const SizedBox(height: 24),
          
          // 执行情况
          _buildAdherenceSection(),
          
          const SizedBox(height: 32),
        ],
      ),
    );
  }
  
  /// 构建执行情况部分
  Widget _buildAdherenceSection() {
    return Card(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.insights,
                  color: AppColors.primary,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  '执行情况',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppColors.primary,
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // 暂时用静态内容代替
            const Text('尚未开始执行此调理方案'),
            const SizedBox(height: 8),
            OutlinedButton(
              onPressed: _createRegimenAdherencePlan,
              child: const Text('开始执行'),
            ),
          ],
        ),
      ),
    );
  }
  
  /// 分享调理方案
  void _shareRegimen() {
    // TODO: 实现分享功能
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('分享功能开发中...')),
    );
  }
  
  /// 下载调理方案
  void _downloadRegimen() {
    // TODO: 实现下载功能
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('下载功能开发中...')),
    );
  }
  
  /// 制定执行计划
  void _createRegimenAdherencePlan() {
    // TODO: 实现跳转到执行计划制定页面
    // Navigator.of(context).push(
    //   MaterialPageRoute(
    //     builder: (context) => RegimenAdherencePlanView(regimen: _regimen!),
    //   ),
    // );
    
    // 临时显示提示
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('执行计划功能开发中...')),
    );
  }
  
  /// 显示反馈对话框
  void _showFeedbackDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('方案反馈'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('请对此调理方案进行评分：'),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(5, (index) {
                  final starIndex = index + 1;
                  return IconButton(
                    icon: Icon(
                      starIndex <= _rating ? Icons.star : Icons.star_border,
                      color: starIndex <= _rating ? Colors.amber : Colors.grey,
                    ),
                    onPressed: () {
                      setState(() {
                        _rating = starIndex;
                      });
                    },
                  );
                }),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _feedbackController,
                decoration: const InputDecoration(
                  hintText: '请输入您的反馈意见',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: const Text('取消'),
            ),
            ElevatedButton(
              onPressed: () {
                _submitFeedback();
                Navigator.of(context).pop();
              },
              child: const Text('提交'),
            ),
          ],
        );
      },
    );
  }
  
  /// 提交反馈
  Future<void> _submitFeedback() async {
    if (_regimen == null) return;
    
    final feedback = _feedbackController.text.trim();
    if (feedback.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请输入反馈内容')),
      );
      return;
    }
    
    try {
      final useCase = ref.read(manageHealthRegimenUseCaseProvider);
      await useCase.saveRegimenFeedback(_regimen!.id, feedback, _rating);
      
      // 清空输入
      _feedbackController.clear();
      
      // 显示成功提示
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('感谢您的反馈！')),
      );
    } catch (e) {
      // 显示错误提示
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('提交反馈失败: $e')),
      );
    }
  }
} 