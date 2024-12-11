import 'package:flutter/foundation.dart';

class Player {
  final String id;
  final String nickname;
  String? avatarUrl;
  int level;
  int experience;
  int points;
  Map<String, dynamic> inventory;
  Map<String, int> skills;
  List<String> achievements;
  Map<String, dynamic> stats;

  Player({
    required this.id,
    required this.nickname,
    this.avatarUrl,
    this.level = 1,
    this.experience = 0,
    this.points = 0,
    Map<String, dynamic>? inventory,
    Map<String, int>? skills,
    List<String>? achievements,
    Map<String, dynamic>? stats,
  })  : inventory = inventory ?? {},
        skills = skills ?? {
          'tracking': 1,
          'identification': 1,
          'navigation': 1,
          'trading': 1,
          'teamwork': 1,
          'teaching': 1,
          'mushroom_lore': 1,
          'nature_wisdom': 1,
          'local_geography': 1,
        },
        achievements = achievements ?? [],
        stats = stats ?? {
          'quests_completed': 0,
          'treasures_found': 0,
          'distance_traveled': 0,
          'time_spent': 0,
          'photos_shared': 0,
          'helped_others': 0,
        };

  // 增加经验值
  void addExperience(int amount) {
    experience += amount;
    // 检查是否升级
    checkLevelUp();
  }

  // 检查升级
  void checkLevelUp() {
    int requiredExp = calculateRequiredExp(level);
    while (experience >= requiredExp) {
      level++;
      experience -= requiredExp;
      requiredExp = calculateRequiredExp(level);
    }
  }

  // 计算升级所需经验
  int calculateRequiredExp(int currentLevel) {
    return 100 * currentLevel * currentLevel;
  }

  // 添加物品到背包
  void addItem(String itemId, dynamic item) {
    if (inventory.containsKey(itemId)) {
      if (inventory[itemId] is int) {
        inventory[itemId]++;
      } else {
        inventory[itemId] = item;
      }
    } else {
      inventory[itemId] = item;
    }
  }

  // 使用物品
  bool useItem(String itemId) {
    if (!inventory.containsKey(itemId)) return false;
    
    if (inventory[itemId] is int) {
      if (inventory[itemId] > 0) {
        inventory[itemId]--;
        if (inventory[itemId] <= 0) {
          inventory.remove(itemId);
        }
        return true;
      }
    }
    return false;
  }

  // 提升技能等级
  void improveSkill(String skillName) {
    if (skills.containsKey(skillName)) {
      skills[skillName] = (skills[skillName] ?? 0) + 1;
    }
  }

  // 添加成就
  void addAchievement(String achievement) {
    if (!achievements.contains(achievement)) {
      achievements.add(achievement);
    }
  }

  // 更新统计数据
  void updateStats(String stat, dynamic value) {
    if (stats.containsKey(stat)) {
      if (value is int) {
        stats[stat] += value;
      } else {
        stats[stat] = value;
      }
    }
  }

  // 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nickname': nickname,
      'avatarUrl': avatarUrl,
      'level': level,
      'experience': experience,
      'points': points,
      'inventory': inventory,
      'skills': skills,
      'achievements': achievements,
      'stats': stats,
    };
  }

  // 从JSON创建
  factory Player.fromJson(Map<String, dynamic> json) {
    return Player(
      id: json['id'],
      nickname: json['nickname'],
      avatarUrl: json['avatarUrl'],
      level: json['level'] ?? 1,
      experience: json['experience'] ?? 0,
      points: json['points'] ?? 0,
      inventory: json['inventory'] ?? {},
      skills: Map<String, int>.from(json['skills'] ?? {}),
      achievements: List<String>.from(json['achievements'] ?? []),
      stats: json['stats'] ?? {},
    );
  }
} 