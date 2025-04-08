import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/models/sensor_data.dart';
import 'package:suoke_life/core/services/background_sensing_service.dart';
import 'package:suoke_life/core/services/context_aware_sensing_service.dart';
import 'package:suoke_life/core/services/privacy_protection_service.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/di/providers.dart';
import 'package:suoke_life/presentation/common/widgets/custom_app_bar.dart';
import 'package:suoke_life/presentation/common/widgets/loading_indicator.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class SensingControlPage extends ConsumerStatefulWidget {
  const SensingControlPage({Key? key}) : super(key: key);

  @override
  ConsumerState<SensingControlPage> createState() => _SensingControlPageState();
}

class _SensingControlPageState extends ConsumerState<SensingControlPage> {
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _refreshStatus();
  }

  // 刷新服务状态
  Future<void> _refreshStatus() async {
    setState(() {
      _isLoading = true;
    });

    try {
      // 刷新状态
      await ref.read(holisticSensingEngineProvider.notifier).getSensingStatus();
    } catch (e) {
      // 错误处理
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  // 切换服务状态
  Future<void> _toggleSensingState(bool value) async {
    setState(() {
      _isLoading = true;
    });

    try {
      if (value) {
        await ref.read(holisticSensingEngineProvider.notifier).startSensing();
      } else {
        await ref.read(holisticSensingEngineProvider.notifier).stopSensing();
      }
      await _refreshStatus();
    } catch (e) {
      // 错误处理
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    // 监听全息感知引擎状态
    final sensingEngineAsync = ref.watch(holisticSensingEngineProvider);

    // 监听背景感知服务
    final backgroundSensingService =
        ref.watch(backgroundSensingServiceProvider);

    // 监听环境感知服务
    final contextAwareSensingService =
        ref.watch(contextAwareSensingServiceProvider);

    // 监听隐私保护服务
    final privacyService = ref.watch(privacyProtectionServiceProvider);

    return Scaffold(
      appBar: CustomAppBar(
        title: '传感器与数据采集',
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isLoading ? null : _refreshStatus,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: LoadingIndicator())
          : sensingEngineAsync.when(
              data: (isInitialized) => _buildContent(
                context,
                isInitialized,
                backgroundSensingService,
                contextAwareSensingService,
                privacyService,
              ),
              loading: () => const Center(child: LoadingIndicator()),
              error: (error, stack) => Center(
                child: Text('初始化失败: $error'),
              ),
            ),
    );
  }

  Widget _buildContent(
    BuildContext context,
    bool isInitialized,
    BackgroundSensingService backgroundService,
    ContextAwareSensingService contextService,
    PrivacyProtectionService privacyService,
  ) {
    return RefreshIndicator(
      onRefresh: _refreshStatus,
      child: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          _buildStatusCard(isInitialized),
          const SizedBox(height: 16),
          _buildControlCard(context),
          const SizedBox(height: 16),
          _buildSensorStatusCard(backgroundService),
          const SizedBox(height: 16),
          _buildContextStatusCard(contextService),
          const SizedBox(height: 16),
          _buildPrivacyCard(privacyService),
        ],
      ),
    );
  }

  // 状态卡片
  Widget _buildStatusCard(bool isInitialized) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  isInitialized ? Icons.check_circle : Icons.error,
                  color: isInitialized ? Colors.green : Colors.red,
                ),
                const SizedBox(width: 8),
                Text(
                  '全息感知引擎状态',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              isInitialized ? '已初始化，可以使用' : '未初始化，无法使用',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
            FutureBuilder<Map<String, dynamic>>(
              future: ref
                  .read(holisticSensingEngineProvider.notifier)
                  .getSensingStatus(),
              builder: (context, snapshot) {
                if (!snapshot.hasData) {
                  return const Center(
                    child: SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                  );
                }

                final statusData = snapshot.data!;
                final isActive = statusData['holisticSensingActive'] as bool;

                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildStatusItem(
                      '全息感知系统',
                      isActive ? '运行中' : '已停止',
                      isActive ? Colors.green : Colors.grey,
                    ),
                    _buildStatusItem(
                      '背景感知服务',
                      statusData['backgroundSensing'] ? '运行中' : '已停止',
                      statusData['backgroundSensing']
                          ? Colors.green
                          : Colors.grey,
                    ),
                    _buildStatusItem(
                      '环境感知服务',
                      statusData['contextSensing'] ? '运行中' : '已停止',
                      statusData['contextSensing'] ? Colors.green : Colors.grey,
                    ),
                    _buildStatusItem(
                      '数据处理队列',
                      '${statusData['processingQueueSize']} 个任务',
                      statusData['processingQueueSize'] > 0
                          ? Colors.blue
                          : Colors.grey,
                    ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  // 控制卡片
  Widget _buildControlCard(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '控制中心',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 16),
            FutureBuilder<Map<String, dynamic>>(
              future: ref
                  .read(holisticSensingEngineProvider.notifier)
                  .getSensingStatus(),
              builder: (context, snapshot) {
                final isActive = snapshot.hasData
                    ? (snapshot.data!['holisticSensingActive'] as bool)
                    : false;

                return Column(
                  children: [
                    SwitchListTile(
                      title: const Text('全息感知系统'),
                      subtitle: Text(isActive ? '已启用' : '已禁用'),
                      value: isActive,
                      activeColor: AppColors.brandPrimary,
                      onChanged: _isLoading
                          ? null
                          : (value) => _toggleSensingState(value),
                    ),
                    const Divider(),
                    ElevatedButton.icon(
                      icon: const Icon(Icons.sync),
                      label: const Text('触发数据同步'),
                      onPressed: _isLoading || !isActive
                          ? null
                          : () async {
                              final backgroundService =
                                  ref.read(backgroundSensingServiceProvider);
                              await backgroundService.triggerDataSync();
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('数据同步任务已触发')),
                              );
                            },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.brandPrimary,
                        foregroundColor: Colors.white,
                        minimumSize: const Size(double.infinity, 48),
                      ),
                    ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  // 传感器状态卡片
  Widget _buildSensorStatusCard(BackgroundSensingService service) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '传感器状态',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 16),
            FutureBuilder<Map<String, dynamic>>(
              future: service.getSensorStatus(),
              builder: (context, snapshot) {
                if (!snapshot.hasData) {
                  return const Center(
                    child: SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                  );
                }

                final statusData = snapshot.data!;
                final enabledSensors =
                    statusData['enabledSensors'] as List<dynamic>;

                return Column(
                  children: [
                    _buildStatusItem(
                      '服务状态',
                      statusData['isRunning'] ? '运行中' : '已停止',
                      statusData['isRunning'] ? Colors.green : Colors.grey,
                    ),
                    const SizedBox(height: 8),
                    const Divider(),
                    const SizedBox(height: 8),
                    Text(
                      '已启用的传感器',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: enabledSensors.map((sensor) {
                        return Chip(
                          label: Text(sensor),
                          backgroundColor:
                              AppColors.brandPrimary.withAlpha((0.2 * 255).toInt()),
                        );
                      }).toList(),
                    ),
                    const SizedBox(height: 16),
                    ExpansionTile(
                      title: const Text('传感器配置'),
                      children: SensorType.values.map((type) {
                        return _buildSensorConfigTile(service, type);
                      }).toList(),
                    ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  // 传感器配置项
  Widget _buildSensorConfigTile(
      BackgroundSensingService service, SensorType type) {
    final config = service.getCurrentConfig().getConfig(type);
    final typeStr = type.toString().split('.').last;

    return ListTile(
      title: Text(typeStr),
      subtitle: Text(
        '状态: ${config.enabled ? "启用" : "禁用"}, '
        '间隔: ${config.samplingInterval}ms, '
        '电池优化: ${config.powerOptimizationLevel}/5',
      ),
      trailing: Switch(
        value: config.enabled,
        activeColor: AppColors.brandPrimary,
        onChanged: (value) async {
          if (value) {
            await service.enableSensor(type);
          } else {
            await service.disableSensor(type);
          }
          setState(() {});
        },
      ),
      onTap: () {
        // 可以添加配置对话框
      },
    );
  }

  // 环境感知状态卡片
  Widget _buildContextStatusCard(ContextAwareSensingService service) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '环境感知状态',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 16),
            _buildStatusItem(
              '监控状态',
              service.isMonitoring() ? '运行中' : '已停止',
              service.isMonitoring() ? Colors.green : Colors.grey,
            ),
            const SizedBox(height: 8),
            const Divider(),
            const SizedBox(height: 8),
            Text(
              '当前环境数据',
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),
            _buildEnvironmentInfoCard(service),
          ],
        ),
      ),
    );
  }

  // 环境信息卡片
  Widget _buildEnvironmentInfoCard(ContextAwareSensingService service) {
    final userContext = service.getCurrentContext();
    final environment = userContext.environment;
    final activity = userContext.activity;

    return Column(
      children: [
        _buildInfoRow('环境类型', environment.type.toString().split('.').last),
        _buildInfoRow(
            '光照级别', '${environment.lightLevel.toStringAsFixed(1)} lux'),
        _buildInfoRow(
            '噪音级别', '${environment.noiseLevel.toStringAsFixed(1)} dB'),
        if (environment.location != null) _buildInfoRow('位置信息', '已获取'),
        const Divider(),
        _buildInfoRow('活动状态', activity.state.toString().split('.').last),
        _buildInfoRow('置信度', '${activity.confidence}%'),
        _buildInfoRow('持续时间', '${activity.duration}秒'),
        const Divider(),
        _buildInfoRow('推断状态', userContext.inferredState),
      ],
    );
  }

  // 隐私设置卡片
  Widget _buildPrivacyCard(PrivacyProtectionService service) {
    final settings = service.getPrivacySettings();

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '隐私保护设置',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 16),
            SwitchListTile(
              title: const Text('匿名化'),
              subtitle: const Text('对敏感数据进行匿名化处理'),
              value: settings.enableAnonymization,
              activeColor: AppColors.brandPrimary,
              onChanged: (value) async {
                final newSettings = PrivacySettings(
                  differentialPrivacyEpsilon:
                      settings.differentialPrivacyEpsilon,
                  differentialPrivacyDelta: settings.differentialPrivacyDelta,
                  anonymizationSalt: settings.anonymizationSalt,
                  sensitiveFields: settings.sensitiveFields,
                  enableAnonymization: value,
                  enableDifferentialPrivacy: settings.enableDifferentialPrivacy,
                  enableFullEncryption: settings.enableFullEncryption,
                );
                await service.updatePrivacySettings(newSettings);
                setState(() {});
              },
            ),
            SwitchListTile(
              title: const Text('差分隐私'),
              subtitle: const Text('对数值数据添加随机噪声'),
              value: settings.enableDifferentialPrivacy,
              activeColor: AppColors.brandPrimary,
              onChanged: (value) async {
                final newSettings = PrivacySettings(
                  differentialPrivacyEpsilon:
                      settings.differentialPrivacyEpsilon,
                  differentialPrivacyDelta: settings.differentialPrivacyDelta,
                  anonymizationSalt: settings.anonymizationSalt,
                  sensitiveFields: settings.sensitiveFields,
                  enableAnonymization: settings.enableAnonymization,
                  enableDifferentialPrivacy: value,
                  enableFullEncryption: settings.enableFullEncryption,
                );
                await service.updatePrivacySettings(newSettings);
                setState(() {});
              },
            ),
            SwitchListTile(
              title: const Text('完全加密'),
              subtitle: const Text('对所有数据进行加密存储'),
              value: settings.enableFullEncryption,
              activeColor: AppColors.brandPrimary,
              onChanged: (value) async {
                final newSettings = PrivacySettings(
                  differentialPrivacyEpsilon:
                      settings.differentialPrivacyEpsilon,
                  differentialPrivacyDelta: settings.differentialPrivacyDelta,
                  anonymizationSalt: settings.anonymizationSalt,
                  sensitiveFields: settings.sensitiveFields,
                  enableAnonymization: settings.enableAnonymization,
                  enableDifferentialPrivacy: settings.enableDifferentialPrivacy,
                  enableFullEncryption: value,
                );
                await service.updatePrivacySettings(newSettings);
                setState(() {});
              },
            ),
            const Divider(),
            ExpansionTile(
              title: const Text('敏感字段配置'),
              children: settings.sensitiveFields.map((field) {
                return ListTile(
                  title: Text(field),
                  leading: const Icon(Icons.security),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  // 信息行
  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: Colors.grey[700],
            ),
          ),
          Text(value),
        ],
      ),
    );
  }

  // 状态项
  Widget _buildStatusItem(String label, String status, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Chip(
            label: Text(
              status,
              style: TextStyle(
                color: color == Colors.grey ? Colors.white : Colors.white,
                fontSize: 12,
              ),
            ),
            backgroundColor: color,
            padding: EdgeInsets.zero,
          ),
        ],
      ),
    );
  }
}
