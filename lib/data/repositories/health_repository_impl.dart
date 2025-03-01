import 'package:logger/logger.dart';
import '../../domain/entities/health_data.dart';
import '../../domain/repositories/health_repository.dart';
import '../datasources/health_data_source.dart';
import '../models/health_data_model.dart';

/// 健康数据仓库实现
/// 实现领域层定义的健康数据仓库接口，连接数据源和领域层
class HealthRepositoryImpl implements HealthRepository {
  final HealthDataSource remoteDataSource;
  final HealthDataSource localDataSource;
  final Logger logger;

  HealthRepositoryImpl({
    required this.remoteDataSource,
    required this.localDataSource,
    required this.logger,
  });

  @override
  Future<List<HealthData>> getUserHealthData(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
    int limit = 100,
    int offset = 0,
  }) async {
    try {
      // 首先尝试从本地获取
      try {
        final localData = await localDataSource.getUserHealthData(
          userId,
          startDate: startDate,
          endDate: endDate,
          limit: limit,
          offset: offset,
        );
        return localData.map((model) => model.toEntity()).toList();
      } catch (_) {
        // 本地获取失败，从远程获取
        final remoteData = await remoteDataSource.getUserHealthData(
          userId,
          startDate: startDate,
          endDate: endDate,
          limit: limit,
          offset: offset,
        );
        
        // 保存到本地
        await localDataSource.saveBatchHealthData(remoteData);
        
        return remoteData.map((model) => model.toEntity()).toList();
      }
    } catch (e) {
      logger.e('获取用户健康数据失败: $e');
      throw Exception('获取用户健康数据失败');
    }
  }

  @override
  Future<List<HealthData>> getHealthDataByType(
    String userId,
    HealthDataType type, {
    DateTime? startDate,
    DateTime? endDate,
    int limit = 100,
    int offset = 0,
  }) async {
    try {
      // 首先尝试从本地获取
      try {
        final localData = await localDataSource.getHealthDataByType(
          userId,
          type,
          startDate: startDate,
          endDate: endDate,
          limit: limit,
          offset: offset,
        );
        return localData.map((model) => model.toEntity()).toList();
      } catch (_) {
        // 本地获取失败，从远程获取
        final remoteData = await remoteDataSource.getHealthDataByType(
          userId,
          type,
          startDate: startDate,
          endDate: endDate,
          limit: limit,
          offset: offset,
        );
        
        // 保存到本地
        await localDataSource.saveBatchHealthData(remoteData);
        
        return remoteData.map((model) => model.toEntity()).toList();
      }
    } catch (e) {
      logger.e('获取用户特定类型健康数据失败: $e');
      throw Exception('获取用户特定类型健康数据失败');
    }
  }

  @override
  Future<HealthData> getHealthDataById(String dataId) async {
    try {
      // 首先尝试从本地获取
      try {
        final localData = await localDataSource.getHealthDataById(dataId);
        return localData.toEntity();
      } catch (_) {
        // 本地不存在，从远程获取
        final remoteData = await remoteDataSource.getHealthDataById(dataId);
        // 保存到本地
        await localDataSource.saveHealthData(remoteData);
        return remoteData.toEntity();
      }
    } catch (e) {
      logger.e('获取健康数据详情失败: $e');
      throw Exception('获取健康数据详情失败');
    }
  }

  @override
  Future<HealthData> saveHealthData(HealthData data) async {
    try {
      final dataModel = HealthDataModel.fromEntity(data);
      final savedData = await remoteDataSource.saveHealthData(dataModel);
      await localDataSource.saveHealthData(savedData);
      return savedData.toEntity();
    } catch (e) {
      logger.e('保存健康数据失败: $e');
      throw Exception('保存健康数据失败');
    }
  }

  @override
  Future<List<HealthData>> saveBatchHealthData(List<HealthData> dataList) async {
    try {
      final dataModels = dataList.map((data) => HealthDataModel.fromEntity(data)).toList();
      final savedDataList = await remoteDataSource.saveBatchHealthData(dataModels);
      await localDataSource.saveBatchHealthData(savedDataList);
      return savedDataList.map((model) => model.toEntity()).toList();
    } catch (e) {
      logger.e('批量保存健康数据失败: $e');
      throw Exception('批量保存健康数据失败');
    }
  }

  @override
  Future<HealthData> updateHealthData(HealthData data) async {
    try {
      final dataModel = HealthDataModel.fromEntity(data);
      final updatedData = await remoteDataSource.updateHealthData(dataModel);
      await localDataSource.updateHealthData(updatedData);
      return updatedData.toEntity();
    } catch (e) {
      logger.e('更新健康数据失败: $e');
      throw Exception('更新健康数据失败');
    }
  }

  @override
  Future<void> deleteHealthData(String dataId) async {
    try {
      await remoteDataSource.deleteHealthData(dataId);
      await localDataSource.deleteHealthData(dataId);
    } catch (e) {
      logger.e('删除健康数据失败: $e');
      throw Exception('删除健康数据失败');
    }
  }

  @override
  Future<void> deleteBatchHealthData(List<String> dataIds) async {
    try {
      await remoteDataSource.deleteBatchHealthData(dataIds);
      await localDataSource.deleteBatchHealthData(dataIds);
    } catch (e) {
      logger.e('批量删除健康数据失败: $e');
      throw Exception('批量删除健康数据失败');
    }
  }

  @override
  Future<Map<HealthDataType, num>> getDailyHealthSummary(
    String userId,
    DateTime date,
  ) async {
    try {
      return await remoteDataSource.getDailyHealthSummary(userId, date);
    } catch (e) {
      logger.e('获取每日健康数据汇总失败: $e');
      throw Exception('获取每日健康数据汇总失败');
    }
  }

  @override
  Future<Map<String, dynamic>> getHealthStatistics(
    String userId,
    HealthDataType type, {
    required DateTime startDate,
    required DateTime endDate,
    String? groupBy,
  }) async {
    try {
      return await remoteDataSource.getHealthStatistics(
        userId,
        type,
        startDate: startDate,
        endDate: endDate,
        groupBy: groupBy,
      );
    } catch (e) {
      logger.e('获取健康数据统计失败: $e');
      throw Exception('获取健康数据统计失败');
    }
  }

  @override
  Future<HealthData?> getLatestHealthData(
    String userId,
    HealthDataType type,
  ) async {
    try {
      final latestDataModel = await remoteDataSource.getLatestHealthData(userId, type);
      return latestDataModel?.toEntity();
    } catch (e) {
      logger.e('获取最新健康数据失败: $e');
      throw Exception('获取最新健康数据失败');
    }
  }

  @override
  Future<List<Map<String, dynamic>>> getHealthTrend(
    String userId,
    HealthDataType type, {
    required DateTime startDate,
    required DateTime endDate,
    required String interval,
  }) async {
    try {
      return await remoteDataSource.getHealthTrend(
        userId,
        type,
        startDate: startDate,
        endDate: endDate,
        interval: interval,
      );
    } catch (e) {
      logger.e('获取健康数据趋势失败: $e');
      throw Exception('获取健康数据趋势失败');
    }
  }

  @override
  Future<List<HealthData>> syncExternalHealthData(
    String userId,
    String source, {
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final syncedDataModels = await remoteDataSource.syncExternalHealthData(
        userId,
        source,
        startDate: startDate,
        endDate: endDate,
      );
      
      // 保存到本地
      await localDataSource.saveBatchHealthData(syncedDataModels);
      
      return syncedDataModels.map((model) => model.toEntity()).toList();
    } catch (e) {
      logger.e('同步外部健康数据失败: $e');
      throw Exception('同步外部健康数据失败');
    }
  }

  @override
  Future<Map<String, dynamic>> getUserHealthScore(String userId) async {
    try {
      // 获取用户各类型最新的健康数据
      final healthDataTypes = HealthDataType.values;
      final healthScores = <String, dynamic>{};
      
      // 计算健康评分
      // 注意：这里仅为示例，实际应用中应该有更复杂的计算逻辑
      int totalScore = 0;
      int validDataTypes = 0;
      
      for (final type in healthDataTypes) {
        try {
          final latestData = await getLatestHealthData(userId, type);
          if (latestData != null) {
            // 简单评分逻辑，实际应用中需要更复杂的算法
            int score;
            switch (type) {
              case HealthDataType.steps:
                score = (latestData.value >= 10000) ? 100 : (latestData.value / 100).round();
                break;
              case HealthDataType.sleep:
                score = (latestData.value >= 7 && latestData.value <= 9) ? 100 : 70;
                break;
              case HealthDataType.heartRate:
                score = (latestData.value >= 60 && latestData.value <= 100) ? 100 : 70;
                break;
              default:
                score = 70; // 默认评分
            }
            
            healthScores[type.toString()] = {
              'score': score,
              'value': latestData.value,
              'unit': latestData.unit.toString(),
              'timestamp': latestData.timestamp.toIso8601String(),
            };
            
            totalScore += score;
            validDataTypes++;
          }
        } catch (_) {
          // 忽略不可用的数据类型
        }
      }
      
      // 计算总评分
      final overallScore = validDataTypes > 0 ? totalScore / validDataTypes : 0;
      
      return {
        'overall_score': overallScore,
        'details': healthScores,
        'timestamp': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      logger.e('获取用户健康评分失败: $e');
      throw Exception('获取用户健康评分失败');
    }
  }

  @override
  Future<List<String>> getHealthSuggestions(
    String userId, {
    HealthDataType? focusArea,
  }) async {
    try {
      // 获取用户健康评分
      final healthScore = await getUserHealthScore(userId);
      
      // 根据健康评分生成建议
      // 注意：这里仅为示例，实际应用中应该有更复杂的逻辑
      final suggestions = <String>[];
      
      final details = healthScore['details'] as Map<String, dynamic>;
      
      // 如果指定了关注区域，只提供该区域的建议
      if (focusArea != null) {
        final focusAreaStr = focusArea.toString();
        if (details.containsKey(focusAreaStr)) {
          final score = details[focusAreaStr]['score'] as int;
          suggestions.add(_getSuggestionByTypeAndScore(focusArea, score));
        }
      } else {
        // 提供所有区域的建议
        for (final entry in details.entries) {
          final typeStr = entry.key;
          final score = entry.value['score'] as int;
          final type = HealthDataType.values.firstWhere(
            (t) => t.toString() == typeStr,
            orElse: () => HealthDataType.steps,
          );
          
          if (score < 80) {
            // 只对得分低于80的项目提供建议
            suggestions.add(_getSuggestionByTypeAndScore(type, score));
          }
        }
        
        // 添加一些通用建议
        suggestions.add('保持均衡饮食，多摄入蔬果和全谷物食品。');
        suggestions.add('每天保持充足的水分摄入，建议6-8杯水。');
        suggestions.add('保持良好的作息习惯，尽量在固定时间入睡和起床。');
      }
      
      return suggestions;
    } catch (e) {
      logger.e('获取健康建议失败: $e');
      throw Exception('获取健康建议失败');
    }
  }

  /// 根据健康数据类型和评分生成建议
  String _getSuggestionByTypeAndScore(HealthDataType type, int score) {
    if (score >= 80) return '您的${_getTypeName(type)}状况良好，请继续保持！';
    
    switch (type) {
      case HealthDataType.steps:
        return '您的日常活动量偏低，建议每天至少走10000步，或进行30分钟中等强度的有氧运动。';
      case HealthDataType.sleep:
        return '您的睡眠质量需要改善，建议保持规律的作息时间，睡前避免使用电子设备，卧室保持安静、黑暗和舒适的环境。';
      case HealthDataType.heartRate:
        return '您的心率状况需要关注，建议避免过度疲劳和压力，适量进行有氧运动，必要时咨询医生。';
      case HealthDataType.bloodPressure:
        return '您的血压状况需要关注，建议减少盐分摄入，保持健康的生活方式，定期检测血压，必要时咨询医生。';
      case HealthDataType.weight:
        return '您的体重状况需要调整，建议合理控制饮食，增加运动量，制定科学的减重计划。';
      case HealthDataType.waterIntake:
        return '您的水分摄入不足，建议每天饮用6-8杯水，在运动后及时补充水分。';
      case HealthDataType.foodIntake:
        return '您的饮食结构需要优化，建议增加蔬果摄入，控制高糖高脂食物，保持饮食多样性。';
      case HealthDataType.mood:
        return '您的情绪状态需要关注，建议尝试冥想、深呼吸等放松技巧，保持积极心态，必要时寻求专业帮助。';
      default:
        return '建议您持续关注健康状况，保持健康的生活方式。';
    }
  }

  /// 获取健康数据类型的中文名称
  String _getTypeName(HealthDataType type) {
    switch (type) {
      case HealthDataType.steps: return '步数';
      case HealthDataType.sleep: return '睡眠';
      case HealthDataType.heartRate: return '心率';
      case HealthDataType.bloodPressure: return '血压';
      case HealthDataType.bloodOxygen: return '血氧';
      case HealthDataType.temperature: return '体温';
      case HealthDataType.weight: return '体重';
      case HealthDataType.waterIntake: return '水分摄入';
      case HealthDataType.foodIntake: return '饮食';
      case HealthDataType.medication: return '用药';
      case HealthDataType.mood: return '情绪';
      case HealthDataType.symptom: return '症状';
      case HealthDataType.activity: return '活动';
      case HealthDataType.meditation: return '冥想';
      default: return '健康数据';
    }
  }

  @override
  Future<Map<String, dynamic>> generateHealthReport(
    String userId, {
    required DateTime startDate,
    required DateTime endDate,
  }) async {
    try {
      // 获取用户在指定时间段内的各类健康数据统计
      final healthDataTypes = HealthDataType.values;
      final reportData = <String, dynamic>{};
      
      // 获取每种类型的健康数据统计
      for (final type in healthDataTypes) {
        try {
          final statistics = await getHealthStatistics(
            userId,
            type,
            startDate: startDate,
            endDate: endDate,
            groupBy: 'day',
          );
          
          reportData[type.toString()] = statistics;
        } catch (_) {
          // 忽略不可用的数据类型
        }
      }
      
      // 获取健康评分
      final healthScore = await getUserHealthScore(userId);
      
      // 获取健康建议
      final suggestions = await getHealthSuggestions(userId);
      
      // 构建报告
      return {
        'user_id': userId,
        'start_date': startDate.toIso8601String(),
        'end_date': endDate.toIso8601String(),
        'generated_at': DateTime.now().toIso8601String(),
        'health_score': healthScore,
        'suggestions': suggestions,
        'data': reportData,
      };
    } catch (e) {
      logger.e('生成健康报告失败: $e');
      throw Exception('生成健康报告失败');
    }
  }
} 