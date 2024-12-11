import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/player.dart';
import '../models/treasure.dart';
import '../models/game_config.dart';
import 'ar_service.dart';

class GameService {
  // 单例模式
  static final GameService _instance = GameService._internal();
  factory GameService() => _instance;
  GameService._internal();

  // 服务状态
  bool _isInitialized = false;
  late ARService _arService;
  Player? _currentPlayer;
  
  // 游戏状态
  final Map<String, Treasure> _activeTreasures = {};
  final List<String> _completedQuests = [];
  final Map<String, dynamic> _currentWeather = {};
  Timer? _weatherUpdateTimer;
  Timer? _treasureSpawnTimer;
  
  // 状态流控制器
  final _gameStateController = StreamController<Map<String, dynamic>>.broadcast();
  final _questController = StreamController<Map<String, dynamic>>.broadcast();
  final _achievementController = StreamController<Map<String, dynamic>>.broadcast();

  // 初始化游戏服务
  Future<bool> initialize(Player player) async {
    if (_isInitialized) return true;

    try {
      _currentPlayer = player;
      _arService = ARService();
      await _arService.initialize();

      // 启动各个系统
      _startWeatherSystem();
      _startTreasureSystem();
      _startQuestSystem();
      _startAchievementSystem();

      _isInitialized = true;
      return true;
    } catch (e) {
      debugPrint('Game Service initialization failed: $e');
      return false;
    }
  }

  // 天气系统
  void _startWeatherSystem() {
    // 初始天气
    _updateWeather();

    // 定期更新天气
    _weatherUpdateTimer = Timer.periodic(
      const Duration(minutes: 15),
      (_) => _updateWeather(),
    );
  }

  void _updateWeather() {
    // TODO: 接入真实天气API
    final weathers = GameConfig.weatherEffects.keys.toList();
    final randomWeather = weathers[DateTime.now().millisecond % weathers.length];
    
    _currentWeather = {
      'type': randomWeather,
      'effects': GameConfig.weatherEffects[randomWeather],
    };

    _notifyGameState();
  }

  // 宝藏系统
  void _startTreasureSystem() {
    // 初始宝藏
    _spawnInitialTreasures();

    // 定期刷新宝藏
    _treasureSpawnTimer = Timer.periodic(
      const Duration(minutes: 30),
      (_) => _spawnNewTreasures(),
    );
  }

  void _spawnInitialTreasures() {
    // TODO: 根据当前位置和游戏配置生成初始宝藏
  }

  void _spawnNewTreasures() {
    // TODO: 根据玩家活动情况和游戏配置生成新宝藏
  }

  // 任务系统
  void _startQuestSystem() {
    _generateDailyQuests();
    _generateWeeklyQuests();
    _checkSeasonProgress();
  }

  void _generateDailyQuests() {
    // TODO: 生成每日任务
  }

  void _generateWeeklyQuests() {
    // TODO: 生成每周任务
  }

  void _checkSeasonProgress() {
    // TODO: 检查赛季进度
  }

  // 成就系统
  void _startAchievementSystem() {
    _checkAchievements();
  }

  void _checkAchievements() {
    // TODO: 检查成就完成情况
  }

  // 发现宝藏
  Future<Map<String, dynamic>> discoverTreasure(String treasureId) async {
    final treasure = _activeTreasures[treasureId];
    if (treasure == null) {
      throw Exception('Treasure not found');
    }

    if (treasure.isFound) {
      throw Exception('Treasure already found');
    }

    // 标记宝藏为已找到
    treasure.markAsFound(_currentPlayer!.id);

    // 获取奖励
    final rewards = treasure.getRewards();

    // 更新玩家状态
    _currentPlayer!.addExperience(rewards['experience'] as int);
    _currentPlayer!.points += rewards['points'] as int;
    
    // 添加物品到背包
    final items = rewards['items'] as List<Map<String, dynamic>>;
    for (final item in items) {
      _currentPlayer!.addItem(item['id'], item);
    }

    // 检查相关任务和成就
    _checkQuestProgress(treasureId);
    _checkAchievements();

    // 从活动宝藏中移除
    _activeTreasures.remove(treasureId);
    
    // 通知状态更新
    _notifyGameState();

    return rewards;
  }

  // 完成任务
  Future<Map<String, dynamic>> completeQuest(String questId) async {
    if (_completedQuests.contains(questId)) {
      throw Exception('Quest already completed');
    }

    // TODO: 验证任务完成条件

    // 标记任务完成
    _completedQuests.add(questId);

    // TODO: 发放任务奖励

    // 通知任务更新
    _notifyQuestUpdate();

    return {}; // 返回奖励信息
  }

  // 状态通知
  void _notifyGameState() {
    if (!_gameStateController.isClosed) {
      _gameStateController.add({
        'player': _currentPlayer?.toJson(),
        'weather': _currentWeather,
        'treasures': _activeTreasures.values.map((t) => t.toJson()).toList(),
      });
    }
  }

  void _notifyQuestUpdate() {
    if (!_questController.isClosed) {
      _questController.add({
        'completed': _completedQuests,
        // TODO: 添加其他任务相关信息
      });
    }
  }

  void _notifyAchievementUpdate() {
    if (!_achievementController.isClosed) {
      _achievementController.add({
        'achievements': _currentPlayer?.achievements,
        // TODO: 添加其他成就相关信息
      });
    }
  }

  // 获取游戏状态流
  Stream<Map<String, dynamic>> get gameState => _gameStateController.stream;

  // 获取任务状态流
  Stream<Map<String, dynamic>> get questState => _questController.stream;

  // 获取成就状态流
  Stream<Map<String, dynamic>> get achievementState => _achievementController.stream;

  // 释放资源
  void dispose() {
    _weatherUpdateTimer?.cancel();
    _treasureSpawnTimer?.cancel();
    _gameStateController.close();
    _questController.close();
    _achievementController.close();
    _arService.dispose();
  }
} 