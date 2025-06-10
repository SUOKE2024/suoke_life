import React, { useState, useEffect } from "react";";
import {import { SafeAreaView } from "react-native-safe-area-context";";
import Icon from "../common/Icon";""/;,"/g"/;
import { colors } from "../../constants/theme";""/;,"/g"/;
import {View;,}Text,;
StyleSheet,;
TouchableOpacity,;
Animated,;
Dimensions,";"";
}
  ScrollView;'}'';'';
} from "react-native";";
GameReward,;
MazeTheme,;
MazeDifficulty,';,'';
MazeStats;';'';
} from "../../types/maze";""/;,"/g"/;
const { width, height } = Dimensions.get('window');';,'';
interface MazeCompletionScreenProps {navigation: any}route: {params: {score: number,;
completionTime: number,;
stepsCount: number,;
theme: MazeTheme,;
difficulty: MazeDifficulty,;
const rewards = GameReward[];
isNewRecord?: boolean;
const mazeName = string;
onPlayAgain?: () => void;
}
}
      onBackToMenu?: () => void;}
};
  };
}
const  MazeCompletionScreen: React.FC<Suspense fallback={<LoadingSpinner  />}><MazeCompletionScreenProps></Suspense> = ({/;));,}navigation,);/g/;
}
  route;)}
}) => {const {}    score,;
completionTime,;
stepsCount,;
theme,;
difficulty,;
rewards,;
isNewRecord,;
mazeName,;
onPlayAgain,;
};
onBackToMenu;}
  } = route.params;
const [animatedValue] = useState(new Animated.Value(0));
const [scoreAnimatedValue] = useState(new Animated.Value(0));
const [showDetails, setShowDetails] = useState(false);
  // 主题配置/;,/g/;
const  themeConfig = {[MazeTheme.HEALTH_PATH]: {';}';,'';
color: '#4CAF50';','';
gradient: ["#4CAF50",#81C784'],'';'';
}
      const icon = 'heart-pulse'}'';'';
    ;}
    [MazeTheme.NUTRITION_GARDEN]: {';}';'';
}
      color: '#FF9800',gradient: ["#FF9800",#FFB74D'],icon: 'food-apple';'}'';'';
    },[MazeTheme.TCM_JOURNEY]: {';}';'';
}
      color: '#9C27B0',gradient: ["#9C27B0",#BA68C8'],icon: 'leaf';'}'';'';
    },[MazeTheme.BALANCED_LIFE]: {';}';'';
}
      color: '#2196F3',gradient: ["#2196F3",#64B5F6'],icon: 'scale-balance';'}'';'';
    };
  };
  // 难度配置/;,/g/;
const  difficultyConfig = {[MazeDifficulty.EASY]: {}}
}
      multiplier: 1 ;},[MazeDifficulty.NORMAL]: {}}
}
      multiplier: 1.5 ;},[MazeDifficulty.HARD]: {}}
}
      multiplier: 2 ;},[MazeDifficulty.EXPERT]: {}}
}
      const multiplier = 3 ;};
  };
useEffect() => {// 启动动画/;,}Animated.sequence([;));,]Animated.timing(animatedValue, {)        toValue: 1,);,}duration: 800,);/g/;
}
        const useNativeDriver = true;)}
      }),;
Animated.timing(scoreAnimatedValue, {)toValue: score,);,}duration: 1500,);
}
        const useNativeDriver = false;)}
      });
];
    ]).start();
    // 延迟显示详细信息/;,/g/;
const timer = setTimeout() => {setShowDetails(true);}
    }, 1000);
return () => clearTimeout(timer);
  }, [animatedValue, scoreAnimatedValue, score]);
  // 格式化时间/;,/g/;
const formatTime = (seconds: number): string => {const minutes = Math.floor(seconds / 60);'/;}}'/g'/;
    const remainingSeconds = seconds % 60;'}'';
return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;````;```;
  };
  // 计算星级评分/;,/g/;
const getStarRating = (): number => {const baseScore = 1000;,}timeBonus: Math.max(0, baseScore - completionTime * 2);
stepBonus: Math.max(0, baseScore - stepsCount * 5);
const totalScore = score + timeBonus + stepBonus;
if (totalScore >= 2500) return 3;
if (totalScore >= 1500) return 2;
}
    return 1;}
  };
  // 渲染星级/;,/g/;
const renderStars = useCallback(() => {const stars = getStarRating();}}
    return (;)}
      <View style={styles.starsContainer}>;
        {[1, 2, 3].map(star) => (;);}}
          <Animated.View;}  />/;,/g/;
key={star};
style={[;];,}styles.star,{opacity: animatedValue,transform: [;]}
];
                  {scale: animatedValue.interpolate({inputRange: [0, 1],outputRange: [0, star <= stars ? 1.2 : 0.3];)}
                    }});
                  }
                ];
              }
            ]}
          >';'';
            <Icon;'  />/;,'/g'/;
name="star";
size={32}
              color={star <= stars ? colors.warning : colors.textSecondary}
             />/;/g/;
          </Animated.View>/;/g/;
        ))}
      </View>;/;/g/;
    );
  };
  // 渲染奖励/;,/g/;
const renderRewards = useCallback(() => {if (!rewards || rewards.length === 0) return null;}
    return (<View style={styles.rewardsSection}>;);
        <Text style={styles.sectionTitle}>获得奖励</Text>;)/;/g/;
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>;);
          {rewards.map(reward, index) => (;));}}
            <Animated.View;}  />/;,/g/;
key={index};
style={[;];,}styles.rewardCard,{opacity: animatedValue,transform: [;]}
];
                    {translateY: animatedValue.interpolate({inputRange: [0, 1],outputRange: [50, 0];)}
                      }});
                    }
                  ];
                }
              ]}
            >";"";
              <View style={styles.rewardIcon}>";"";
                <Icon name="gift" size={24} color={colors.primary}  />"/;"/g"/;
              </View>/;/g/;
              <Text style={styles.rewardName}>{reward.name}</Text>/;/g/;
              <Text style={styles.rewardDescription}>{reward.description}</Text>/;/g/;
            </Animated.View>/;/g/;
          ))}
        </ScrollView>/;/g/;
      </View>;/;/g/;
    );
  };
  // 渲染统计详情/;,/g/;
const renderStats = useCallback(() => {if (!showDetails) return null;,}return (;);
      <Animated.View;  />/;,/g/;
style={[;];,}styles.statsSection,{opacity: animatedValue,transform: [;]}
];
              {translateY: animatedValue.interpolate({inputRange: [0, 1],outputRange: [30, 0];)}
                }});
              }
            ];
          }
        ]}
      >;
        <Text style={styles.sectionTitle}>游戏统计</Text>/;/g/;
        <View style={styles.statsGrid}>";"";
          <View style={styles.statCard}>";"";
            <Icon name="clock" size={20} color={colors.info}  />"/;"/g"/;
            <Text style={styles.statValue}>{formatTime(completionTime)}</Text>/;/g/;
            <Text style={styles.statLabel}>完成时间</Text>/;/g/;
          </View>"/;"/g"/;
          <View style={styles.statCard}>";"";
            <Icon name="footsteps" size={20} color={colors.success}  />"/;"/g"/;
            <Text style={styles.statValue}>{stepsCount}</Text>/;/g/;
            <Text style={styles.statLabel}>步数</Text>/;/g/;
          </View>"/;"/g"/;
          <View style={styles.statCard}>";"";
            <Icon name="trending-up" size={20} color={colors.warning}  />"/;"/g"/;
            <Text style={styles.statValue}>{difficultyConfig[difficulty].name}</Text>/;/g/;
            <Text style={styles.statLabel}>难度</Text>/;/g/;
          </View>/;/g/;
        </View>/;/g/;
      </Animated.View>;/;/g/;
    );
  };
return (;);
    <SafeAreaView style={styles.container}>;
      <ScrollView contentContainerStyle={styles.content}>;
        {// 背景装饰};/;/g/;
        <View style={styles.backgroundDecoration}>;
          <Animated.View;  />/;,/g/;
style={[;];,}styles.celebrationCircle,{transform: [;]}
];
                  {scale: animatedValue.interpolate({inputRange: [0, 1],outputRange: [0, 1];)}
                    }});
                  }";"";
                ],";,"";
const backgroundColor = themeConfig[theme].color + '20'';'';
              ;}
            ]}
          />/;/g/;
        </View>/;/g/;
        {// 完成标题}/;/g/;
        <Animated.View;  />/;,/g/;
style={[;,]styles.titleSection,;}            {opacity: animatedValue}const transform = [;]                {translateY: animatedValue.interpolate({),;}];
inputRange: [0, 1],;
}
                    outputRange: [-50, 0]}
                  ;}});
                }
              ];
            }
          ]}
        >';'';
          <Icon;'  />/;,'/g'/;
name="check-circle";
size={64}
            color={themeConfig[theme].color}
          />/;/g/;
          <Text style={styles.congratsText}>恭喜完成！</Text>/;/g/;
          <Text style={styles.mazeNameText}>{mazeName}</Text>"/;"/g"/;
          {isNewRecord  && <View style={styles.newRecordBadge}>";"";
              <Icon name="trophy" size={16} color={colors.warning}  />"/;"/g"/;
              <Text style={styles.newRecordText}>新纪录！</Text>/;/g/;
            </View>/;/g/;
          )}
        </Animated.View>/;/g/;
        {// 分数显示}/;/g/;
        <Animated.View style={styles.scoreSection}>;
          <Text style={styles.scoreLabel}>最终得分</Text>/;/g/;
          <Animated.Text style={styles.scoreValue}>;
            {scoreAnimatedValue}
          </Animated.Text>/;/g/;
          {renderStars()}
        </Animated.View>/;/g/;
        {// 统计信息}/;/g/;
        {renderStats()}
        {// 奖励展示}/;/g/;
        {renderRewards()}
        {// 操作按钮}/;/g/;
        <View style={styles.actionsSection}>;
          <TouchableOpacity;  />/;,/g/;
style={[styles.actionButton, styles.secondaryButton]}
            onPress={() => {onPlayAgain?.();}}
              navigation.goBack();}
            }}";"";
          >";"";
            <Icon name="refresh" size={20} color={colors.primary}  />"/;"/g"/;
            <Text style={styles.secondaryButtonText}>再玩一次</Text>/;/g/;
          </TouchableOpacity>/;/g/;
          <TouchableOpacity;  />/;,/g/;
style={[styles.actionButton, styles.primaryButton]}
            onPress={() => {";,}onBackToMenu?.();";"";
}
              navigation.navigate('MazeMain');'}'';'';
            }}';'';
          >';'';
            <Icon name="home" size={20} color={colors.white}  />"/;"/g"/;
            <Text style={styles.primaryButtonText}>返回主页</Text>/;/g/;
          </TouchableOpacity>/;/g/;
        </View>/;/g/;
        {// 分享按钮}/;/g/;
        <TouchableOpacity;  />/;,/g/;
style={styles.shareButton}
          onPress={() => {}            // 实现分享功能/;/g/;
}
}
          }}";"";
        >";"";
          <Icon name="share" size={20} color={colors.primary}  />"/;"/g"/;
          <Text style={styles.shareButtonText}>分享成绩</Text>/;/g/;
        </TouchableOpacity>/;/g/;
      </ScrollView>/;/g/;
    </SafeAreaView>/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {flex: 1,;
}
    const backgroundColor = colors.background;}
  }
content: {flexGrow: 1,;
paddingHorizontal: 20,;
}
    const paddingVertical = 20;}
  },";,"";
backgroundDecoration: {,";,}position: 'absolute';','';
top: 0,;
left: 0,;
right: 0,';,'';
bottom: 0,';,'';
alignItems: 'center';','';'';
}
    const justifyContent = 'center'}'';'';
  ;}
celebrationCircle: {width: width * 1.5,;
height: width * 1.5,';,'';
borderRadius: width * 0.75,';'';
}
    const position = 'absolute'}'';'';
  ;},';,'';
titleSection: {,';,}alignItems: 'center';','';
marginTop: 40,;
}
    const marginBottom = 30;}
  }
congratsText: {,';,}fontSize: 28,';,'';
fontWeight: 'bold';','';
color: colors.text,';,'';
marginTop: 16,';'';
}
    const textAlign = 'center'}'';'';
  ;}
mazeNameText: {fontSize: 18,;
color: colors.textSecondary,';,'';
marginTop: 8,';'';
}
    const textAlign = 'center'}'';'';
  ;},';,'';
newRecordBadge: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
backgroundColor: colors.warning + '20';','';
paddingHorizontal: 12,;
paddingVertical: 6,;
borderRadius: 20,;
}
    const marginTop = 12;}
  }
newRecordText: {,';,}fontSize: 14,';,'';
fontWeight: '600';','';
color: colors.warning,;
}
    const marginLeft = 4;}
  },';,'';
scoreSection: {,';,}alignItems: 'center';','';'';
}
    const marginBottom = 30;}
  }
scoreLabel: {fontSize: 16,;
color: colors.textSecondary,;
}
    const marginBottom = 8;}
  }
scoreValue: {,';,}fontSize: 48,';,'';
fontWeight: 'bold';','';
color: colors.primary,;
}
    const marginBottom = 16;}
  },';,'';
starsContainer: {,';,}flexDirection: 'row';','';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
star: {,;}}
  const marginHorizontal = 4;}
  }
sectionTitle: {,';,}fontSize: 18,';,'';
fontWeight: '600';','';
color: colors.text,';,'';
marginBottom: 16,';'';
}
    const textAlign = 'center'}'';'';
  ;}
statsSection: {,;}}
  const marginBottom = 30;}
  },';,'';
statsGrid: {,';,}flexDirection: 'row';','';'';
}
    const justifyContent = 'space-around'}'';'';
  ;},';,'';
statCard: {,';,}alignItems: 'center';','';
backgroundColor: colors.surface,;
borderRadius: 12,;
padding: 16,;
minWidth: 80,';,'';
elevation: 2,';'';
}
    shadowColor: '#000';','}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
const shadowRadius = 4;
  }
statValue: {,';,}fontSize: 16,';,'';
fontWeight: 'bold';','';
color: colors.text,;
marginTop: 8,;
}
    const marginBottom = 4;}
  }
statLabel: {fontSize: 12,';,'';
color: colors.textSecondary,';'';
}
    const textAlign = 'center'}'';'';
  ;}
rewardsSection: {,;}}
  const marginBottom = 30;}
  }
rewardCard: {backgroundColor: colors.surface,;
borderRadius: 12,;
padding: 16,;
marginRight: 12,';,'';
width: 120,';,'';
alignItems: 'center';','';
elevation: 2,';'';
}
    shadowColor: '#000';',}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
const shadowRadius = 4;
  }
rewardIcon: {width: 48,;
height: 48,';,'';
borderRadius: 24,';,'';
backgroundColor: colors.primary + '20';','';
alignItems: 'center';','';
justifyContent: 'center';','';'';
}
    const marginBottom = 8;}
  }
rewardName: {,';,}fontSize: 14,';,'';
fontWeight: '600';','';
color: colors.text,';,'';
textAlign: 'center';','';'';
}
    const marginBottom = 4;}
  }
rewardDescription: {fontSize: 12,';,'';
color: colors.textSecondary,';'';
}
    const textAlign = 'center'}'';'';
  ;},';,'';
actionsSection: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';'';
}
    const marginBottom = 20;}
  }
actionButton: {,';,}flex: 1,';,'';
flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'center';','';
paddingVertical: 16,;
borderRadius: 12,;
}
    const marginHorizontal = 6;}
  }
primaryButton: {,;}}
  const backgroundColor = colors.primary;}
  }
secondaryButton: {backgroundColor: colors.surface,;
borderWidth: 1,;
}
    const borderColor = colors.primary;}
  }
primaryButtonText: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';
color: colors.white,;
}
    const marginLeft = 8;}
  }
secondaryButtonText: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';
color: colors.primary,;
}
    const marginLeft = 8;}';'';
  },shareButton: {,';,}flexDirection: "row";","";"";
}
      alignItems: 'center',justifyContent: 'center',paddingVertical: 12,borderRadius: 8,backgroundColor: colors.surface;')}'';'';
  },shareButtonText: {fontSize: 14,fontWeight: '500',color: colors.primary,marginLeft: 8;')}'';'';
  };);
});';,'';
export default MazeCompletionScreen;