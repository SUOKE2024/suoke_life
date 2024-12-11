import 'package:flutter/foundation.dart';
import 'package:latlong2/latlong.dart';

class Treasure {
  final String id;
  final String name;
  final String type;      // 'mushroom', 'product', 'special'
  final String rarity;    // 'common', 'rare', 'epic', 'legendary'
  final LatLng location;
  final Map<String, dynamic> rewards;
  final Map<String, dynamic>? conditions;
  final String? description;
  final String? imageUrl;
  bool isFound;
  DateTime? foundTime;
  String? foundBy;

  Treasure({
    required this.id,
    required this.name,
    required this.type,
    required this.rarity,
    required this.location,
    required this.rewards,
    this.conditions,
    this.description,
    this.imageUrl,
    this.isFound = false,
    this.foundTime,
    this.foundBy,
  });

  // 计算与玩家的距离
  double calculateDistance(LatLng playerLocation) {
    final Distance distance = Distance();
    return distance.as(LengthUnit.Meter, location, playerLocation);
  }

  // 检查是否满足出现条件
  bool checkConditions(Map<String, dynamic> currentConditions) {
    if (conditions == null) return true;
    
    bool meetsConditions = true;
    conditions?.forEach((key, value) {
      if (currentConditions.containsKey(key)) {
        if (value is List) {
          meetsConditions &= value.contains(currentConditions[key]);
        } else {
          meetsConditions &= value == currentConditions[key];
        }
      }
    });
    
    return meetsConditions;
  }

  // 标记为已找到
  void markAsFound(String playerId) {
    isFound = true;
    foundTime = DateTime.now();
    foundBy = playerId;
  }

  // 获取奖励值
  Map<String, dynamic> getRewards() {
    return {
      ...rewards,
      'timestamp': DateTime.now().toIso8601String(),
    };
  }

  // 获取提示信息
  String getHint(int playerLevel) {
    String hint = '';
    
    switch (playerLevel) {
      case 1:
        hint = '这个宝藏在附近...';
        break;
      case 2:
        hint = '向${getDirectionHint()}方向寻找';
        break;
      default:
        hint = '距离约${getDistanceHint()}米，在${getDirectionHint()}方向';
    }
    
    return hint;
  }

  // 获取方向提示
  String getDirectionHint() {
    // 这里需要根据实际位置计算方向
    return '北';  // 示例返回
  }

  // 获取距离提示
  String getDistanceHint() {
    // 这里需要根据实际位置计算距离
    return '100';  // 示例返回
  }

  // 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'type': type,
      'rarity': rarity,
      'location': {
        'latitude': location.latitude,
        'longitude': location.longitude,
      },
      'rewards': rewards,
      'conditions': conditions,
      'description': description,
      'imageUrl': imageUrl,
      'isFound': isFound,
      'foundTime': foundTime?.toIso8601String(),
      'foundBy': foundBy,
    };
  }

  // 从JSON创建
  factory Treasure.fromJson(Map<String, dynamic> json) {
    return Treasure(
      id: json['id'],
      name: json['name'],
      type: json['type'],
      rarity: json['rarity'],
      location: LatLng(
        json['location']['latitude'],
        json['location']['longitude'],
      ),
      rewards: json['rewards'],
      conditions: json['conditions'],
      description: json['description'],
      imageUrl: json['imageUrl'],
      isFound: json['isFound'] ?? false,
      foundTime: json['foundTime'] != null
          ? DateTime.parse(json['foundTime'])
          : null,
      foundBy: json['foundBy'],
    );
  }

  // 创建野生菌宝藏
  factory Treasure.createMushroom({
    required String id,
    required String name,
    required LatLng location,
    required String rarity,
    String? description,
    String? imageUrl,
    Map<String, dynamic>? conditions,
  }) {
    final Map<String, dynamic> rewards = {
      'experience': _calculateMushroomExperience(rarity),
      'points': _calculateMushroomPoints(rarity),
      'items': _getMushroomRewardItems(rarity),
    };

    return Treasure(
      id: id,
      name: name,
      type: 'mushroom',
      rarity: rarity,
      location: location,
      rewards: rewards,
      conditions: conditions,
      description: description,
      imageUrl: imageUrl,
    );
  }

  // 计算野生菌经验值
  static int _calculateMushroomExperience(String rarity) {
    switch (rarity) {
      case 'common': return 100;
      case 'rare': return 300;
      case 'epic': return 600;
      case 'legendary': return 1000;
      default: return 50;
    }
  }

  // 计算野生菌积分
  static int _calculateMushroomPoints(String rarity) {
    switch (rarity) {
      case 'common': return 50;
      case 'rare': return 150;
      case 'epic': return 300;
      case 'legendary': return 500;
      default: return 25;
    }
  }

  // 获取野生菌奖励物品
  static List<Map<String, dynamic>> _getMushroomRewardItems(String rarity) {
    switch (rarity) {
      case 'common':
        return [
          {'id': 'mushroom_basket', 'count': 1},
          {'id': 'basic_guide', 'count': 1},
        ];
      case 'rare':
        return [
          {'id': 'special_basket', 'count': 1},
          {'id': 'identification_book', 'count': 1},
          {'id': 'rare_mushroom_badge', 'count': 1},
        ];
      case 'epic':
        return [
          {'id': 'master_basket', 'count': 1},
          {'id': 'expert_guide', 'count': 1},
          {'id': 'epic_mushroom_badge', 'count': 1},
          {'id': 'special_tool', 'count': 1},
        ];
      case 'legendary':
        return [
          {'id': 'legendary_basket', 'count': 1},
          {'id': 'master_guide', 'count': 1},
          {'id': 'legendary_mushroom_badge', 'count': 1},
          {'id': 'special_equipment', 'count': 1},
          {'id': 'nft_token', 'count': 1},
        ];
      default:
        return [
          {'id': 'basic_basket', 'count': 1},
        ];
    }
  }
} 