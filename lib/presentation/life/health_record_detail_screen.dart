import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:suoke_life/di/providers.dart';
import 'package:suoke_life/domain/models/health_record_model.dart';

/// 健康记录详情屏幕
class HealthRecordDetailScreen extends ConsumerStatefulWidget {
  /// 记录ID
  final String recordId;

  /// 构造函数
  const HealthRecordDetailScreen({
    Key? key,
    required this.recordId,
  }) : super(key: key);

  @override
  ConsumerState<HealthRecordDetailScreen> createState() => _HealthRecordDetailScreenState();
}

class _HealthRecordDetailScreenState extends ConsumerState<HealthRecordDetailScreen> {
  HealthRecord? _record;
  bool _isLoading = true;
  String? _errorMessage;
  final DateFormat _dateFormat = DateFormat('yyyy-MM-dd HH:mm');

  @override
  void initState() {
    super.initState();
    _loadRecord();
  }

  Future<void> _loadRecord() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final record = await ref.read(healthRecordViewModelProvider.notifier)
          .getRecordById(widget.recordId);
      
      setState(() {
        _record = record;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = '加载记录失败：${e.toString()}';
        _isLoading = false;
      });
    }
  }

  void _deleteRecord() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认删除'),
        content: const Text('确定要删除此记录吗？此操作不可撤销。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.pop(context); // 关闭对话框
              
              // 显示加载指示器
              setState(() {
                _isLoading = true;
              });
              
              try {
                await ref.read(healthRecordViewModelProvider.notifier)
                    .deleteRecord(widget.recordId);
                    
                if (!mounted) return;
                
                // 返回上一页
                Navigator.pop(context);
                
              } catch (e) {
                setState(() {
                  _errorMessage = '删除记录失败：${e.toString()}';
                  _isLoading = false;
                });
              }
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('删除'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_record != null ? '${_record!.type.name}详情' : '记录详情'),
        actions: [
          if (_record != null)
            IconButton(
              icon: const Icon(Icons.delete),
              tooltip: '删除记录',
              onPressed: _deleteRecord,
            ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage != null
              ? Center(child: Text('错误: $_errorMessage'))
              : _record == null
                  ? const Center(child: Text('记录不存在'))
                  : _buildRecordDetails(),
    );
  }

  Widget _buildRecordDetails() {
    if (_record == null) return const SizedBox();
    
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 记录基本信息卡片
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        _record!.type.name,
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      _buildTypeIcon(_record!.type),
                    ],
                  ),
                  const Divider(),
                  ListTile(
                    leading: const Icon(Icons.calendar_today),
                    title: const Text('记录时间'),
                    subtitle: Text(_dateFormat.format(_record!.recordTime)),
                  ),
                  if (_record!.note != null && _record!.note!.isNotEmpty)
                    ListTile(
                      leading: const Icon(Icons.note),
                      title: const Text('备注'),
                      subtitle: Text(_record!.note!),
                    ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // 记录详细数据卡片
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '详细数据',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  _buildRecordTypeSpecificDetails(),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTypeIcon(HealthDataType type) {
    IconData iconData;
    Color iconColor;
    
    switch (type) {
      case HealthDataType.bloodPressure:
        iconData = Icons.favorite;
        iconColor = Colors.red;
        break;
      case HealthDataType.weight:
        iconData = Icons.monitor_weight;
        iconColor = Colors.blue;
        break;
      case HealthDataType.heartRate:
        iconData = Icons.favorite_border;
        iconColor = Colors.pink;
        break;
      case HealthDataType.bloodGlucose:
        iconData = Icons.water_drop;
        iconColor = Colors.red;
        break;
      case HealthDataType.sleep:
        iconData = Icons.nightlight;
        iconColor = Colors.indigo;
        break;
      default:
        iconData = Icons.question_mark;
        iconColor = Colors.grey;
    }
    
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: iconColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Icon(
        iconData,
        color: iconColor,
        size: 30,
      ),
    );
  }

  Widget _buildRecordTypeSpecificDetails() {
    if (_record == null) return const SizedBox();
    
    switch (_record!.type) {
      case HealthDataType.bloodPressure:
        return _buildBloodPressureDetails(_record! as BloodPressureRecord);
      case HealthDataType.weight:
        return _buildWeightDetails(_record! as WeightRecord);
      case HealthDataType.heartRate:
        return _buildHeartRateDetails(_record! as HeartRateRecord);
      case HealthDataType.bloodGlucose:
        return _buildBloodGlucoseDetails(_record! as BloodGlucoseRecord);
      case HealthDataType.sleep:
        return _buildSleepDetails(_record! as SleepRecord);
      default:
        return const Text('未知记录类型');
    }
  }

  Widget _buildBloodPressureDetails(BloodPressureRecord record) {
    return Column(
      children: [
        _buildDataItem(
          title: '收缩压',
          value: '${record.systolic}',
          unit: 'mmHg',
          icon: Icons.arrow_upward,
          color: Colors.red,
        ),
        _buildDataItem(
          title: '舒张压',
          value: '${record.diastolic}',
          unit: 'mmHg',
          icon: Icons.arrow_downward,
          color: Colors.blue,
        ),
        if (record.pulse != null)
          _buildDataItem(
            title: '脉搏',
            value: '${record.pulse}',
            unit: '次/分',
            icon: Icons.favorite_border,
            color: Colors.pink,
          ),
      ],
    );
  }

  Widget _buildWeightDetails(WeightRecord record) {
    return Column(
      children: [
        _buildDataItem(
          title: '体重',
          value: record.weight.toStringAsFixed(1),
          unit: 'kg',
          icon: Icons.monitor_weight,
          color: Colors.blue,
        ),
        if (record.bmi != null)
          _buildDataItem(
            title: 'BMI',
            value: record.bmi!.toStringAsFixed(1),
            unit: '',
            icon: Icons.square_foot,
            color: Colors.green,
          ),
        if (record.bodyFat != null)
          _buildDataItem(
            title: '体脂率',
            value: record.bodyFat!.toStringAsFixed(1),
            unit: '%',
            icon: Icons.water_drop,
            color: Colors.amber,
          ),
        if (record.muscleMass != null)
          _buildDataItem(
            title: '肌肉量',
            value: record.muscleMass!.toStringAsFixed(1),
            unit: 'kg',
            icon: Icons.fitness_center,
            color: Colors.deepPurple,
          ),
      ],
    );
  }

  Widget _buildHeartRateDetails(HeartRateRecord record) {
    return Column(
      children: [
        _buildDataItem(
          title: '心率',
          value: '${record.beatsPerMinute}',
          unit: '次/分',
          icon: Icons.favorite,
          color: Colors.red,
        ),
        if (record.measurementContext != null)
          _buildDataItem(
            title: '测量场景',
            value: record.measurementContext!,
            unit: '',
            icon: Icons.location_on,
            color: Colors.blue,
          ),
      ],
    );
  }

  Widget _buildBloodGlucoseDetails(BloodGlucoseRecord record) {
    return Column(
      children: [
        _buildDataItem(
          title: '血糖值',
          value: record.value.toStringAsFixed(1),
          unit: 'mmol/L',
          icon: Icons.water_drop,
          color: Colors.red,
        ),
        _buildDataItem(
          title: '测量时段',
          value: record.period.name,
          unit: '',
          icon: Icons.access_time,
          color: Colors.blue,
        ),
        _buildDataItem(
          title: '是否空腹',
          value: record.isFasting ? '是' : '否',
          unit: '',
          icon: Icons.food_bank,
          color: Colors.amber,
        ),
      ],
    );
  }

  Widget _buildSleepDetails(SleepRecord record) {
    final startTimeFormat = DateFormat('HH:mm');
    final endTimeFormat = DateFormat('HH:mm');
    
    return Column(
      children: [
        _buildDataItem(
          title: '睡眠时长',
          value: record.durationHours.toStringAsFixed(1),
          unit: '小时',
          icon: Icons.nightlight,
          color: Colors.indigo,
        ),
        _buildDataItem(
          title: '入睡时间',
          value: startTimeFormat.format(record.startTime),
          unit: '',
          icon: Icons.bedtime,
          color: Colors.blue,
        ),
        _buildDataItem(
          title: '起床时间',
          value: endTimeFormat.format(record.endTime),
          unit: '',
          icon: Icons.wb_sunny,
          color: Colors.amber,
        ),
        if (record.quality != null)
          _buildDataItem(
            title: '睡眠质量',
            value: '${record.quality}',
            unit: '分',
            icon: Icons.star,
            color: Colors.orange,
          ),
        _buildDataItem(
          title: '是否中断',
          value: record.hasInterruption ? '是' : '否',
          unit: '',
          icon: Icons.pause_circle,
          color: Colors.red,
        ),
      ],
    );
  }

  Widget _buildDataItem({
    required String title,
    required String value,
    required String unit,
    required IconData icon,
    required Color color,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              title,
              style: const TextStyle(
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Text(
            '$value ${unit.isEmpty ? '' : unit}',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

