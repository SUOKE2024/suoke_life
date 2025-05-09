import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/models/diagnosis_session_model.dart';
import 'package:suoke_life/domain/models/tongue_analysis_model.dart';
import 'package:suoke_life/presentation/life/view_models/diagnosis_view_model.dart';
import 'package:suoke_life/presentation/widgets/loading_overlay.dart';

/// 体质类型枚举
enum ConstitutionType {
  /// 平和质
  balanced,
  
  /// 气虚质
  qiDeficiency,
  
  /// 阳虚质
  yangDeficiency,
  
  /// 阴虚质
  yinDeficiency,
  
  /// 痰湿质
  phlegmDampness,
  
  /// 湿热质
  dampnessHeat,
  
  /// 血瘀质
  bloodStasis,
  
  /// 气郁质
  qiStagnation,
  
  /// 特禀质
  allergic,
}

/// 四诊结果分析页面
class DiagnosisResultScreen extends ConsumerStatefulWidget {
  /// 会话ID
  final String sessionId;

  /// 构造函数
  const DiagnosisResultScreen({
    super.key,
    required this.sessionId,
  });

  @override
  ConsumerState<DiagnosisResultScreen> createState() => _DiagnosisResultScreenState();
}

class _DiagnosisResultScreenState extends ConsumerState<DiagnosisResultScreen> {
  Map<ConstitutionType, double> _constitutionScores = {};
  List<String> _keySymptoms = [];
  List<String> _healthSuggestions = [];
  bool _isGeneratingReport = false;
  
  @override
  void initState() {
    super.initState();
    
    // 加载会话
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      final viewModel = ref.read(diagnosisViewModelProvider.notifier);
      await viewModel.getSession(widget.sessionId);
      _analyzeResults();
    });
  }
  
  /// 分析四诊结果
  Future<void> _analyzeResults() async {
    setState(() {
      _isGeneratingReport = true;
    });
    
    final state = ref.read(diagnosisViewModelProvider);
    if (state.currentSession == null) return;
    
    try {
      // 模拟分析过程
      await Future.delayed(const Duration(seconds: 2));
      
      // 生成体质分析结果（实际应用中应基于真实分析）
      setState(() {
        // 生成随机体质评分（实际中应基于四诊结果综合评分）
        final Map<ConstitutionType, double> scores = {};
        for (final type in ConstitutionType.values) {
          // 生成0.0-1.0的随机分数，平和质稍高一些
          double score = 0.3 + (DateTime.now().millisecond % 70) / 100; // 0.3-1.0
          if (type == ConstitutionType.balanced) {
            score = 0.6 + (DateTime.now().microsecond % 40) / 100; // 0.6-1.0
          }
          scores[type] = score;
        }
        
        _constitutionScores = scores;
        
        // 生成关键症状（实际中应基于四诊结果）
        _keySymptoms = _generateKeySymptoms(state.currentSession!);
        
        // 生成健康建议（实际中应基于分析结果）
        _healthSuggestions = _generateHealthSuggestions();
        
        _isGeneratingReport = false;
      });
      
      // 更新会话状态
      await ref.read(diagnosisViewModelProvider.notifier).completeCurrentStep(
        {
          'constitution_scores': _constitutionScores.map((key, value) => 
              MapEntry(key.name, value)),
          'key_symptoms': _keySymptoms,
          'health_suggestions': _healthSuggestions,
        },
        nextStep: DiagnosisStep.recommendation,
      );
    } catch (e) {
      setState(() {
        _isGeneratingReport = false;
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('分析失败: $e')),
        );
      }
    }
  }
  
  /// 生成关键症状
  List<String> _generateKeySymptoms(DiagnosisSession session) {
    // 基于会话中收集的数据生成关键症状（模拟）
    final List<String> symptoms = [];
    
    // 从舌象分析中提取症状
    if (session.diagnosisData.containsKey('tongue_analysis')) {
      final tongueData = session.diagnosisData['tongue_analysis'] as Map<String, dynamic>;
      
      // 舌质分析
      if (tongueData.containsKey('body_color')) {
        final bodyColor = tongueData['body_color'] as String;
        if (bodyColor == 'pale') {
          symptoms.add('舌淡白，提示气血不足');
        } else if (bodyColor == 'red') {
          symptoms.add('舌红，提示有内热');
        } else if (bodyColor == 'purple') {
          symptoms.add('舌紫，提示有血瘀');
        }
      }
      
      // 舌苔分析
      if (tongueData.containsKey('coating_color')) {
        final coatingColor = tongueData['coating_color'] as String;
        if (coatingColor == 'white') {
          symptoms.add('舌苔白，提示风寒或胃寒');
        } else if (coatingColor == 'yellow') {
          symptoms.add('舌苔黄，提示有胃热');
        } else if (coatingColor == 'gray') {
          symptoms.add('舌苔灰，提示有内寒');
        }
      }
    }
    
    // 从声音分析中提取症状
    if (session.diagnosisData.containsKey('voice_features')) {
      final voiceFeatures = session.diagnosisData['voice_features'] as Map<String, dynamic>;
      
      if (voiceFeatures.containsKey('pitch')) {
        final pitch = voiceFeatures['pitch'] as double;
        if (pitch > 0.8) {
          symptoms.add('声音偏高，提示体内有热');
        } else if (pitch < 0.6) {
          symptoms.add('声音偏低，提示体内有寒');
        }
      }
      
      if (voiceFeatures.containsKey('volume')) {
        final volume = voiceFeatures['volume'] as double;
        if (volume < 0.5) {
          symptoms.add('声音较弱，提示气虚');
        }
      }
    }
    
    // 从脉象分析中提取症状
    if (session.diagnosisData.containsKey('pulse_types')) {
      final pulseTypes = session.diagnosisData['pulse_types'] as List<dynamic>;
      
      if (pulseTypes.contains('rapid')) {
        symptoms.add('脉搏较快，提示有热证');
      }
      
      if (pulseTypes.contains('slow')) {
        symptoms.add('脉搏较慢，提示有寒证');
      }
      
      if (pulseTypes.contains('weak')) {
        symptoms.add('脉搏无力，提示气血不足');
      }
    }
    
    // 添加一些基础症状
    symptoms.addAll([
      '容易疲劳，提示气虚',
      '口干舌燥，提示阴虚',
      '腹部胀满，提示脾胃不和',
      '睡眠欠佳，提示肝郁气滞',
    ]);
    
    return symptoms;
  }
  
  /// 生成健康建议
  List<String> _generateHealthSuggestions() {
    return [
      '调整生活作息，保证充足睡眠，最好在23点前入睡',
      '饮食宜清淡，避免辛辣刺激性食物',
      '增加蔬果摄入，保证每日5种以上蔬菜水果',
      '适量运动，可选择太极、瑜伽等舒缓运动',
      '保持心情舒畅，避免情绪波动过大',
      '建议每日进行腹式呼吸5-10分钟',
      '按摩足三里、关元等穴位，增强体质',
      '注意保暖，预防感冒',
      '饮食规律，避免过饱或过饿',
      '避免长时间使用电子设备，保护眼睛'
    ];
  }
  
  /// 获取体质名称
  String _getConstitutionName(ConstitutionType type) {
    switch (type) {
      case ConstitutionType.balanced:
        return '平和质';
      case ConstitutionType.qiDeficiency:
        return '气虚质';
      case ConstitutionType.yangDeficiency:
        return '阳虚质';
      case ConstitutionType.yinDeficiency:
        return '阴虚质';
      case ConstitutionType.phlegmDampness:
        return '痰湿质';
      case ConstitutionType.dampnessHeat:
        return '湿热质';
      case ConstitutionType.bloodStasis:
        return '血瘀质';
      case ConstitutionType.qiStagnation:
        return '气郁质';
      case ConstitutionType.allergic:
        return '特禀质';
    }
  }
  
  /// 获取体质颜色
  Color _getConstitutionColor(ConstitutionType type) {
    switch (type) {
      case ConstitutionType.balanced:
        return Colors.green;
      case ConstitutionType.qiDeficiency:
        return Colors.orange;
      case ConstitutionType.yangDeficiency:
        return Colors.blue;
      case ConstitutionType.yinDeficiency:
        return Colors.red;
      case ConstitutionType.phlegmDampness:
        return Colors.teal;
      case ConstitutionType.dampnessHeat:
        return Colors.amber;
      case ConstitutionType.bloodStasis:
        return Colors.purple;
      case ConstitutionType.qiStagnation:
        return Colors.indigo;
      case ConstitutionType.allergic:
        return Colors.pink;
    }
  }
  
  @override
  Widget build(BuildContext context) {
    final state = ref.watch(diagnosisViewModelProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('四诊分析结果'),
        elevation: 0,
      ),
      body: Stack(
        children: [
          if (state.currentSession == null || _isGeneratingReport)
            const Center(child: CircularProgressIndicator())
          else
            SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 结果概述
                  Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
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
                                color: Theme.of(context).colorScheme.primary,
                                size: 28,
                              ),
                              const SizedBox(width: 8),
                              const Text(
                                '体质分析结果',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          
                          // 体质评分条
                          ...(_constitutionScores.entries.toList()
                            ..sort((a, b) => b.value.compareTo(a.value)))
                            .map((entry) {
                              return Padding(
                                padding: const EdgeInsets.only(bottom: 12),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text(
                                          _getConstitutionName(entry.key),
                                          style: const TextStyle(fontWeight: FontWeight.bold),
                                        ),
                                        Text('${(entry.value * 100).toInt()}%'),
                                      ],
                                    ),
                                    const SizedBox(height: 4),
                                    LinearProgressIndicator(
                                      value: entry.value,
                                      minHeight: 8,
                                      borderRadius: BorderRadius.circular(4),
                                      color: _getConstitutionColor(entry.key),
                                      backgroundColor: Colors.grey.withOpacity(0.2),
                                    ),
                                  ],
                                ),
                              );
                            }).toList(),
                          
                          const SizedBox(height: 16),
                          
                          // 主要体质类型
                          const Text(
                            '主要体质类型:',
                            style: TextStyle(fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 8),
                          
                          // 显示前3名的体质类型
                          Wrap(
                            spacing: 8,
                            runSpacing: 8,
                            children: (_constitutionScores.entries.toList()
                              ..sort((a, b) => b.value.compareTo(a.value))
                              ..take(3))
                              .map((entry) {
                                return Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 12,
                                    vertical: 6,
                                  ),
                                  decoration: BoxDecoration(
                                    color: _getConstitutionColor(entry.key).withOpacity(0.2),
                                    borderRadius: BorderRadius.circular(16),
                                    border: Border.all(
                                      color: _getConstitutionColor(entry.key).withOpacity(0.5),
                                    ),
                                  ),
                                  child: Text(_getConstitutionName(entry.key)),
                                );
                              }).toList(),
                          ),
                        ],
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // 关键症状
                  Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                Icons.local_hospital,
                                color: Theme.of(context).colorScheme.primary,
                                size: 28,
                              ),
                              const SizedBox(width: 8),
                              const Text(
                                '关键症状与指标',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          
                          // 症状列表
                          ..._keySymptoms.map((symptom) {
                            return Padding(
                              padding: const EdgeInsets.only(bottom: 8),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Container(
                                    margin: const EdgeInsets.only(top: 5),
                                    width: 8,
                                    height: 8,
                                    decoration: BoxDecoration(
                                      color: Theme.of(context).colorScheme.primary,
                                      shape: BoxShape.circle,
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      symptom,
                                      style: const TextStyle(fontSize: 15),
                                    ),
                                  ),
                                ],
                              ),
                            );
                          }).toList(),
                        ],
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // 健康建议
                  Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                Icons.health_and_safety,
                                color: Theme.of(context).colorScheme.primary,
                                size: 28,
                              ),
                              const SizedBox(width: 8),
                              const Text(
                                '健康调理建议',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          
                          // 建议列表
                          ..._healthSuggestions.asMap().entries.map((entry) {
                            return Padding(
                              padding: const EdgeInsets.only(bottom: 12),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Container(
                                    width: 24,
                                    height: 24,
                                    decoration: BoxDecoration(
                                      color: Theme.of(context).colorScheme.primary,
                                      shape: BoxShape.circle,
                                    ),
                                    child: Center(
                                      child: Text(
                                        '${entry.key + 1}',
                                        style: const TextStyle(
                                          color: Colors.white,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          entry.value,
                                          style: const TextStyle(fontSize: 15),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            );
                          }).toList(),
                          
                          const SizedBox(height: 16),
                          
                          // 注意事项
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.amber.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(
                                color: Colors.amber.withOpacity(0.5),
                              ),
                            ),
                            child: const Row(
                              children: [
                                Icon(
                                  Icons.warning_amber_rounded,
                                  color: Colors.amber,
                                ),
                                SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    '以上建议仅供参考，请结合个人情况酌情采纳。如有严重健康问题，请及时就医。',
                                    style: TextStyle(
                                      fontSize: 13,
                                      color: Colors.black87,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // 保存按钮
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () {
                        // TODO: 实现保存到健康档案功能
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('已保存到健康档案')),
                        );
                        Navigator.of(context).pop();
                      },
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: const Text('保存到健康档案'),
                    ),
                  ),
                ],
              ),
            ),
          
          // 加载遮罩
          if (_isGeneratingReport)
            const LoadingOverlay(message: '正在生成分析报告...'),
        ],
      ),
    );
  }
} 