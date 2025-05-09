import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:suoke_life/di/providers.dart';
import 'package:suoke_life/domain/models/health_record_model.dart';
import 'package:uuid/uuid.dart';

/// 添加健康记录屏幕
class AddHealthRecordScreen extends ConsumerStatefulWidget {
  /// 初始健康数据类型
  final HealthDataType initialType;

  /// 构造函数
  const AddHealthRecordScreen({
    Key? key,
    required this.initialType,
  }) : super(key: key);

  @override
  ConsumerState<AddHealthRecordScreen> createState() => _AddHealthRecordScreenState();
}

class _AddHealthRecordScreenState extends ConsumerState<AddHealthRecordScreen> {
  final _formKey = GlobalKey<FormState>();
  late DateTime _selectedDate;
  late TimeOfDay _selectedTime;
  final TextEditingController _noteController = TextEditingController();
  
  // 血压相关
  final TextEditingController _systolicController = TextEditingController();
  final TextEditingController _diastolicController = TextEditingController();
  final TextEditingController _pulseController = TextEditingController();
  
  // 体重相关
  final TextEditingController _weightController = TextEditingController();
  final TextEditingController _bmiController = TextEditingController();
  final TextEditingController _bodyFatController = TextEditingController();
  final TextEditingController _muscleMassController = TextEditingController();
  
  // 心率相关
  final TextEditingController _heartRateController = TextEditingController();
  String? _selectedMeasurementContext;
  final List<String> _measurementContexts = ['静息', '运动后', '睡眠前', '其他'];
  
  // 血糖相关
  final TextEditingController _bloodGlucoseController = TextEditingController();
  GlucoseMeasurementPeriod _selectedPeriod = GlucoseMeasurementPeriod.beforeBreakfast;
  bool _isFasting = true;

  @override
  void initState() {
    super.initState();
    _selectedDate = DateTime.now();
    _selectedTime = TimeOfDay.now();
  }

  @override
  void dispose() {
    _noteController.dispose();
    _systolicController.dispose();
    _diastolicController.dispose();
    _pulseController.dispose();
    _weightController.dispose();
    _bmiController.dispose();
    _bodyFatController.dispose();
    _muscleMassController.dispose();
    _heartRateController.dispose();
    _bloodGlucoseController.dispose();
    super.dispose();
  }

  Future<void> _selectDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: DateTime(2000),
      lastDate: DateTime.now(),
    );
    
    if (picked != null && picked != _selectedDate) {
      setState(() {
        _selectedDate = picked;
      });
    }
  }

  Future<void> _selectTime(BuildContext context) async {
    final TimeOfDay? picked = await showTimePicker(
      context: context,
      initialTime: _selectedTime,
    );
    
    if (picked != null && picked != _selectedTime) {
      setState(() {
        _selectedTime = picked;
      });
    }
  }

  DateTime _getDateTime() {
    return DateTime(
      _selectedDate.year,
      _selectedDate.month, 
      _selectedDate.day,
      _selectedTime.hour,
      _selectedTime.minute,
    );
  }

  void _saveRecord() {
    if (_formKey.currentState!.validate()) {
      final recordTime = _getDateTime();
      final uuid = const Uuid();
      final recordId = uuid.v4();
      
      HealthRecord record;
      
      switch (widget.initialType) {
        case HealthDataType.bloodPressure:
          record = BloodPressureRecord(
            id: recordId,
            userId: 'current_user', // 实际项目中应获取真实用户ID
            recordTime: recordTime, 
            systolic: int.parse(_systolicController.text),
            diastolic: int.parse(_diastolicController.text),
            pulse: _pulseController.text.isNotEmpty 
                ? int.parse(_pulseController.text) 
                : null,
            note: _noteController.text.isNotEmpty ? _noteController.text : null,
          );
          break;
          
        case HealthDataType.weight:
          record = WeightRecord(
            id: recordId,
            userId: 'current_user',
            recordTime: recordTime,
            weight: double.parse(_weightController.text),
            bmi: _bmiController.text.isNotEmpty 
                ? double.parse(_bmiController.text) 
                : null,
            bodyFat: _bodyFatController.text.isNotEmpty 
                ? double.parse(_bodyFatController.text) 
                : null,
            muscleMass: _muscleMassController.text.isNotEmpty 
                ? double.parse(_muscleMassController.text) 
                : null,
            note: _noteController.text.isNotEmpty ? _noteController.text : null,
          );
          break;
          
        case HealthDataType.heartRate:
          record = HeartRateRecord(
            id: recordId,
            userId: 'current_user',
            recordTime: recordTime,
            beatsPerMinute: int.parse(_heartRateController.text),
            measurementContext: _selectedMeasurementContext,
            note: _noteController.text.isNotEmpty ? _noteController.text : null,
          );
          break;
          
        case HealthDataType.bloodGlucose:
          record = BloodGlucoseRecord(
            id: recordId,
            userId: 'current_user',
            recordTime: recordTime,
            value: double.parse(_bloodGlucoseController.text),
            period: _selectedPeriod,
            isFasting: _isFasting,
            note: _noteController.text.isNotEmpty ? _noteController.text : null,
          );
          break;
          
        default:
          // 暂时不处理其他类型
          Navigator.of(context).pop();
          return;
      }
      
      // 保存记录
      ref.read(healthRecordViewModelProvider.notifier).addRecord(record);
      
      // 返回上一页
      Navigator.of(context).pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('添加${_getTypeTitle(widget.initialType)}'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 日期和时间选择
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        '记录时间',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          Expanded(
                            child: ListTile(
                              title: Text(
                                DateFormat('yyyy-MM-dd').format(_selectedDate),
                              ),
                              trailing: const Icon(Icons.calendar_today),
                              onTap: () => _selectDate(context),
                            ),
                          ),
                          Expanded(
                            child: ListTile(
                              title: Text(_selectedTime.format(context)),
                              trailing: const Icon(Icons.access_time),
                              onTap: () => _selectTime(context),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: 16),
              
              // 根据记录类型显示不同的表单内容
              _buildTypeSpecificForm(),
              
              const SizedBox(height: 16),
              
              // 备注
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        '备注',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextFormField(
                        controller: _noteController,
                        maxLines: 3,
                        decoration: const InputDecoration(
                          border: OutlineInputBorder(),
                          hintText: '添加备注信息（可选）',
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
                height: 50,
                child: ElevatedButton(
                  onPressed: _saveRecord,
                  child: const Text('保存记录'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTypeSpecificForm() {
    switch (widget.initialType) {
      case HealthDataType.bloodPressure:
        return _buildBloodPressureForm();
      case HealthDataType.weight:
        return _buildWeightForm();
      case HealthDataType.heartRate:
        return _buildHeartRateForm();
      case HealthDataType.bloodGlucose:
        return _buildBloodGlucoseForm();
      default:
        return const Center(
          child: Text('此类型记录尚未支持'),
        );
    }
  }

  Widget _buildBloodPressureForm() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '血压数据',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _systolicController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: '收缩压 (mmHg)',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return '请输入收缩压';
                      }
                      final systolic = int.tryParse(value);
                      if (systolic == null || systolic < 60 || systolic > 250) {
                        return '收缩压应在60-250mmHg范围内';
                      }
                      return null;
                    },
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextFormField(
                    controller: _diastolicController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: '舒张压 (mmHg)',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return '请输入舒张压';
                      }
                      final diastolic = int.tryParse(value);
                      if (diastolic == null || diastolic < 40 || diastolic > 150) {
                        return '舒张压应在40-150mmHg范围内';
                      }
                      return null;
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _pulseController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: '脉搏 (次/分钟，可选)',
                border: OutlineInputBorder(),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return null; // 脉搏是可选的
                }
                final pulse = int.tryParse(value);
                if (pulse == null || pulse < 40 || pulse > 200) {
                  return '脉搏应在40-200次/分钟范围内';
                }
                return null;
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWeightForm() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '体重数据',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _weightController,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(
                labelText: '体重 (kg)',
                border: OutlineInputBorder(),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return '请输入体重';
                }
                final weight = double.tryParse(value);
                if (weight == null || weight < 20 || weight > 300) {
                  return '体重应在20-300kg范围内';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _bmiController,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(
                labelText: 'BMI (可选)',
                border: OutlineInputBorder(),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return null; // BMI是可选的
                }
                final bmi = double.tryParse(value);
                if (bmi == null || bmi < 10 || bmi > 50) {
                  return 'BMI应在10-50范围内';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _bodyFatController,
                    keyboardType: const TextInputType.numberWithOptions(decimal: true),
                    decoration: const InputDecoration(
                      labelText: '体脂率 (%, 可选)',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return null; // 体脂率是可选的
                      }
                      final bodyFat = double.tryParse(value);
                      if (bodyFat == null || bodyFat < 1 || bodyFat > 60) {
                        return '体脂率应在1-60%范围内';
                      }
                      return null;
                    },
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextFormField(
                    controller: _muscleMassController,
                    keyboardType: const TextInputType.numberWithOptions(decimal: true),
                    decoration: const InputDecoration(
                      labelText: '肌肉量 (kg, 可选)',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return null; // 肌肉量是可选的
                      }
                      final muscleMass = double.tryParse(value);
                      if (muscleMass == null || muscleMass < 10 || muscleMass > 100) {
                        return '肌肉量应在10-100kg范围内';
                      }
                      return null;
                    },
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeartRateForm() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '心率数据',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _heartRateController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: '心率 (次/分)',
                border: OutlineInputBorder(),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return '请输入心率';
                }
                final heartRate = int.tryParse(value);
                if (heartRate == null || heartRate < 30 || heartRate > 220) {
                  return '心率应在30-220次/分范围内';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              decoration: const InputDecoration(
                labelText: '测量场景',
                border: OutlineInputBorder(),
              ),
              value: _selectedMeasurementContext,
              hint: const Text('选择一个测量场景'),
              items: _measurementContexts.map((String context) {
                return DropdownMenuItem<String>(
                  value: context,
                  child: Text(context),
                );
              }).toList(),
              onChanged: (String? newValue) {
                setState(() {
                  _selectedMeasurementContext = newValue;
                });
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBloodGlucoseForm() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '血糖数据',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _bloodGlucoseController,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(
                labelText: '血糖值 (mmol/L)',
                border: OutlineInputBorder(),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return '请输入血糖值';
                }
                final bloodGlucose = double.tryParse(value);
                if (bloodGlucose == null || bloodGlucose < 1 || bloodGlucose > 30) {
                  return '血糖值应在1-30mmol/L范围内';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<GlucoseMeasurementPeriod>(
              decoration: const InputDecoration(
                labelText: '测量时段',
                border: OutlineInputBorder(),
              ),
              value: _selectedPeriod,
              items: GlucoseMeasurementPeriod.values.map((GlucoseMeasurementPeriod period) {
                return DropdownMenuItem<GlucoseMeasurementPeriod>(
                  value: period,
                  child: Text(period.name),
                );
              }).toList(),
              onChanged: (GlucoseMeasurementPeriod? newValue) {
                if (newValue != null) {
                  setState(() {
                    _selectedPeriod = newValue;
                  });
                }
              },
            ),
            const SizedBox(height: 16),
            SwitchListTile(
              title: const Text('是否空腹'),
              value: _isFasting,
              onChanged: (bool value) {
                setState(() {
                  _isFasting = value;
                });
              },
            ),
          ],
        ),
      ),
    );
  }

  /// 获取类型标题
  String _getTypeTitle(HealthDataType type) {
    switch (type) {
      case HealthDataType.sleep:
        return '睡眠';
      case HealthDataType.bloodPressure:
        return '血压';
      case HealthDataType.weight:
        return '体重';
      case HealthDataType.heartRate:
        return '心率';
      case HealthDataType.bloodGlucose:
        return '血糖';
      default:
        return '健康';
    }
  }
}
