import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/domain/entities/constitution_type.dart';
import 'package:suoke_life/domain/repositories/constitution_repository.dart';
import 'package:suoke_life/domain/usecases/get_user_constitution.dart';
import 'package:suoke_life/presentation/life/widgets/health/constitution_result_card.dart';

/// 体质测评页面
///
/// 展示用户体质测评结果和提供体质测评功能
class ConstitutionAssessmentView extends ConsumerStatefulWidget {
  /// 用户ID
  final String userId;
  
  /// 创建体质测评页面
  const ConstitutionAssessmentView({
    Key? key, 
    required this.userId,
  }) : super(key: key);

  @override
  ConsumerState<ConstitutionAssessmentView> createState() => _ConstitutionAssessmentViewState();
}

class _ConstitutionAssessmentViewState extends ConsumerState<ConstitutionAssessmentView> {
  /// 是否正在加载
  bool _isLoading = true;
  
  /// 是否存在结果
  bool _hasResult = false;
  
  /// 用户最新体质测评结果
  ConstitutionTypeResult? _latestResult;
  
  /// 历史测评结果
  List<ConstitutionTypeResult> _historyResults = [];
  
  @override
  void initState() {
    super.initState();
    _loadData();
  }
  
  /// 加载数据
  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
    });
    
    try {
      final useCase = ref.read(getUserConstitutionUseCaseProvider);
      
      // 获取最新结果
      final latestResult = await useCase.getLatestResult(widget.userId);
      
      // 如果有最新结果，获取历史记录
      List<ConstitutionTypeResult> historyResults = [];
      if (latestResult != null) {
        historyResults = await useCase.getHistory(widget.userId);
      }
      
      setState(() {
        _latestResult = latestResult;
        _hasResult = latestResult != null;
        _historyResults = historyResults;
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
          content: Text('加载体质测评数据失败: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('体质测评'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
            tooltip: '刷新',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildContent(),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _startNewAssessment,
        icon: const Icon(Icons.add),
        label: const Text('开始测评'),
        backgroundColor: AppColors.primary,
      ),
    );
  }
  
  /// 构建页面内容
  Widget _buildContent() {
    if (!_hasResult) {
      return _buildEmptyState();
    }
    
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 最新测评结果
          if (_latestResult != null) ...[
            const Text(
              '最近测评结果',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            ConstitutionResultCard(
              result: _latestResult!,
              onTap: () => _navigateToResultDetails(_latestResult!),
            ),
          ],
          
          // 历史测评记录
          if (_historyResults.length > 1) ...[
            const SizedBox(height: 24),
            const Text(
              '历史测评记录',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            ...List.generate(
              _historyResults.length - 1, // 不包括最新的结果
              (index) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: ConstitutionResultCard(
                  result: _historyResults[index + 1], // 跳过最新结果
                  onTap: () => _navigateToResultDetails(_historyResults[index + 1]),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
  
  /// 构建空状态提示
  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.account_circle,
            size: 100,
            color: Colors.grey.withAlpha(100),
          ),
          const SizedBox(height: 16),
          const Text(
            '还没有体质测评记录',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            '点击下方按钮开始您的中医体质测评',
            style: TextStyle(
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: _startNewAssessment,
            child: const Text('立即测评'),
          ),
        ],
      ),
    );
  }
  
  /// 开始新的体质测评
  void _startNewAssessment() {
    // TODO: 实现跳转到体质测评问卷页面
    // Navigator.of(context).push(
    //   MaterialPageRoute(
    //     builder: (context) => ConstitutionQuestionnaireView(userId: widget.userId),
    //   ),
    // );
    
    // 临时显示提示
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('体质测评问卷功能开发中...'),
      ),
    );
  }
  
  /// 跳转到结果详情页面
  void _navigateToResultDetails(ConstitutionTypeResult result) {
    // TODO: 实现跳转到体质测评结果详情页面
    // Navigator.of(context).push(
    //   MaterialPageRoute(
    //     builder: (context) => ConstitutionResultDetailsView(result: result),
    //   ),
    // );
    
    // 临时显示提示
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('体质测评结果详情页面开发中...'),
      ),
    );
  }
} 