import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/domain/entities/constitution_type.dart';
import 'package:suoke_life/domain/entities/constitution_type_result.dart';
import 'package:suoke_life/domain/usecases/get_user_constitution.dart';

/// 体质评估问卷页面
///
/// 用于展示体质评估问卷并收集用户回答
class ConstitutionAssessmentQuestionnaireView extends ConsumerStatefulWidget {
  /// 用户ID
  final String userId;
  
  /// 评估ID
  final String assessmentId;
  
  /// 创建体质评估问卷页面
  const ConstitutionAssessmentQuestionnaireView({
    Key? key,
    required this.userId,
    required this.assessmentId,
  }) : super(key: key);

  @override
  ConsumerState<ConstitutionAssessmentQuestionnaireView> createState() => _ConstitutionAssessmentQuestionnaireViewState();
}

class _ConstitutionAssessmentQuestionnaireViewState extends ConsumerState<ConstitutionAssessmentQuestionnaireView> {
  /// 问卷题目
  List<Map<String, dynamic>> _questions = [];
  
  /// 回答（问题ID : 回答值）
  Map<String, dynamic> _answers = {};
  
  /// 当前页面索引
  int _currentPageIndex = 0;
  
  /// 是否正在加载
  bool _isLoading = true;
  
  /// 是否正在提交
  bool _isSubmitting = false;
  
  /// 页面控制器
  final PageController _pageController = PageController();
  
  @override
  void initState() {
    super.initState();
    _loadQuestions();
  }
  
  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }
  
  /// 加载问卷题目
  Future<void> _loadQuestions() async {
    setState(() {
      _isLoading = true;
    });
    
    try {
      final getUserConstitutionUseCase = ref.read(getUserConstitutionUseCaseProvider);
      final questions = await getUserConstitutionUseCase.getAssessmentQuestions();
      
      setState(() {
        _questions = questions;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      
      // 显示错误提示
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('加载问卷题目失败: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
  
  /// 提交问卷
  Future<void> _submitQuestionnaire() async {
    // 检查是否所有题目都已回答
    if (_questions.length != _answers.length) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('请回答所有问题'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }
    
    setState(() {
      _isSubmitting = true;
    });
    
    try {
      final getUserConstitutionUseCase = ref.read(getUserConstitutionUseCaseProvider);
      
      // 提交问卷答案
      await getUserConstitutionUseCase.submitAssessmentAnswers(
        widget.assessmentId,
        _answers,
      );
      
      // 获取评估结果
      final result = await getUserConstitutionUseCase.getAssessmentResult(widget.assessmentId);
      
      setState(() {
        _isSubmitting = false;
      });
      
      // 跳转到结果页面
      if (!mounted) return;
      
      // 导航到结果页面
      // Navigator.of(context).push(
      //   MaterialPageRoute(
      //     builder: (context) => ConstitutionAssessmentResultView(result: result),
      //   ),
      // );
      
      // 临时返回上一页
      Navigator.of(context).pop(result);
    } catch (e) {
      setState(() {
        _isSubmitting = false;
      });
      
      // 显示错误提示
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('提交问卷失败: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
  
  /// 设置答案
  void _setAnswer(String questionId, dynamic value) {
    setState(() {
      _answers[questionId] = value;
    });
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('中医体质评估问卷'),
        backgroundColor: AppColors.primary,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildQuestionnaireContent(),
    );
  }
  
  /// 构建问卷内容
  Widget _buildQuestionnaireContent() {
    return Column(
      children: [
        // 进度指示器
        LinearProgressIndicator(
          value: (_currentPageIndex + 1) / _questions.length,
          backgroundColor: Colors.grey.withAlpha(50),
          valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
          minHeight: 8,
        ),
        
        // 页面指示器
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Text(
            '问题 ${_currentPageIndex + 1}/${_questions.length}',
            style: const TextStyle(fontSize: 14, color: Colors.grey),
          ),
        ),
        
        // 问题内容
        Expanded(
          child: PageView.builder(
            controller: _pageController,
            itemCount: _questions.length,
            onPageChanged: (index) {
              setState(() {
                _currentPageIndex = index;
              });
            },
            itemBuilder: (context, index) {
              final question = _questions[index];
              return _buildQuestionItem(question);
            },
          ),
        ),
        
        // 底部按钮
        _buildBottomButtons(),
      ],
    );
  }
  
  /// 构建问题项
  Widget _buildQuestionItem(Map<String, dynamic> question) {
    final String questionId = question['id'];
    final String questionText = question['text'];
    final String questionType = question['type'];
    final List<dynamic> options = question['options'] ?? [];
    
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Card(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 问题标题
              Text(
                questionText,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              
              const SizedBox(height: 24),
              
              // 问题类型对应的输入控件
              if (questionType == 'single_choice') _buildSingleChoiceQuestion(questionId, options),
              if (questionType == 'multiple_choice') _buildMultipleChoiceQuestion(questionId, options),
              if (questionType == 'slider') _buildSliderQuestion(questionId, question),
              if (questionType == 'yes_no') _buildYesNoQuestion(questionId),
            ],
          ),
        ),
      ),
    );
  }
  
  /// 构建单选题
  Widget _buildSingleChoiceQuestion(String questionId, List<dynamic> options) {
    return Column(
      children: options.map((option) {
        return RadioListTile<String>(
          title: Text(option['text']),
          value: option['value'],
          groupValue: _answers[questionId],
          onChanged: (value) {
            _setAnswer(questionId, value);
          },
          activeColor: AppColors.primary,
        );
      }).toList(),
    );
  }
  
  /// 构建多选题
  Widget _buildMultipleChoiceQuestion(String questionId, List<dynamic> options) {
    // 确保答案是一个List
    if (_answers[questionId] == null) {
      _answers[questionId] = <String>[];
    }
    
    return Column(
      children: options.map((option) {
        final List<String> selectedValues = List<String>.from(_answers[questionId] ?? []);
        final bool isSelected = selectedValues.contains(option['value']);
        
        return CheckboxListTile(
          title: Text(option['text']),
          value: isSelected,
          onChanged: (bool? value) {
            if (value == true) {
              selectedValues.add(option['value']);
            } else {
              selectedValues.remove(option['value']);
            }
            _setAnswer(questionId, selectedValues);
          },
          activeColor: AppColors.primary,
        );
      }).toList(),
    );
  }
  
  /// 构建滑块题
  Widget _buildSliderQuestion(String questionId, Map<String, dynamic> question) {
    final double minValue = (question['min_value'] ?? 0).toDouble();
    final double maxValue = (question['max_value'] ?? 5).toDouble();
    final double step = (question['step'] ?? 1).toDouble();
    
    // 初始化答案
    if (_answers[questionId] == null) {
      _answers[questionId] = minValue;
    }
    
    return Column(
      children: [
        Slider(
          value: (_answers[questionId] ?? minValue).toDouble(),
          min: minValue,
          max: maxValue,
          divisions: ((maxValue - minValue) / step).round(),
          label: _answers[questionId]?.toString() ?? minValue.toString(),
          onChanged: (value) {
            _setAnswer(questionId, value);
          },
          activeColor: AppColors.primary,
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(minValue.toInt().toString()),
              Text(maxValue.toInt().toString()),
            ],
          ),
        ),
      ],
    );
  }
  
  /// 构建是非题
  Widget _buildYesNoQuestion(String questionId) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        ElevatedButton(
          onPressed: () => _setAnswer(questionId, true),
          style: ElevatedButton.styleFrom(
            backgroundColor: _answers[questionId] == true ? AppColors.primary : Colors.grey.withAlpha(50),
            foregroundColor: _answers[questionId] == true ? Colors.white : Colors.black,
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
          child: const Text('是'),
        ),
        const SizedBox(width: 32),
        ElevatedButton(
          onPressed: () => _setAnswer(questionId, false),
          style: ElevatedButton.styleFrom(
            backgroundColor: _answers[questionId] == false ? AppColors.secondary : Colors.grey.withAlpha(50),
            foregroundColor: _answers[questionId] == false ? Colors.white : Colors.black,
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
          child: const Text('否'),
        ),
      ],
    );
  }
  
  /// 构建底部按钮
  Widget _buildBottomButtons() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // 上一步按钮
          ElevatedButton(
            onPressed: _currentPageIndex > 0
                ? () {
                    _pageController.previousPage(
                      duration: const Duration(milliseconds: 300),
                      curve: Curves.easeInOut,
                    );
                  }
                : null,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.grey.withAlpha(50),
              foregroundColor: Colors.black,
            ),
            child: const Text('上一步'),
          ),
          
          // 下一步或提交按钮
          ElevatedButton(
            onPressed: _isSubmitting
                ? null
                : () {
                    if (_currentPageIndex < _questions.length - 1) {
                      _pageController.nextPage(
                        duration: const Duration(milliseconds: 300),
                        curve: Curves.easeInOut,
                      );
                    } else {
                      _submitQuestionnaire();
                    }
                  },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              foregroundColor: Colors.white,
            ),
            child: _isSubmitting
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  )
                : Text(_currentPageIndex < _questions.length - 1 ? '下一步' : '提交'),
          ),
        ],
      ),
    );
  }
} 