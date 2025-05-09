import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/models/inquiry_data_model.dart';
import 'package:suoke_life/presentation/life/view_models/diagnosis_view_model.dart';
import 'package:suoke_life/domain/models/diagnosis_session_model.dart';
import 'package:suoke_life/presentation/widgets/loading_overlay.dart';

/// 症状问诊页面
class SymptomsInquiryScreen extends ConsumerStatefulWidget {
  /// 会话ID
  final String? sessionId;

  /// 构造函数
  const SymptomsInquiryScreen({
    super.key,
    this.sessionId,
  });

  @override
  ConsumerState<SymptomsInquiryScreen> createState() => _SymptomsInquiryScreenState();
}

class _SymptomsInquiryScreenState extends ConsumerState<SymptomsInquiryScreen> {
  final _formKey = GlobalKey<FormState>();
  
  // 表单数据控制器
  final _mainSymptomsController = TextEditingController();
  final _secondarySymptomsController = TextEditingController();
  final _notesController = TextEditingController();
  final _waterIntakeController = TextEditingController();
  
  // 当前选择的值
  SymptomSeverity _selectedSeverity = SymptomSeverity.moderate;
  SymptomDuration _selectedDuration = SymptomDuration.shortTerm;
  EmotionalState _selectedEmotionalState = EmotionalState.calm;
  SleepQuality _selectedSleepQuality = SleepQuality.average;
  AppetiteState _selectedAppetite = AppetiteState.normal;
  bool _hasRegularExercise = false;
  
  // 其他数据
  final List<String> _dietaryPreferences = [];
  final List<String> _allergies = [];
  final List<String> _medicalHistory = [];
  
  // 页面状态
  int _currentStep = 0;
  
  @override
  void initState() {
    super.initState();
    _waterIntakeController.text = '6';
    
    // 如果有会话ID，获取会话信息
    if (widget.sessionId != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        ref.read(diagnosisViewModelProvider.notifier).getSession(widget.sessionId!);
      });
    }
  }
  
  @override
  void dispose() {
    _mainSymptomsController.dispose();
    _secondarySymptomsController.dispose();
    _notesController.dispose();
    _waterIntakeController.dispose();
    super.dispose();
  }
  
  /// 提交问诊数据
  void _submitInquiryData() {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    
    // 获取症状列表（按逗号分隔）
    final mainSymptoms = _mainSymptomsController.text
        .split(',')
        .map((s) => s.trim())
        .where((s) => s.isNotEmpty)
        .toList();
    
    // 获取伴随症状列表
    final secondarySymptoms = _secondarySymptomsController.text.isEmpty
        ? null
        : _secondarySymptomsController.text
            .split(',')
            .map((s) => s.trim())
            .where((s) => s.isNotEmpty)
            .toList();
    
    // 构建问诊数据
    final inquiryData = InquiryData.create(
      userId: 'current_user', // TODO: 实际应用中应从用户信息获取
      mainSymptoms: mainSymptoms,
      severity: _selectedSeverity,
      duration: _selectedDuration,
      secondarySymptoms: secondarySymptoms,
      emotionalState: _selectedEmotionalState,
      sleepQuality: _selectedSleepQuality,
      appetite: _selectedAppetite,
      waterIntake: int.tryParse(_waterIntakeController.text),
      regularExercise: _hasRegularExercise,
      dietaryPreferences: _dietaryPreferences.isEmpty ? null : _dietaryPreferences,
      allergies: _allergies.isEmpty ? null : _allergies,
      medicalHistory: _medicalHistory.isEmpty ? null : _medicalHistory,
      notes: _notesController.text.isEmpty ? null : _notesController.text,
    );
    
    // 如果当前有会话，更新会话状态
    final viewModel = ref.read(diagnosisViewModelProvider.notifier);
    final state = ref.read(diagnosisViewModelProvider);
    
    if (state.currentSession != null) {
      // 完成问诊步骤
      viewModel.completeCurrentStep(
        {'inquiry_data': inquiryData.toJson()},
        nextStep: DiagnosisStep.lifestyleInquiry,
      );
    }
    
    // 导航到下一步
    Navigator.of(context).pop(inquiryData);
  }
  
  @override
  Widget build(BuildContext context) {
    final state = ref.watch(diagnosisViewModelProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('症状问诊'),
        elevation: 0,
      ),
      body: Stack(
        children: [
          Form(
            key: _formKey,
            child: Stepper(
              currentStep: _currentStep,
              onStepContinue: () {
                if (_currentStep < 2) {
                  setState(() {
                    _currentStep += 1;
                  });
                } else {
                  _submitInquiryData();
                }
              },
              onStepCancel: () {
                if (_currentStep > 0) {
                  setState(() {
                    _currentStep -= 1;
                  });
                } else {
                  Navigator.of(context).pop();
                }
              },
              controlsBuilder: (context, details) {
                return Padding(
                  padding: const EdgeInsets.only(top: 16.0),
                  child: Row(
                    children: [
                      ElevatedButton(
                        onPressed: details.onStepContinue,
                        child: Text(_currentStep < 2 ? '下一步' : '提交'),
                      ),
                      const SizedBox(width: 12),
                      TextButton(
                        onPressed: details.onStepCancel,
                        child: Text(_currentStep > 0 ? '上一步' : '取消'),
                      ),
                    ],
                  ),
                );
              },
              steps: [
                // 症状信息步骤
                Step(
                  title: const Text('症状信息'),
                  subtitle: const Text('请描述您的不适症状'),
                  content: _buildSymptomsStep(),
                  isActive: _currentStep >= 0,
                ),
                
                // 精神状态步骤
                Step(
                  title: const Text('精神状态'),
                  subtitle: const Text('情绪与睡眠情况'),
                  content: _buildMentalStateStep(),
                  isActive: _currentStep >= 1,
                ),
                
                // 生活习惯步骤
                Step(
                  title: const Text('生活习惯'),
                  subtitle: const Text('饮食与运动情况'),
                  content: _buildLifestyleStep(),
                  isActive: _currentStep >= 2,
                ),
              ],
            ),
          ),
          
          // 引导文本
          if (state.currentGuidanceText != null)
            Positioned(
              top: 0,
              left: 0,
              right: 0,
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
                color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                child: Text(
                  state.currentGuidanceText!,
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.primary,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ),
          
          // 加载遮罩
          if (state.isLoading) const LoadingOverlay(message: '正在处理...'),
        ],
      ),
    );
  }
  
  /// 构建症状信息步骤UI
  Widget _buildSymptomsStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 主要症状
        TextFormField(
          controller: _mainSymptomsController,
          decoration: const InputDecoration(
            labelText: '主要症状 *',
            hintText: '请输入您的主要不适症状，多个症状用逗号分隔',
          ),
          maxLines: 2,
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return '请输入主要症状';
            }
            return null;
          },
        ),
        
        const SizedBox(height: 16),
        
        // 伴随症状
        TextFormField(
          controller: _secondarySymptomsController,
          decoration: const InputDecoration(
            labelText: '伴随症状（可选）',
            hintText: '请输入伴随症状，多个症状用逗号分隔',
          ),
          maxLines: 2,
        ),
        
        const SizedBox(height: 16),
        
        // 症状严重程度
        const Text('症状严重程度：'),
        const SizedBox(height: 8),
        Row(
          children: [
            _buildSeverityRadio(SymptomSeverity.mild, '轻微'),
            _buildSeverityRadio(SymptomSeverity.moderate, '中等'),
            _buildSeverityRadio(SymptomSeverity.severe, '严重'),
          ],
        ),
        
        const SizedBox(height: 16),
        
        // 症状持续时间
        const Text('症状持续时间：'),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 4,
          children: [
            _buildDurationChip(SymptomDuration.recent, '新发(1-3天)'),
            _buildDurationChip(SymptomDuration.shortTerm, '短期(一周内)'),
            _buildDurationChip(SymptomDuration.mediumTerm, '中期(一个月内)'),
            _buildDurationChip(SymptomDuration.longTerm, '长期(超过一个月)'),
            _buildDurationChip(SymptomDuration.chronic, '慢性(反复发作)'),
          ],
        ),
      ],
    );
  }
  
  /// 构建精神状态步骤UI
  Widget _buildMentalStateStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 情绪状态
        const Text('近期情绪状态：'),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 4,
          children: [
            _buildEmotionalStateChip(EmotionalState.calm, '平静'),
            _buildEmotionalStateChip(EmotionalState.anxious, '焦虑'),
            _buildEmotionalStateChip(EmotionalState.depressed, '抑郁'),
            _buildEmotionalStateChip(EmotionalState.irritable, '易怒'),
            _buildEmotionalStateChip(EmotionalState.mood_swings, '情绪波动'),
          ],
        ),
        
        const SizedBox(height: 16),
        
        // 睡眠质量
        const Text('睡眠质量：'),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 4,
          children: [
            _buildSleepQualityChip(SleepQuality.good, '良好'),
            _buildSleepQualityChip(SleepQuality.average, '一般'),
            _buildSleepQualityChip(SleepQuality.poor, '较差'),
            _buildSleepQualityChip(SleepQuality.insomnia, '严重失眠'),
          ],
        ),
        
        const SizedBox(height: 16),
        
        // 备注信息
        TextFormField(
          controller: _notesController,
          decoration: const InputDecoration(
            labelText: '备注信息（可选）',
            hintText: '其他想要补充的情况',
          ),
          maxLines: 3,
        ),
      ],
    );
  }
  
  /// 构建生活习惯步骤UI
  Widget _buildLifestyleStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 食欲状态
        const Text('目前食欲状态：'),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 4,
          children: [
            _buildAppetiteChip(AppetiteState.normal, '正常'),
            _buildAppetiteChip(AppetiteState.increased, '食欲增加'),
            _buildAppetiteChip(AppetiteState.decreased, '食欲减退'),
            _buildAppetiteChip(AppetiteState.poor, '明显厌食'),
          ],
        ),
        
        const SizedBox(height: 16),
        
        // 饮水情况
        Row(
          children: [
            Expanded(
              child: TextFormField(
                controller: _waterIntakeController,
                decoration: const InputDecoration(
                  labelText: '日均饮水量（杯）',
                  suffixText: '杯',
                ),
                keyboardType: TextInputType.number,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return '请输入饮水量';
                  }
                  return null;
                },
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: SwitchListTile(
                title: const Text('有规律运动'),
                value: _hasRegularExercise,
                contentPadding: EdgeInsets.zero,
                onChanged: (value) {
                  setState(() {
                    _hasRegularExercise = value;
                  });
                },
              ),
            ),
          ],
        ),
        
        const SizedBox(height: 16),
        
        // 饮食偏好选择
        const Text('饮食偏好（可多选）：'),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 4,
          children: [
            _buildPreferenceChip('辛辣食物'),
            _buildPreferenceChip('寒凉食物'),
            _buildPreferenceChip('油腻食物'),
            _buildPreferenceChip('甜食'),
            _buildPreferenceChip('清淡饮食'),
          ],
        ),
      ],
    );
  }
  
  /// 构建症状严重程度单选按钮
  Widget _buildSeverityRadio(SymptomSeverity value, String label) {
    return Expanded(
      child: RadioListTile<SymptomSeverity>(
        title: Text(label),
        value: value,
        groupValue: _selectedSeverity,
        onChanged: (SymptomSeverity? newValue) {
          if (newValue != null) {
            setState(() {
              _selectedSeverity = newValue;
            });
          }
        },
        contentPadding: EdgeInsets.zero,
        dense: true,
      ),
    );
  }
  
  /// 构建症状持续时间选择芯片
  Widget _buildDurationChip(SymptomDuration value, String label) {
    return ChoiceChip(
      label: Text(label),
      selected: _selectedDuration == value,
      onSelected: (bool selected) {
        if (selected) {
          setState(() {
            _selectedDuration = value;
          });
        }
      },
    );
  }
  
  /// 构建情绪状态选择芯片
  Widget _buildEmotionalStateChip(EmotionalState value, String label) {
    return ChoiceChip(
      label: Text(label),
      selected: _selectedEmotionalState == value,
      onSelected: (bool selected) {
        if (selected) {
          setState(() {
            _selectedEmotionalState = value;
          });
        }
      },
    );
  }
  
  /// 构建睡眠质量选择芯片
  Widget _buildSleepQualityChip(SleepQuality value, String label) {
    return ChoiceChip(
      label: Text(label),
      selected: _selectedSleepQuality == value,
      onSelected: (bool selected) {
        if (selected) {
          setState(() {
            _selectedSleepQuality = value;
          });
        }
      },
    );
  }
  
  /// 构建食欲状态选择芯片
  Widget _buildAppetiteChip(AppetiteState value, String label) {
    return ChoiceChip(
      label: Text(label),
      selected: _selectedAppetite == value,
      onSelected: (bool selected) {
        if (selected) {
          setState(() {
            _selectedAppetite = value;
          });
        }
      },
    );
  }
  
  /// 构建饮食偏好选择芯片
  Widget _buildPreferenceChip(String preference) {
    final isSelected = _dietaryPreferences.contains(preference);
    return FilterChip(
      label: Text(preference),
      selected: isSelected,
      onSelected: (bool selected) {
        setState(() {
          if (selected) {
            _dietaryPreferences.add(preference);
          } else {
            _dietaryPreferences.remove(preference);
          }
        });
      },
    );
  }
} 