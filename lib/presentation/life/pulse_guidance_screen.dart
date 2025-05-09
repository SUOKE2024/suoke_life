import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/models/diagnosis_session_model.dart';
import 'package:suoke_life/presentation/life/view_models/diagnosis_view_model.dart';
import 'package:suoke_life/presentation/widgets/loading_overlay.dart';

/// 脉搏类型枚举
enum PulseType {
  /// 浮脉 - 轻取即得，重按反弱
  floating,
  
  /// 沉脉 - 轻取不得，重按方得
  sinking,
  
  /// 迟脉 - 脉来缓慢
  slow,
  
  /// 数脉 - 脉来快速
  rapid,
  
  /// 虚脉 - 脉来无力
  weak,
  
  /// 实脉 - 脉来有力
  strong,
  
  /// 滑脉 - 脉来流利如珠
  slippery,
  
  /// 涩脉 - 脉来艰涩不畅
  rough,
}

/// 脉诊引导页面
class PulseGuidanceScreen extends ConsumerStatefulWidget {
  /// 会话ID
  final String? sessionId;

  /// 构造函数
  const PulseGuidanceScreen({
    super.key,
    this.sessionId,
  });

  @override
  ConsumerState<PulseGuidanceScreen> createState() => _PulseGuidanceScreenState();
}

class _PulseGuidanceScreenState extends ConsumerState<PulseGuidanceScreen> {
  // 当前步骤
  int _currentStep = 0;
  
  // 选中的脉象类型
  final Set<PulseType> _selectedPulseTypes = {};
  
  // 脉搏速率
  double _pulseRate = 70;
  
  // 脉搏力度 (0-1)
  double _pulseStrength = 0.5;
  
  // 脉搏节律 (0表示不规则，1表示规则)
  double _pulseRhythm = 0.8;
  
  // 脉搏质量评价
  String? _pulseQuality;
  
  @override
  void initState() {
    super.initState();
    
    // 加载会话
    if (widget.sessionId != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        ref.read(diagnosisViewModelProvider.notifier).getSession(widget.sessionId!);
      });
    }
  }
  
  /// 完成脉诊
  Future<void> _completePulseGuidance() async {
    final viewModel = ref.read(diagnosisViewModelProvider.notifier);
    
    // 收集数据
    final pulseData = {
      'pulse_types': _selectedPulseTypes.map((type) => type.name).toList(),
      'pulse_rate': _pulseRate.toInt(),
      'pulse_strength': _pulseStrength,
      'pulse_rhythm': _pulseRhythm,
      'pulse_quality': _pulseQuality,
    };
    
    // 更新会话
    await viewModel.completeCurrentStep(
      pulseData,
      nextStep: DiagnosisStep.analysis,
    );
    
    if (mounted) {
      Navigator.of(context).pop();
    }
  }
  
  /// 获取脉象名称
  String _getPulseName(PulseType type) {
    switch (type) {
      case PulseType.floating:
        return '浮脉';
      case PulseType.sinking:
        return '沉脉';
      case PulseType.slow:
        return '迟脉';
      case PulseType.rapid:
        return '数脉';
      case PulseType.weak:
        return '虚脉';
      case PulseType.strong:
        return '实脉';
      case PulseType.slippery:
        return '滑脉';
      case PulseType.rough:
        return '涩脉';
    }
  }
  
  /// 获取脉象描述
  String _getPulseDescription(PulseType type) {
    switch (type) {
      case PulseType.floating:
        return '轻按即可感觉到，重按反而减弱。多见于表证、风寒外感';
      case PulseType.sinking:
        return '轻按不明显，重按才能感觉到。多见于里证、内伤证';
      case PulseType.slow:
        return '每分钟跳动不足60次，节律缓慢。多见于寒证';
      case PulseType.rapid:
        return '每分钟跳动超过90次，节律快速。多见于热证';
      case PulseType.weak:
        return '脉来无力，按之空虚。多见于气血不足、虚证';
      case PulseType.strong:
        return '脉来强劲有力，充实。多见于实证';
      case PulseType.slippery:
        return '脉来流利活泼，如珠走盘。多见于痰饮、湿热或妊娠';
      case PulseType.rough:
        return '脉来涩滞不畅，如轻刀刮竹。多见于气血不足、血瘀';
    }
  }
  
  /// 切换脉象选择
  void _togglePulseType(PulseType type) {
    setState(() {
      if (_selectedPulseTypes.contains(type)) {
        _selectedPulseTypes.remove(type);
      } else {
        _selectedPulseTypes.add(type);
      }
    });
  }
  
  @override
  Widget build(BuildContext context) {
    final state = ref.watch(diagnosisViewModelProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('脉诊引导'),
        elevation: 0,
      ),
      body: Stack(
        children: [
          Stepper(
            physics: const ClampingScrollPhysics(),
            currentStep: _currentStep,
            onStepContinue: () {
              // 检查当前步骤是否完成
              bool canContinue = true;
              
              if (_currentStep == 1 && _selectedPulseTypes.isEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('请至少选择一种脉象类型')),
                );
                canContinue = false;
              }
              
              if (_currentStep == 2 && _pulseQuality == null) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('请选择脉搏质量评价')),
                );
                canContinue = false;
              }
              
              if (canContinue) {
                final isLastStep = _currentStep == 2;
                
                if (isLastStep) {
                  // 完成脉诊
                  _completePulseGuidance();
                } else {
                  setState(() {
                    _currentStep += 1;
                  });
                }
              }
            },
            onStepCancel: () {
              if (_currentStep > 0) {
                setState(() {
                  _currentStep -= 1;
                });
              }
            },
            controlsBuilder: (context, details) {
              return Padding(
                padding: const EdgeInsets.only(top: 16.0),
                child: Row(
                  children: [
                    ElevatedButton(
                      onPressed: details.onStepContinue,
                      child: Text(_currentStep < 2 ? '下一步' : '完成'),
                    ),
                    if (_currentStep > 0) ...[
                      const SizedBox(width: 16),
                      TextButton(
                        onPressed: details.onStepCancel,
                        child: const Text('上一步'),
                      ),
                    ],
                  ],
                ),
              );
            },
            steps: [
              Step(
                title: const Text('脉诊准备'),
                subtitle: const Text('学习如何正确把脉'),
                content: _buildPulsePreparationStep(),
                isActive: _currentStep >= 0,
              ),
              Step(
                title: const Text('脉象识别'),
                subtitle: const Text('识别脉搏特征'),
                content: _buildPulseIdentificationStep(),
                isActive: _currentStep >= 1,
              ),
              Step(
                title: const Text('脉诊总结'),
                subtitle: const Text('记录脉搏情况'),
                content: _buildPulseSummaryStep(),
                isActive: _currentStep >= 2,
              ),
            ],
          ),
          
          // 加载遮罩
          if (state.isLoading) const LoadingOverlay(message: '保存中...'),
        ],
      ),
    );
  }
  
  /// 构建脉诊准备步骤
  Widget _buildPulsePreparationStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionTitle('正确的脉诊方法'),
        
        const SizedBox(height: 16),
        
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.grey.withOpacity(0.1),
                spreadRadius: 1,
                blurRadius: 3,
                offset: const Offset(0, 1),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 120,
                    height: 120,
                    decoration: BoxDecoration(
                      color: Colors.grey[200],
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Center(
                      child: Icon(
                        Icons.image,
                        size: 40,
                        color: Colors.grey,
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildInstructionStep('保持安静放松'),
                        _buildInstructionStep('取坐位或卧位'),
                        _buildInstructionStep('将手腕放平，掌心向上'),
                        _buildInstructionStep('将三个手指（食指、中指、无名指）放在桡骨动脉处'),
                        _buildInstructionStep('轻、中、重三种力度分别感受脉象'),
                      ],
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 16),
              
              const Text(
                '注意: 脉诊最好在早晨进行，避免刚进食、剧烈运动或情绪激动后立即测量。',
                style: TextStyle(
                  fontStyle: FontStyle.italic,
                  color: Colors.red,
                ),
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 24),
        
        _buildSectionTitle('桡动脉位置识别'),
        
        const SizedBox(height: 16),
        
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.grey.withOpacity(0.1),
                spreadRadius: 1,
                blurRadius: 3,
                offset: const Offset(0, 1),
              ),
            ],
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '桡动脉位于手腕内侧，拇指一侧的凹陷处。这是中医脉诊的主要部位，称为"寸口"。',
                style: TextStyle(fontSize: 15),
              ),
              SizedBox(height: 8),
              Text(
                '轻轻按压该处，您应该能感受到规律的搏动。这就是您的脉搏。',
                style: TextStyle(fontSize: 15),
              ),
            ],
          ),
        ),
      ],
    );
  }
  
  /// 构建脉象识别步骤
  Widget _buildPulseIdentificationStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionTitle('脉搏基本特征'),
        
        const SizedBox(height: 16),
        
        // 脉搏速率选择
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.grey.withOpacity(0.1),
                spreadRadius: 1,
                blurRadius: 3,
                offset: const Offset(0, 1),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '脉搏速率 (次/分钟)',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const SizedBox(height: 8),
              Text(
                '数值：${_pulseRate.toInt()}',
                style: TextStyle(
                  color: Theme.of(context).colorScheme.primary,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Slider(
                value: _pulseRate,
                min: 40,
                max: 120,
                divisions: 80,
                label: _pulseRate.toInt().toString(),
                onChanged: (value) {
                  setState(() {
                    _pulseRate = value;
                  });
                },
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('慢 (40)', style: TextStyle(fontSize: 12)),
                  const Text('正常 (60-90)', style: TextStyle(fontSize: 12)),
                  const Text('快 (120)', style: TextStyle(fontSize: 12)),
                ],
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 16),
        
        // 脉搏力度选择
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.grey.withOpacity(0.1),
                spreadRadius: 1,
                blurRadius: 3,
                offset: const Offset(0, 1),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '脉搏力度',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const SizedBox(height: 8),
              Text(
                '力度：${(_pulseStrength * 100).toInt()}%',
                style: TextStyle(
                  color: Theme.of(context).colorScheme.primary,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Slider(
                value: _pulseStrength,
                min: 0,
                max: 1,
                divisions: 10,
                label: (_pulseStrength * 100).toInt().toString() + '%',
                onChanged: (value) {
                  setState(() {
                    _pulseStrength = value;
                  });
                },
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('虚弱', style: TextStyle(fontSize: 12)),
                  const Text('中等', style: TextStyle(fontSize: 12)),
                  const Text('有力', style: TextStyle(fontSize: 12)),
                ],
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 16),
        
        // 脉搏节律选择
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.grey.withOpacity(0.1),
                spreadRadius: 1,
                blurRadius: 3,
                offset: const Offset(0, 1),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '脉搏节律',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const SizedBox(height: 8),
              Text(
                '规律性：${(_pulseRhythm * 100).toInt()}%',
                style: TextStyle(
                  color: Theme.of(context).colorScheme.primary,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Slider(
                value: _pulseRhythm,
                min: 0,
                max: 1,
                divisions: 10,
                label: (_pulseRhythm * 100).toInt().toString() + '%',
                onChanged: (value) {
                  setState(() {
                    _pulseRhythm = value;
                  });
                },
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('不规则', style: TextStyle(fontSize: 12)),
                  const Text('基本规律', style: TextStyle(fontSize: 12)),
                  const Text('非常规律', style: TextStyle(fontSize: 12)),
                ],
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 24),
        
        _buildSectionTitle('脉象类型'),
        
        const SizedBox(height: 16),
        
        // 脉象类型选择网格
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            childAspectRatio: 3,
            crossAxisSpacing: 10,
            mainAxisSpacing: 10,
          ),
          itemCount: PulseType.values.length,
          itemBuilder: (context, index) {
            final pulseType = PulseType.values[index];
            final isSelected = _selectedPulseTypes.contains(pulseType);
            
            return InkWell(
              onTap: () => _togglePulseType(pulseType),
              borderRadius: BorderRadius.circular(8),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: isSelected
                      ? Theme.of(context).colorScheme.primary.withOpacity(0.1)
                      : Colors.white,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: isSelected
                        ? Theme.of(context).colorScheme.primary
                        : Colors.grey[300]!,
                    width: isSelected ? 2 : 1,
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      isSelected ? Icons.check_circle : Icons.circle_outlined,
                      color: isSelected
                          ? Theme.of(context).colorScheme.primary
                          : Colors.grey,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _getPulseName(pulseType),
                        style: TextStyle(
                          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        ),
        
        const SizedBox(height: 16),
        
        // 选中脉象的详细描述
        if (_selectedPulseTypes.isNotEmpty) ...[
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primary.withOpacity(0.05),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: Theme.of(context).colorScheme.primary.withOpacity(0.2),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  '选中脉象描述:',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 8),
                ..._selectedPulseTypes.map((type) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 8.0),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '• ${_getPulseName(type)}: ',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        Expanded(
                          child: Text(_getPulseDescription(type)),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ],
            ),
          ),
        ],
      ],
    );
  }
  
  /// 构建脉诊总结步骤
  Widget _buildPulseSummaryStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionTitle('脉搏情况总结'),
        
        const SizedBox(height: 16),
        
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.grey.withOpacity(0.1),
                spreadRadius: 1,
                blurRadius: 3,
                offset: const Offset(0, 1),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '请选择您的脉搏总体质量:',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              const SizedBox(height: 16),
              
              _buildRadioOption('和缓有力 - 脉搏平稳有力，节律规则', '和缓有力'),
              _buildRadioOption('无力漂浮 - 脉搏较弱，轻按即得', '无力漂浮'),
              _buildRadioOption('沉重有力 - 脉搏较深，按重才明显', '沉重有力'),
              _buildRadioOption('细弱欲绝 - 脉搏微弱难辨', '细弱欲绝'),
              _buildRadioOption('洪大有力 - 脉搏强劲有力，跳动明显', '洪大有力'),
              _buildRadioOption('弦紧滑数 - 脉搏紧绷如弦，速度较快', '弦紧滑数'),
            ],
          ),
        ),
        
        const SizedBox(height: 24),
        
        _buildSectionTitle('脉诊总结报告'),
        
        const SizedBox(height: 16),
        
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.grey.withOpacity(0.1),
                spreadRadius: 1,
                blurRadius: 3,
                offset: const Offset(0, 1),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 速率评估
              Row(
                children: [
                  const Text(
                    '脉搏速率: ',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Text(_getPulseRateAssessment()),
                ],
              ),
              const SizedBox(height: 8),
              
              // 力度评估
              Row(
                children: [
                  const Text(
                    '脉搏力度: ',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Text(_getPulseStrengthAssessment()),
                ],
              ),
              const SizedBox(height: 8),
              
              // 节律评估
              Row(
                children: [
                  const Text(
                    '脉搏节律: ',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Text(_getPulseRhythmAssessment()),
                ],
              ),
              const SizedBox(height: 8),
              
              // 脉象类型
              if (_selectedPulseTypes.isNotEmpty) ...[
                const Text(
                  '脉象类型: ',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: _selectedPulseTypes.map((type) {
                    return Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(
                          color: Theme.of(context).colorScheme.primary.withOpacity(0.3),
                        ),
                      ),
                      child: Text(_getPulseName(type)),
                    );
                  }).toList(),
                ),
              ],
              
              const SizedBox(height: 16),
              
              const Text(
                '温馨提示: 本脉诊分析仅供参考，不能替代专业中医师的诊断。如有不适，请及时就医。',
                style: TextStyle(
                  fontStyle: FontStyle.italic,
                  color: Colors.red,
                  fontSize: 13,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
  
  /// 构建指导步骤项
  Widget _buildInstructionStep(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('• ', style: TextStyle(fontWeight: FontWeight.bold)),
          Expanded(child: Text(text)),
        ],
      ),
    );
  }
  
  /// 构建单选选项
  Widget _buildRadioOption(String title, String value) {
    return RadioListTile<String>(
      title: Text(title),
      value: value,
      groupValue: _pulseQuality,
      onChanged: (val) {
        setState(() {
          _pulseQuality = val;
        });
      },
      activeColor: Theme.of(context).colorScheme.primary,
      contentPadding: EdgeInsets.zero,
    );
  }
  
  /// 构建小节标题
  Widget _buildSectionTitle(String title) {
    return Container(
      margin: const EdgeInsets.only(top: 8),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
  
  /// 获取脉搏速率评估
  String _getPulseRateAssessment() {
    if (_pulseRate < 60) {
      return '偏慢 (${_pulseRate.toInt()}次/分钟)，提示可能有寒证';
    } else if (_pulseRate > 90) {
      return '偏快 (${_pulseRate.toInt()}次/分钟)，提示可能有热证';
    } else {
      return '正常 (${_pulseRate.toInt()}次/分钟)';
    }
  }
  
  /// 获取脉搏力度评估
  String _getPulseStrengthAssessment() {
    if (_pulseStrength < 0.4) {
      return '偏弱 (${(_pulseStrength * 100).toInt()}%)，提示可能气血不足';
    } else if (_pulseStrength > 0.7) {
      return '有力 (${(_pulseStrength * 100).toInt()}%)，提示身体较为强健';
    } else {
      return '适中 (${(_pulseStrength * 100).toInt()}%)';
    }
  }
  
  /// 获取脉搏节律评估
  String _getPulseRhythmAssessment() {
    if (_pulseRhythm < 0.6) {
      return '不规则 (${(_pulseRhythm * 100).toInt()}%)，提示气血运行不畅';
    } else {
      return '规律 (${(_pulseRhythm * 100).toInt()}%)，提示气血运行通畅';
    }
  }
} 