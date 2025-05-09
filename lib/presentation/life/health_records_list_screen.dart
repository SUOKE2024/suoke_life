import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:suoke_life/di/providers.dart';
import 'package:suoke_life/domain/models/health_record_model.dart';
import 'package:suoke_life/presentation/life/add_health_record_screen.dart';
import 'package:suoke_life/presentation/life/health_record_detail_screen.dart';

/// 健康记录列表屏幕
class HealthRecordsListScreen extends ConsumerStatefulWidget {
  /// 构造函数
  const HealthRecordsListScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<HealthRecordsListScreen> createState() => _HealthRecordsListScreenState();
}

class _HealthRecordsListScreenState extends ConsumerState<HealthRecordsListScreen> {
  HealthDataType? _selectedType;
  final DateFormat _dateFormat = DateFormat('yyyy-MM-dd HH:mm');
  final DateFormat _timeFormat = DateFormat('HH:mm');
  final DateFormat _dateOnlyFormat = DateFormat('yyyy-MM-dd');

  @override
  void initState() {
    super.initState();
    
    // 加载所有记录
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(healthRecordViewModelProvider.notifier).getAllRecords();
    });
  }

  // 跳转到添加记录页面
  void _navigateToAddRecord(HealthDataType type) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => AddHealthRecordScreen(initialType: type),
      ),
    ).then((_) {
      // 返回后刷新记录列表
      if (_selectedType != null) {
        ref.read(healthRecordViewModelProvider.notifier).getRecordsByType(_selectedType!);
      } else {
        ref.read(healthRecordViewModelProvider.notifier).getAllRecords();
      }
    });
  }

  // 跳转到记录详情页面
  void _navigateToRecordDetail(String recordId) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => HealthRecordDetailScreen(recordId: recordId),
      ),
    );
  }

  // 过滤记录类型
  void _filterByType(HealthDataType? type) {
    setState(() {
      _selectedType = type;
    });
    
    if (type != null) {
      ref.read(healthRecordViewModelProvider.notifier).getRecordsByType(type);
    } else {
      ref.read(healthRecordViewModelProvider.notifier).getAllRecords();
    }
  }

  @override
  Widget build(BuildContext context) {
    final recordState = ref.watch(healthRecordViewModelProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('健康记录'),
        actions: [
          // 添加筛选按钮
          PopupMenuButton<HealthDataType?>(
            icon: const Icon(Icons.filter_list),
            tooltip: '筛选记录类型',
            onSelected: _filterByType,
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: null,
                child: Text('全部类型'),
              ),
              const PopupMenuItem(
                value: HealthDataType.bloodPressure,
                child: Text('血压记录'),
              ),
              const PopupMenuItem(
                value: HealthDataType.weight,
                child: Text('体重记录'),
              ),
              const PopupMenuItem(
                value: HealthDataType.heartRate,
                child: Text('心率记录'),
              ),
              const PopupMenuItem(
                value: HealthDataType.bloodGlucose,
                child: Text('血糖记录'),
              ),
              const PopupMenuItem(
                value: HealthDataType.sleep,
                child: Text('睡眠记录'),
              ),
            ],
          ),
        ],
      ),
      body: recordState.isLoading
          ? const Center(child: CircularProgressIndicator())
          : recordState.errorMessage != null
              ? Center(child: Text('错误: ${recordState.errorMessage}'))
              : recordState.records.isEmpty
                  ? _buildEmptyView()
                  : _buildRecordsList(recordState.records),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showAddRecordDialog(),
        tooltip: '添加健康记录',
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildEmptyView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.note_alt_outlined,
            size: 80,
            color: Colors.grey,
          ),
          const SizedBox(height: 16),
          Text(
            _selectedType != null
                ? '暂无${_selectedType!.name}记录'
                : '暂无健康记录',
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            '点击下方的"+"按钮添加记录',
            style: TextStyle(color: Colors.grey),
          ),
        ],
      ),
    );
  }

  Widget _buildRecordsList(List<HealthRecord> records) {
    // 按日期对记录进行分组
    final Map<String, List<HealthRecord>> recordsByDate = {};
    
    for (final record in records) {
      final dateString = _dateOnlyFormat.format(record.recordTime);
      if (!recordsByDate.containsKey(dateString)) {
        recordsByDate[dateString] = [];
      }
      recordsByDate[dateString]!.add(record);
    }
    
    // 对日期进行排序（最新的日期排在前面）
    final sortedDates = recordsByDate.keys.toList()
      ..sort((a, b) => b.compareTo(a));
    
    return ListView.builder(
      itemCount: sortedDates.length,
      itemBuilder: (context, index) {
        final date = sortedDates[index];
        final dailyRecords = recordsByDate[date]!;
        
        // 对单日内的记录按时间排序（最新的时间排在前面）
        dailyRecords.sort((a, b) => b.recordTime.compareTo(a.recordTime));
        
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 日期标题
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
              child: Text(
                date,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ),
            // 该日期下的记录列表
            ...dailyRecords.map((record) => _buildRecordItem(record)).toList(),
          ],
        );
      },
    );
  }

  Widget _buildRecordItem(HealthRecord record) {
    // 根据记录类型构建不同的内容
    Widget content;
    Icon typeIcon;
    
    switch (record.type) {
      case HealthDataType.bloodPressure:
        final bpRecord = record as BloodPressureRecord;
        content = Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '收缩压: ${bpRecord.systolic} mmHg, 舒张压: ${bpRecord.diastolic} mmHg',
              style: const TextStyle(fontSize: 16),
            ),
            if (bpRecord.pulse != null)
              Text('脉搏: ${bpRecord.pulse} 次/分'),
          ],
        );
        typeIcon = const Icon(Icons.favorite, color: Colors.red);
        break;
        
      case HealthDataType.weight:
        final weightRecord = record as WeightRecord;
        content = Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '体重: ${weightRecord.weight.toStringAsFixed(1)} kg',
              style: const TextStyle(fontSize: 16),
            ),
            Row(
              children: [
                if (weightRecord.bmi != null)
                  Text('BMI: ${weightRecord.bmi!.toStringAsFixed(1)}'),
                if (weightRecord.bmi != null && weightRecord.bodyFat != null)
                  const Text(' | '),
                if (weightRecord.bodyFat != null)
                  Text('体脂率: ${weightRecord.bodyFat!.toStringAsFixed(1)}%'),
              ],
            ),
          ],
        );
        typeIcon = const Icon(Icons.monitor_weight, color: Colors.blue);
        break;
        
      case HealthDataType.heartRate:
        final hrRecord = record as HeartRateRecord;
        content = Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '心率: ${hrRecord.beatsPerMinute} 次/分',
              style: const TextStyle(fontSize: 16),
            ),
            if (hrRecord.measurementContext != null)
              Text('场景: ${hrRecord.measurementContext}'),
          ],
        );
        typeIcon = const Icon(Icons.favorite_border, color: Colors.pink);
        break;
        
      case HealthDataType.bloodGlucose:
        final bgRecord = record as BloodGlucoseRecord;
        content = Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '血糖: ${bgRecord.value.toStringAsFixed(1)} mmol/L',
              style: const TextStyle(fontSize: 16),
            ),
            Text(
              '${bgRecord.period.name} | ${bgRecord.isFasting ? '空腹' : '非空腹'}',
            ),
          ],
        );
        typeIcon = const Icon(Icons.water_drop, color: Colors.red);
        break;
        
      case HealthDataType.sleep:
        final sleepRecord = record as SleepRecord;
        final startTimeStr = _timeFormat.format(sleepRecord.startTime);
        final endTimeStr = _timeFormat.format(sleepRecord.endTime);
        content = Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '睡眠时长: ${sleepRecord.durationHours.toStringAsFixed(1)} 小时',
              style: const TextStyle(fontSize: 16),
            ),
            Text('时间: $startTimeStr - $endTimeStr'),
          ],
        );
        typeIcon = const Icon(Icons.nightlight, color: Colors.indigo);
        break;
        
      default:
        content = const Text('未知记录类型');
        typeIcon = const Icon(Icons.question_mark, color: Colors.grey);
    }
    
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: InkWell(
        onTap: () => _navigateToRecordDetail(record.id),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 记录类型图标
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: typeIcon,
              ),
              const SizedBox(width: 16),
              // 记录内容
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          record.type.name,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          _timeFormat.format(record.recordTime),
                          style: TextStyle(
                            color: Colors.grey.shade600,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    content,
                    if (record.note != null && record.note!.isNotEmpty) ...[
                      const SizedBox(height: 8),
                      Text(
                        '备注: ${record.note}',
                        style: TextStyle(
                          color: Colors.grey.shade700,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showAddRecordDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('选择记录类型'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.favorite, color: Colors.red),
              title: const Text('血压记录'),
              onTap: () {
                Navigator.pop(context);
                _navigateToAddRecord(HealthDataType.bloodPressure);
              },
            ),
            ListTile(
              leading: const Icon(Icons.monitor_weight, color: Colors.blue),
              title: const Text('体重记录'),
              onTap: () {
                Navigator.pop(context);
                _navigateToAddRecord(HealthDataType.weight);
              },
            ),
            ListTile(
              leading: const Icon(Icons.favorite_border, color: Colors.pink),
              title: const Text('心率记录'),
              onTap: () {
                Navigator.pop(context);
                _navigateToAddRecord(HealthDataType.heartRate);
              },
            ),
            ListTile(
              leading: const Icon(Icons.water_drop, color: Colors.red),
              title: const Text('血糖记录'),
              onTap: () {
                Navigator.pop(context);
                _navigateToAddRecord(HealthDataType.bloodGlucose);
              },
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
        ],
      ),
    );
  }
}
