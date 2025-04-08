import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/domain/entities/four_diagnostic_data.dart';
import 'package:suoke_life/domain/usecases/manage_diagnostic_data_usecase.dart';

/// 四诊数据输入页面
///
/// 用于收集用户的四诊数据（望闻问切）
class DiagnosticDataInputView extends ConsumerStatefulWidget {
  /// 用户ID
  final String userId;
  
  /// 创建四诊数据输入页面
  const DiagnosticDataInputView({
    Key? key,
    required this.userId,
  }) : super(key: key);

  @override
  ConsumerState<DiagnosticDataInputView> createState() => _DiagnosticDataInputViewState();
}

class _DiagnosticDataInputViewState extends ConsumerState<DiagnosticDataInputView> {
  /// 当前标签页索引
  int _currentTabIndex = 0;
  
  /// 是否正在保存
  bool _isSaving = false;
  
  /// 望诊数据控制器
  final TextEditingController _faceColorController = TextEditingController();
  final TextEditingController _faceShapeController = TextEditingController();
  final TextEditingController _tongueColorController = TextEditingController();
  final TextEditingController _tongueCoatingController = TextEditingController();
  final TextEditingController _eyesController = TextEditingController();
  final TextEditingController _lipsController = TextEditingController();
  
  /// 闻诊数据控制器
  final TextEditingController _voiceController = TextEditingController();
  final TextEditingController _breathController = TextEditingController();
  final TextEditingController _odorController = TextEditingController();
  
  /// 问诊数据控制器
  final TextEditingController _mainComplaintsController = TextEditingController();
  final TextEditingController _medicalHistoryController = TextEditingController();
  final TextEditingController _familyHistoryController = TextEditingController();
  final TextEditingController _sleepPatternController = TextEditingController();
  final TextEditingController _appetiteController = TextEditingController();
  final TextEditingController _digestionController = TextEditingController();
  final TextEditingController _urinationController = TextEditingController();
  final TextEditingController _bowelMovementController = TextEditingController();
  final TextEditingController _menstruationController = TextEditingController();
  
  /// 切诊数据控制器
  final TextEditingController _pulseRateController = TextEditingController();
  final TextEditingController _pulsePatternController = TextEditingController();
  final TextEditingController _pulseStrengthController = TextEditingController();
  final TextEditingController _abdomenController = TextEditingController();
  final TextEditingController _backController = TextEditingController();
  final TextEditingController _limbsController = TextEditingController();
  
  // 默认值设置
  bool _hasFever = false;
  bool _hasChills = false;
  bool _hasSweat = false;
  bool _hasPain = false;
  
  // 痛点区域选择
  final List<String> _painAreas = [];
  
  @override
  void dispose() {
    _faceColorController.dispose();
    _faceShapeController.dispose();
    _tongueColorController.dispose();
    _tongueCoatingController.dispose();
    _eyesController.dispose();
    _lipsController.dispose();
    
    _voiceController.dispose();
    _breathController.dispose();
    _odorController.dispose();
    
    _mainComplaintsController.dispose();
    _medicalHistoryController.dispose();
    _familyHistoryController.dispose();
    _sleepPatternController.dispose();
    _appetiteController.dispose();
    _digestionController.dispose();
    _urinationController.dispose();
    _bowelMovementController.dispose();
    _menstruationController.dispose();
    
    _pulseRateController.dispose();
    _pulsePatternController.dispose();
    _pulseStrengthController.dispose();
    _abdomenController.dispose();
    _backController.dispose();
    _limbsController.dispose();
    
    super.dispose();
  }
  
  /// 保存四诊数据
  Future<void> _saveDiagnosticData() async {
    setState(() {
      _isSaving = true;
    });
    
    try {
      // 构建四诊数据模型
      final inspectionData = InspectionData(
        faceData: FaceData(
          color: _faceColorController.text,
          shape: _faceShapeController.text,
        ),
        tongueData: TongueData(
          color: _tongueColorController.text,
          coating: _tongueCoatingController.text,
        ),
        eyeData: _eyesController.text,
        lipData: _lipsController.text,
      );
      
      final auscultationData = AuscultationData(
        voiceData: _voiceController.text,
        breathData: _breathController.text,
        odorData: _odorController.text,
      );
      
      final inquiryData = InquiryData(
        mainComplaints: _mainComplaintsController.text,
        medicalHistory: _medicalHistoryController.text,
        familyHistory: _familyHistoryController.text,
        dailyLifeData: DailyLifeData(
          sleepPattern: _sleepPatternController.text,
          appetite: _appetiteController.text,
          digestion: _digestionController.text,
          urination: _urinationController.text,
          bowelMovement: _bowelMovementController.text,
          menstruation: _menstruationController.text,
        ),
        hasFever: _hasFever,
        hasChills: _hasChills,
        hasSweat: _hasSweat,
        hasPain: _hasPain,
        painAreas: _painAreas,
      );
      
      final palpationData = PalpationData(
        pulseData: PulseData(
          rate: _pulseRateController.text,
          pattern: _pulsePatternController.text,
          strength: _pulseStrengthController.text,
        ),
        abdomenData: _abdomenController.text,
        backData: _backController.text,
        limbData: _limbsController.text,
      );
      
      final diagnosticData = FourDiagnosticData(
        id: '', // ID由仓库生成
        userId: widget.userId,
        diagnosisTime: DateTime.now(),
        inspectionData: inspectionData,
        auscultationData: auscultationData,
        inquiryData: inquiryData,
        palpationData: palpationData,
      );
      
      // 保存数据
      final manageDiagnosticDataUseCase = ref.read(manageDiagnosticDataUseCaseProvider);
      final savedData = await manageDiagnosticDataUseCase.saveDiagnosticData(diagnosticData);
      
      setState(() {
        _isSaving = false;
      });
      
      // 数据保存成功，返回上一页
      if (!mounted) return;
      Navigator.of(context).pop(savedData);
    } catch (e) {
      setState(() {
        _isSaving = false;
      });
      
      // 显示错误提示
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('保存四诊数据失败: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('四诊数据采集'),
        backgroundColor: AppColors.primary,
      ),
      body: Column(
        children: [
          _buildTabBar(),
          Expanded(
            child: _buildTabContent(),
          ),
        ],
      ),
      bottomNavigationBar: _buildBottomButtons(),
    );
  }
  
  /// 构建标签栏
  Widget _buildTabBar() {
    return Container(
      color: AppColors.primary.withAlpha(30),
      child: Row(
        children: [
          _buildTabItem(0, '望诊', Icons.visibility),
          _buildTabItem(1, '闻诊', Icons.hearing),
          _buildTabItem(2, '问诊', Icons.question_answer),
          _buildTabItem(3, '切诊', Icons.touch_app),
        ],
      ),
    );
  }
  
  /// 构建标签项
  Widget _buildTabItem(int index, String title, IconData icon) {
    final isSelected = _currentTabIndex == index;
    
    return Expanded(
      child: InkWell(
        onTap: () {
          setState(() {
            _currentTabIndex = index;
          });
        },
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            border: Border(
              bottom: BorderSide(
                color: isSelected ? AppColors.primary : Colors.transparent,
                width: 3,
              ),
            ),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                icon,
                color: isSelected ? AppColors.primary : Colors.grey,
              ),
              const SizedBox(height: 4),
              Text(
                title,
                style: TextStyle(
                  color: isSelected ? AppColors.primary : Colors.grey,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  /// 构建标签页内容
  Widget _buildTabContent() {
    switch (_currentTabIndex) {
      case 0:
        return _buildInspectionTab();
      case 1:
        return _buildAuscultationTab();
      case 2:
        return _buildInquiryTab();
      case 3:
        return _buildPalpationTab();
      default:
        return const SizedBox.shrink();
    }
  }
  
  /// 构建望诊标签页
  Widget _buildInspectionTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '望诊',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const Text(
            '通过观察患者外在表现，了解其健康状况',
            style: TextStyle(
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 24),
          
          // 面色
          _buildSectionTitle('面色'),
          _buildInputField(
            label: '面色颜色',
            hintText: '例如：苍白、潮红、晦暗等',
            controller: _faceColorController,
          ),
          _buildInputField(
            label: '面形特征',
            hintText: '例如：浮肿、消瘦、刮风等',
            controller: _faceShapeController,
          ),
          
          const SizedBox(height: 16),
          
          // 舌象
          _buildSectionTitle('舌象'),
          _buildInputField(
            label: '舌质颜色',
            hintText: '例如：淡红、深红、紫暗等',
            controller: _tongueColorController,
          ),
          _buildInputField(
            label: '舌苔特征',
            hintText: '例如：薄白、厚腻、黄腻等',
            controller: _tongueCoatingController,
          ),
          
          const SizedBox(height: 16),
          
          // 其他
          _buildSectionTitle('其他观察'),
          _buildInputField(
            label: '眼部特征',
            hintText: '例如：明亮、暗淡、充血等',
            controller: _eyesController,
          ),
          _buildInputField(
            label: '唇部特征',
            hintText: '例如：红润、苍白、干裂等',
            controller: _lipsController,
          ),
        ],
      ),
    );
  }
  
  /// 构建闻诊标签页
  Widget _buildAuscultationTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '闻诊',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const Text(
            '通过听声音和嗅气味，了解健康状况',
            style: TextStyle(
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 24),
          
          // 声音
          _buildSectionTitle('声音'),
          _buildInputField(
            label: '声音特征',
            hintText: '例如：洪亮、低沉、颤抖等',
            controller: _voiceController,
          ),
          _buildInputField(
            label: '呼吸特征',
            hintText: '例如：平稳、急促、痰鸣等',
            controller: _breathController,
          ),
          
          const SizedBox(height: 16),
          
          // 气味
          _buildSectionTitle('气味'),
          _buildInputField(
            label: '体味特征',
            hintText: '例如：特殊气味、汗味等',
            controller: _odorController,
          ),
        ],
      ),
    );
  }
  
  /// 构建问诊标签页
  Widget _buildInquiryTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '问诊',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const Text(
            '通过询问患者症状、病史等，了解健康状况',
            style: TextStyle(
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 24),
          
          // 主诉与病史
          _buildSectionTitle('主诉与病史'),
          _buildInputField(
            label: '主要症状',
            hintText: '例如：头痛、乏力、胃痛等',
            controller: _mainComplaintsController,
            maxLines: 3,
          ),
          _buildInputField(
            label: '既往病史',
            hintText: '例如：高血压、糖尿病等',
            controller: _medicalHistoryController,
            maxLines: 3,
          ),
          _buildInputField(
            label: '家族病史',
            hintText: '例如：父亲有高血压，母亲有糖尿病等',
            controller: _familyHistoryController,
            maxLines: 2,
          ),
          
          const SizedBox(height: 16),
          
          // 生活起居
          _buildSectionTitle('生活起居'),
          _buildInputField(
            label: '睡眠情况',
            hintText: '例如：易醒、多梦、入睡困难等',
            controller: _sleepPatternController,
          ),
          _buildInputField(
            label: '饮食情况',
            hintText: '例如：食欲不振、暴饮暴食等',
            controller: _appetiteController,
          ),
          _buildInputField(
            label: '消化情况',
            hintText: '例如：胃胀、反酸、消化不良等',
            controller: _digestionController,
          ),
          _buildInputField(
            label: '小便情况',
            hintText: '例如：尿频、尿急、尿痛等',
            controller: _urinationController,
          ),
          _buildInputField(
            label: '大便情况',
            hintText: '例如：便秘、腹泻、黏液便等',
            controller: _bowelMovementController,
          ),
          _buildInputField(
            label: '月经情况（女性）',
            hintText: '例如：经期规律、量少、痛经等',
            controller: _menstruationController,
          ),
          
          const SizedBox(height: 16),
          
          // 其他症状
          _buildSectionTitle('其他症状'),
          _buildCheckboxItem(
            title: '发热',
            value: _hasFever,
            onChanged: (value) {
              setState(() {
                _hasFever = value ?? false;
              });
            },
          ),
          _buildCheckboxItem(
            title: '畏寒',
            value: _hasChills,
            onChanged: (value) {
              setState(() {
                _hasChills = value ?? false;
              });
            },
          ),
          _buildCheckboxItem(
            title: '出汗',
            value: _hasSweat,
            onChanged: (value) {
              setState(() {
                _hasSweat = value ?? false;
              });
            },
          ),
          _buildCheckboxItem(
            title: '疼痛',
            value: _hasPain,
            onChanged: (value) {
              setState(() {
                _hasPain = value ?? false;
              });
            },
          ),
          
          if (_hasPain) _buildPainAreaSelector(),
        ],
      ),
    );
  }
  
  /// 构建切诊标签页
  Widget _buildPalpationTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '切诊',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const Text(
            '通过触摸脉搏和体表，了解内脏功能和气血状况',
            style: TextStyle(
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 24),
          
          // 脉象
          _buildSectionTitle('脉象'),
          _buildInputField(
            label: '脉率',
            hintText: '例如：60-80次/分，快、慢等',
            controller: _pulseRateController,
          ),
          _buildInputField(
            label: '脉型',
            hintText: '例如：浮、沉、弦、滑等',
            controller: _pulsePatternController,
          ),
          _buildInputField(
            label: '脉力',
            hintText: '例如：有力、无力、微弱等',
            controller: _pulseStrengthController,
          ),
          
          const SizedBox(height: 16),
          
          // 触诊
          _buildSectionTitle('触诊'),
          _buildInputField(
            label: '腹部触诊',
            hintText: '例如：柔软、紧张、压痛等',
            controller: _abdomenController,
          ),
          _buildInputField(
            label: '背部触诊',
            hintText: '例如：肌肉紧张、压痛点等',
            controller: _backController,
          ),
          _buildInputField(
            label: '四肢触诊',
            hintText: '例如：温度、肌肉状态等',
            controller: _limbsController,
          ),
        ],
      ),
    );
  }
  
  /// 构建疼痛区域选择器
  Widget _buildPainAreaSelector() {
    final painAreaOptions = [
      '头部', '颈部', '胸部', '腹部', '腰部', '背部',
      '四肢', '关节', '全身', '其他'
    ];
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.symmetric(vertical: 8),
          child: Text(
            '疼痛区域(可多选)',
            style: TextStyle(
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        Wrap(
          spacing: 8,
          runSpacing: 0,
          children: painAreaOptions.map((area) {
            final isSelected = _painAreas.contains(area);
            
            return FilterChip(
              label: Text(area),
              selected: isSelected,
              onSelected: (value) {
                setState(() {
                  if (value) {
                    _painAreas.add(area);
                  } else {
                    _painAreas.remove(area);
                  }
                });
              },
              selectedColor: AppColors.primary.withAlpha(100),
              checkmarkColor: AppColors.primary,
            );
          }).toList(),
        ),
      ],
    );
  }
  
  /// 构建底部按钮
  Widget _buildBottomButtons() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withAlpha(100),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          OutlinedButton(
            onPressed: () {
              Navigator.of(context).pop();
            },
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            ),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: _isSaving ? null : _saveDiagnosticData,
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
            ),
            child: _isSaving
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  )
                : const Text('保存四诊数据'),
          ),
        ],
      ),
    );
  }
  
  /// 构建章节标题
  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Text(
        title,
        style: const TextStyle(
          fontWeight: FontWeight.bold,
          fontSize: 16,
        ),
      ),
    );
  }
  
  /// 构建输入字段
  Widget _buildInputField({
    required String label,
    required String hintText,
    required TextEditingController controller,
    int maxLines = 1,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: TextFormField(
        controller: controller,
        maxLines: maxLines,
        decoration: InputDecoration(
          labelText: label,
          hintText: hintText,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: BorderSide(color: AppColors.primary, width: 2),
          ),
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        ),
      ),
    );
  }
  
  /// 构建复选框项
  Widget _buildCheckboxItem({
    required String title,
    required bool value,
    required ValueChanged<bool?> onChanged,
  }) {
    return CheckboxListTile(
      title: Text(title),
      value: value,
      onChanged: onChanged,
      activeColor: AppColors.primary,
      contentPadding: EdgeInsets.zero,
      controlAffinity: ListTileControlAffinity.leading,
    );
  }
} 