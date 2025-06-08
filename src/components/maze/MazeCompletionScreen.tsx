import React, { useState, useEffect } from 'react';
import {import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from '../common/Icon';
import { colors } from '../../constants/theme';
import {View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Dimensions,
  ScrollView;
} from 'react-native';
  GameReward,
  MazeTheme,
  MazeDifficulty,
  MazeStats;
} from '../../types/maze';
const { width, height } = Dimensions.get('window');
interface MazeCompletionScreenProps {
  navigation: any;
  route: {;
    params: {;
  score: number;
      completionTime: number;
  stepsCount: number;
      theme: MazeTheme;
  difficulty: MazeDifficulty;
      rewards: GameReward[];
      isNewRecord?: boolean;
      mazeName: string;
      onPlayAgain?: () => void;
      onBackToMenu?: () => void;
};
  };
}
const MazeCompletionScreen: React.FC<MazeCompletionScreenProps> = ({
  navigation,
  route;
}) => {
  const {
    score,
    completionTime,
    stepsCount,
    theme,
    difficulty,
    rewards,
    isNewRecord,
    mazeName,
    onPlayAgain,
    onBackToMenu;
  } = route.params;
  const [animatedValue] = useState(new Animated.Value(0));
  const [scoreAnimatedValue] = useState(new Animated.Value(0));
  const [showDetails, setShowDetails] = useState(false);
  // 主题配置
  const themeConfig = {
    [MazeTheme.HEALTH_PATH]: {
      name: "健康之路",
      color: '#4CAF50',
      gradient: ["#4CAF50",#81C784'],
      icon: 'heart-pulse'
    },
    [MazeTheme.NUTRITION_GARDEN]: {
      name: "营养花园",
      color: '#FF9800',gradient: ["#FF9800",#FFB74D'],icon: 'food-apple';
    },[MazeTheme.TCM_JOURNEY]: {
      name: "中医之旅",
      color: '#9C27B0',gradient: ["#9C27B0",#BA68C8'],icon: 'leaf';
    },[MazeTheme.BALANCED_LIFE]: {
      name: "平衡生活",
      color: '#2196F3',gradient: ["#2196F3",#64B5F6'],icon: 'scale-balance';
    };
  };
  // 难度配置
  const difficultyConfig = {[MazeDifficulty.EASY]: {
      name: "简单",
      multiplier: 1 },[MazeDifficulty.NORMAL]: {
      name: "普通",
      multiplier: 1.5 },[MazeDifficulty.HARD]: {
      name: "困难",
      multiplier: 2 },[MazeDifficulty.EXPERT]: {
      name: "专家",
      multiplier: 3 };
  };
  useEffect() => {
    // 启动动画
    Animated.sequence([
      Animated.timing(animatedValue, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true;
      }),
      Animated.timing(scoreAnimatedValue, {
        toValue: score,
        duration: 1500,
        useNativeDriver: false;
      });
    ]).start();
    // 延迟显示详细信息
    const timer = setTimeout() => {setShowDetails(true);
    }, 1000);
    return () => clearTimeout(timer);
  }, [animatedValue, scoreAnimatedValue, score]);
  // 格式化时间
  const formatTime = (seconds: number): string => {const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };
  // 计算星级评分
  const getStarRating = (): number => {const baseScore = 1000;
    const timeBonus = Math.max(0, baseScore - completionTime * 2);
    const stepBonus = Math.max(0, baseScore - stepsCount * 5);
    const totalScore = score + timeBonus + stepBonus;
    if (totalScore >= 2500) return 3;
    if (totalScore >= 1500) return 2;
    return 1;
  };
  // 渲染星级
  const renderStars = () => {const stars = getStarRating();
    return (;
      <View style={styles.starsContainer}>;
        {[1, 2, 3].map(star) => (;
          <Animated.View;
            key={star};
            style={[;
              styles.star,{opacity: animatedValue,transform: [;
                  {scale: animatedValue.interpolate({inputRange: [0, 1],outputRange: [0, star <= stars ? 1.2 : 0.3];
                    });
                  }
                ]
              }
            ]}
          >
            <Icon;
              name="star"
              size={32}
              color={star <= stars ? colors.warning : colors.textSecondary}
            />
          </Animated.View>
        ))}
      </View>;
    );
  };
  // 渲染奖励
  const renderRewards = () => {if (!rewards || rewards.length === 0) return null;
    return (
      <View style={styles.rewardsSection}>;
        <Text style={styles.sectionTitle}>获得奖励</Text>;
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>;
          {rewards.map((reward, index) => (;
            <Animated.View;
              key={index};
              style={[;
                styles.rewardCard,{opacity: animatedValue,transform: [;
                    {translateY: animatedValue.interpolate({inputRange: [0, 1],outputRange: [50, 0];
                      });
                    }
                  ]
                }
              ]}
            >
              <View style={styles.rewardIcon}>
                <Icon name="gift" size={24} color={colors.primary} />
              </View>
              <Text style={styles.rewardName}>{reward.name}</Text>
              <Text style={styles.rewardDescription}>{reward.description}</Text>
            </Animated.View>
          ))}
        </ScrollView>
      </View>;
    );
  };
  // 渲染统计详情
  const renderStats = () => {if (!showDetails) return null;
    return (;
      <Animated.View;
        style={[;
          styles.statsSection,{opacity: animatedValue,transform: [;
              {translateY: animatedValue.interpolate({inputRange: [0, 1],outputRange: [30, 0];
                });
              }
            ]
          }
        ]}
      >
        <Text style={styles.sectionTitle}>游戏统计</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Icon name="clock" size={20} color={colors.info} />
            <Text style={styles.statValue}>{formatTime(completionTime)}</Text>
            <Text style={styles.statLabel}>完成时间</Text>
          </View>
          <View style={styles.statCard}>
            <Icon name="footsteps" size={20} color={colors.success} />
            <Text style={styles.statValue}>{stepsCount}</Text>
            <Text style={styles.statLabel}>步数</Text>
          </View>
          <View style={styles.statCard}>
            <Icon name="trending-up" size={20} color={colors.warning} />
            <Text style={styles.statValue}>{difficultyConfig[difficulty].name}</Text>
            <Text style={styles.statLabel}>难度</Text>
          </View>
        </View>
      </Animated.View>;
    );
  };
  return (;
    <SafeAreaView style={styles.container}>;
      <ScrollView contentContainerStyle={styles.content}>;
        {// 背景装饰};
        <View style={styles.backgroundDecoration}>;
          <Animated.View;
            style={[;
              styles.celebrationCircle,{transform: [;
                  {scale: animatedValue.interpolate({inputRange: [0, 1],outputRange: [0, 1];
                    });
                  }
                ],
                backgroundColor: themeConfig[theme].color + '20'
              }
            ]}
          />
        </View>
        {// 完成标题}
        <Animated.View;
          style={[
            styles.titleSection,
            {
              opacity: animatedValue,
              transform: [
                {
                  translateY: animatedValue.interpolate({,
  inputRange: [0, 1],
                    outputRange: [-50, 0]
                  });
                }
              ]
            }
          ]}
        >
          <Icon;
            name="check-circle"
            size={64}
            color={themeConfig[theme].color}
          />
          <Text style={styles.congratsText}>恭喜完成！</Text>
          <Text style={styles.mazeNameText}>{mazeName}</Text>
          {isNewRecord && (
        <View style={styles.newRecordBadge}>
              <Icon name="trophy" size={16} color={colors.warning} />
              <Text style={styles.newRecordText}>新纪录！</Text>
            </View>
          )}
        </Animated.View>
        {// 分数显示}
        <Animated.View style={styles.scoreSection}>
          <Text style={styles.scoreLabel}>最终得分</Text>
          <Animated.Text style={styles.scoreValue}>
            {scoreAnimatedValue}
          </Animated.Text>
          {renderStars()}
        </Animated.View>
        {// 统计信息}
        {renderStats()}
        {// 奖励展示}
        {renderRewards()}
        {// 操作按钮}
        <View style={styles.actionsSection}>
          <TouchableOpacity;
            style={[styles.actionButton, styles.secondaryButton]}
            onPress={() => {onPlayAgain?.();
              navigation.goBack();
            }}
          >
            <Icon name="refresh" size={20} color={colors.primary} />
            <Text style={styles.secondaryButtonText}>再玩一次</Text>
          </TouchableOpacity>
          <TouchableOpacity;
            style={[styles.actionButton, styles.primaryButton]}
            onPress={() => {
              onBackToMenu?.();
              navigation.navigate('MazeMain');
            }}
          >
            <Icon name="home" size={20} color={colors.white} />
            <Text style={styles.primaryButtonText}>返回主页</Text>
          </TouchableOpacity>
        </View>
        {// 分享按钮}
        <TouchableOpacity;
          style={styles.shareButton}
          onPress={() => {
            // 实现分享功能
            console.log('分享游戏结果');
          }}
        >
          <Icon name="share" size={20} color={colors.primary} />
          <Text style={styles.shareButtonText}>分享成绩</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: colors.background;
  },
  content: {,
  flexGrow: 1,
    paddingHorizontal: 20,
    paddingVertical: 20;
  },
  backgroundDecoration: {,
  position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    alignItems: 'center',
    justifyContent: 'center'
  },
  celebrationCircle: {,
  width: width * 1.5,
    height: width * 1.5,
    borderRadius: width * 0.75,
    position: 'absolute'
  },
  titleSection: {,
  alignItems: 'center',
    marginTop: 40,
    marginBottom: 30;
  },
  congratsText: {,
  fontSize: 28,
    fontWeight: 'bold',
    color: colors.text,
    marginTop: 16,
    textAlign: 'center'
  },
  mazeNameText: {,
  fontSize: 18,
    color: colors.textSecondary,
    marginTop: 8,
    textAlign: 'center'
  },
  newRecordBadge: {,
  flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.warning + '20',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    marginTop: 12;
  },
  newRecordText: {,
  fontSize: 14,
    fontWeight: '600',
    color: colors.warning,
    marginLeft: 4;
  },
  scoreSection: {,
  alignItems: 'center',
    marginBottom: 30;
  },
  scoreLabel: {,
  fontSize: 16,
    color: colors.textSecondary,
    marginBottom: 8;
  },
  scoreValue: {,
  fontSize: 48,
    fontWeight: 'bold',
    color: colors.primary,
    marginBottom: 16;
  },
  starsContainer: {,
  flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center'
  },
  star: {,
  marginHorizontal: 4;
  },
  sectionTitle: {,
  fontSize: 18,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 16,
    textAlign: 'center'
  },
  statsSection: {,
  marginBottom: 30;
  },
  statsGrid: {,
  flexDirection: 'row',
    justifyContent: 'space-around'
  },
  statCard: {,
  alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
    minWidth: 80,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4;
  },
  statValue: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: colors.text,
    marginTop: 8,
    marginBottom: 4;
  },
  statLabel: {,
  fontSize: 12,
    color: colors.textSecondary,
    textAlign: 'center'
  },
  rewardsSection: {,
  marginBottom: 30;
  },
  rewardCard: {,
  backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
    marginRight: 12,
    width: 120,
    alignItems: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4;
  },
  rewardIcon: {,
  width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.primary + '20',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8;
  },
  rewardName: {,
  fontSize: 14,
    fontWeight: '600',
    color: colors.text,
    textAlign: 'center',
    marginBottom: 4;
  },
  rewardDescription: {,
  fontSize: 12,
    color: colors.textSecondary,
    textAlign: 'center'
  },
  actionsSection: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20;
  },
  actionButton: {,
  flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    marginHorizontal: 6;
  },
  primaryButton: {,
  backgroundColor: colors.primary;
  },
  secondaryButton: {,
  backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.primary;
  },
  primaryButtonText: {,
  fontSize: 16,
    fontWeight: '600',
    color: colors.white,
    marginLeft: 8;
  },
  secondaryButtonText: {,
  fontSize: 16,
    fontWeight: '600',
    color: colors.primary,
    marginLeft: 8;
  },shareButton: {
      flexDirection: "row",
      alignItems: 'center',justifyContent: 'center',paddingVertical: 12,borderRadius: 8,backgroundColor: colors.surface;
  },shareButtonText: {fontSize: 14,fontWeight: '500',color: colors.primary,marginLeft: 8;
  };
});
export default MazeCompletionScreen;