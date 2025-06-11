import React, { useState, useEffect, useCallback } from "react"
import { SafeAreaView  } from "react-native-safe-area-context"
import Icon from "../common/Icon"
import { colors } from "../../constants/theme"
import { cornMazeService } from "../../services/cornMazeService"
import {ViewText,
StyleSheet,
ScrollView,
TouchableOpacity,"
RefreshControl,";
} fromimensions;'}
} from "react-native;
MazeStats,
LeaderboardEntry,
MazeTheme,
MazeDifficulty;
} from "../../types/maze"
const { width } = Dimensions.get('window');
interface MazeStatsScreenProps {
navigation: any,
}
  const userId = string}
}
const MazeStatsScreen: React.FC<Suspense fallback={<LoadingSpinner  />}><MazeStatsScreenProps></Suspense> = ({  navigation, userId ; }) => {/const [stats, setStats] = useState<MazeStats | null>(null),/g/;
const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
const [loading, setLoading] = useState(true);
const [refreshing, setRefreshing] = useState(false);
const [selectedTab, setSelectedTab] = useState<'stats' | 'leaderboard'>('stats');
  // 主题配置'
const  themeConfig = {[MazeTheme.HEALTH_PATH]: {'}
color: '#4CAF50,'
}
      const icon = 'heart-pulse'}
    ;},[MazeTheme.NUTRITION_GARDEN]: {'}
}
      color: '#FF9800',icon: 'food-apple}
    },[MazeTheme.TCM_JOURNEY]: {'}
}
      color: '#9C27B0',icon: 'leaf}
    },[MazeTheme.BALANCED_LIFE]: {'}
}
      color: '#2196F3',icon: 'scale-balance}
    };
  };
  // 加载数据
const loadData = useCallback(async () => {try {setLoading(true);)const [userStats, globalLeaderboard] = await Promise.all([;);)]cornMazeService.getUserStats(userId),cornMazeService.getLeaderboard(undefined, 20);
];
      ]);
setStats(userStats);
}
      setLeaderboard(globalLeaderboard)}
    } catch (error) {}
}
    } finally {}
      setLoading(false)}
    }
  }, [userId]);
  // 刷新数据
const onRefresh = useCallback(async () => {setRefreshing(true);)const await = loadData();
}
    setRefreshing(false)}
  }, [loadData]);
useEffect() => {}
    loadData()}
  }, [loadData]);
  // 渲染统计卡片/,/g,/;
  renderStatsCard: (title: string, value: string | number, icon: string, color: string) => (;);
    <View style={[styles.statsCard, { borderLeftColor: color ;}}]}>;
      <View style={styles.statsIcon}>;
        <Icon name={icon} size={24} color={color}  />;
      </View>;
      <View style={styles.statsContent}>;
        <Text style={styles.statsValue}>{value}</Text>;
        <Text style={styles.statsTitle}>{title}</Text>;
      </View>;
    </View>;
  );
  // 渲染成就徽章
const renderAchievementBadge = (achievement: string) => (;)
    <View key={achievement} style={styles.achievementBadge}>;
      <Icon name="trophy" size={16} color={colors.warning}  />;"/;"/g"/;
      <Text style={styles.achievementText}>{achievement}</Text>;
    </View>;
  );
  // 渲染排行榜条目"/,"/g,"/;
  renderLeaderboardEntry: (entry: LeaderboardEntry, index: number) => {const isCurrentUser = entry.userId === userId;"rankColor: index < 3 ? ["#FFD700",#C0C0C0', '#CD7F32'][index] : colors.textSecondary;
}
    return (<View;}  />/,)key={entry.userId}/g/;
        style={[]styles.leaderboardEntry,}
          isCurrentUser && styles.currentUserEntry}
];
        ]}
      >;
        <View style={styles.rankContainer}>;
          <Text style={[styles.rankText, { color: rankColor ;}}]}>;
            #{entry.rank}
          </Text>'/;'/g'/;
          {index < 3  && <Icon;'}''  />/,'/g'/;
name={index === 0 ? "crown" : "medal"};
size={16});
color={rankColor});
            />)
          )}
        </View>
        <View style={styles.userInfo}>;
          <Text style={[styles.username, isCurrentUser && styles.currentUserText]}>;
            {entry.username};
          </Text>;
          <Text style={styles.mazeName}>{entry.mazeName}</Text>;
        </View>;
        <View style={styles.scoreContainer}>;
          <Text style={[styles.score, isCurrentUser && styles.currentUserText]}>;
          </Text>;"/;"/g"/;
          <Text style={styles.completionTime}>;
            {Math.floor(entry.completionTime / 60)}:{(entry.completionTime % 60).toString().padStart(2, '0')};'/;'/g'/;
          </Text>;
        </View>;
      </View>;
    );
  };
  // 格式化游戏时间
    }
    const hours = Math.floor(minutes / 60);
const remainingMinutes = minutes % 60;
  };
return (<SafeAreaView style={styles.container}>);
      <View style={styles.header}>)
        <TouchableOpacity onPress={() => navigation.goBack()}>'
          <Icon name="arrow-left" size={24} color={colors.text}  />"/;"/g"/;
        </TouchableOpacity>
        <Text style={styles.title}>游戏统计</Text>
        <View style={ width: 24 ;}}  />
      </View>"
      <View style={styles.tabContainer}>
        <TouchableOpacity;"  />"
style={[styles.tab, selectedTab === 'stats' && styles.activeTab]}
onPress={() => setSelectedTab('stats')}
        >'
          <Text style={[styles.tabText, selectedTab === 'stats' && styles.activeTabText]}>
          </Text>'
        </TouchableOpacity>'/;'/g'/;
        <TouchableOpacity;'  />/,'/g'/;
style={[styles.tab, selectedTab === 'leaderboard' && styles.activeTab]}
onPress={() => setSelectedTab('leaderboard')}
        >'
          <Text style={[styles.tabText, selectedTab === 'leaderboard' && styles.activeTabText]}>
          </Text>
        </TouchableOpacity>
      </View>
      <ScrollView;  />
style={styles.content}
        refreshControl={}
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh}  />
        }
      >'
        {selectedTab === 'stats' && stats  && <View style={styles.statsSection}>
            {// 基础统计}
            <View style={styles.statsGrid}>;
            </View>
            {// 等级和排名}
            {(stats.level || stats.rank)  && <View style={styles.levelSection}>;
                <Text style={styles.sectionTitle}>等级信息</Text>
                <View style={styles.levelCard}>
                  {stats.level  && <View style={styles.levelInfo}>'
                      <Icon name="trending-up" size={32} color={colors.primary}  />"/;"/g"/;
                      <View style={styles.levelText}>;
                        <Text style={styles.levelNumber}>等级 {stats.level}</Text>
                        <Text style={styles.levelDescription}>继续努力提升等级</Text>
                      </View>
                    </View>"
                  )}
                  {stats.rank  && <View style={styles.rankInfo}>
                      <Icon name="trophy" size={32} color={colors.warning}  />"/;"/g"/;
                      <View style={styles.rankText}>;
                        <Text style={styles.rankNumber}>排名 #{stats.rank}</Text>
                        <Text style={styles.rankDescription}>全球排名</Text>
                      </View>
                    </View>
                  )}
                </View>
              </View>
            )}
            {// 喜爱主题}
            <View style={styles.favoriteSection}>;
              <Text style={styles.sectionTitle}>喜爱主题</Text>
              <View style={styles.favoriteCard}>;
                <Icon;  />
name={themeConfig[stats.favoriteTheme].icon}
                  size={32}
                  color={themeConfig[stats.favoriteTheme].color}
                />
                <View style={styles.favoriteText}>;
                  <Text style={styles.favoriteName}>;
                    {themeConfig[stats.favoriteTheme].name}
                  </Text>
                  <Text style={styles.favoriteDescription}>;
                  </Text>
                </View>
              </View>
            </View>
            {// 成就}
            {stats.achievements.length > 0  && <View style={styles.achievementsSection}>;
                <Text style={styles.sectionTitle}>获得成就</Text>
                <View style={styles.achievementsList}>;
                  {stats.achievements.map(renderAchievementBadge)}
                </View>
              </View>
            )}
          </View>"/;"/g"/;
        )}
        {selectedTab === 'leaderboard'  && <View style={styles.leaderboardSection}>
            <Text style={styles.sectionTitle}>全球排行榜</Text>;
            {leaderboard.length > 0 ? (;)}
              <View style={styles.leaderboardList}>;
                {leaderboard.map(renderLeaderboardEntry)};
              </View>;
            ) : (;';)              <View style={styles.emptyState}>;
                <Icon name="trophy" size={64} color={colors.textSecondary}  />;"/;"/g"/;
                <Text style={styles.emptyText}>暂无排行榜数据</Text>;)
                <Text style={styles.emptySubtext}>完成更多迷宫来上榜吧</Text>;)
              </View>;)
            )};
          </View>;
        )};
      </ScrollView>;
    </SafeAreaView>;
  );
};
const  styles = StyleSheet.create({)container: {flex: 1,
}
    const backgroundColor = colors.background}
  },","
header: {,"flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'';
paddingHorizontal: 20,
paddingVertical: 16,
borderBottomWidth: 1,
}
    const borderBottomColor = colors.border}
  }
title: {,'fontSize: 18,'
fontWeight: '600,'
}
    const color = colors.text}
  },'
tabContainer: {,'flexDirection: 'row,'';
backgroundColor: colors.surface,
marginHorizontal: 20,
marginTop: 16,
borderRadius: 12,
}
    const padding = 4}
  }
tab: {flex: 1,
paddingVertical: 12,'
alignItems: 'center,'
}
    const borderRadius = 8}
  }
activeTab: {,}
  const backgroundColor = colors.primary}
  }
tabText: {,'fontSize: 14,'
fontWeight: '600,'
}
    const color = colors.textSecondary}
  }
activeTabText: {,}
  const color = colors.white}
  }
content: {flex: 1,
}
    const paddingHorizontal = 20}
  }
statsSection: {,}
  const paddingVertical = 16}
  },'
statsGrid: {,'flexDirection: 'row,'
flexWrap: 'wrap,'
justifyContent: 'space-between,'
}
    const marginBottom = 24}
  },'
statsCard: {,'width: '48%,'';
backgroundColor: colors.surface,
borderRadius: 12,
padding: 16,
marginBottom: 12,
borderLeftWidth: 4,'
flexDirection: 'row,'
alignItems: 'center,'';
elevation: 2,
}
    shadowColor: '#000,}'';
shadowOffset: { width: 0, height: 2 }
shadowOpacity: 0.1,
const shadowRadius = 4;
  }
statsIcon: {,}
  const marginRight = 12}
  }
statsContent: {,}
  const flex = 1}
  }
statsValue: {,'fontSize: 20,'
fontWeight: 'bold,'
}
    const color = colors.text}
  }
statsTitle: {fontSize: 12,
color: colors.textSecondary,
}
    const marginTop = 2}
  }
sectionTitle: {,'fontSize: 16,'
fontWeight: '600,'';
color: colors.text,
}
    const marginBottom = 12}
  }
levelSection: {,}
  const marginBottom = 24}
  }
levelCard: {backgroundColor: colors.surface,
borderRadius: 12,
padding: 16,
elevation: 2,
}
    shadowColor: '#000,'}'';
shadowOffset: { width: 0, height: 2 }
shadowOpacity: 0.1,
const shadowRadius = 4;
  },'
levelInfo: {,'flexDirection: 'row,'
alignItems: 'center,'
}
    const marginBottom = 16}
  }
levelText: {marginLeft: 16,
}
    const flex = 1}
  }
levelNumber: {,'fontSize: 18,'
fontWeight: 'bold,'
}
    const color = colors.text}
  }
levelDescription: {fontSize: 14,
color: colors.textSecondary,
}
    const marginTop = 2}
  },'
rankInfo: {,'flexDirection: 'row,'
}
    const alignItems = 'center'}
  }
rankText: {marginLeft: 16,
}
    const flex = 1}
  }
rankNumber: {,'fontSize: 18,'
fontWeight: 'bold,'
}
    const color = colors.text}
  }
rankDescription: {fontSize: 14,
color: colors.textSecondary,
}
    const marginTop = 2}
  }
favoriteSection: {,}
  const marginBottom = 24}
  }
favoriteCard: {backgroundColor: colors.surface,
borderRadius: 12,
padding: 16,'
flexDirection: 'row,'
alignItems: 'center,'';
elevation: 2,
}
    shadowColor: '#000,'}'';
shadowOffset: { width: 0, height: 2 }
shadowOpacity: 0.1,
const shadowRadius = 4;
  }
favoriteText: {marginLeft: 16,
}
    const flex = 1}
  }
favoriteName: {,'fontSize: 16,'
fontWeight: '600,'
}
    const color = colors.text}
  }
favoriteDescription: {fontSize: 14,
color: colors.textSecondary,
}
    const marginTop = 2}
  }
achievementsSection: {,}
  const marginBottom = 24}
  },'
achievementsList: {,'flexDirection: 'row,'
}
    const flexWrap = 'wrap'}
  ;},'
achievementBadge: {,'flexDirection: 'row,'
alignItems: 'center,'';
backgroundColor: colors.surface,
borderRadius: 20,
paddingHorizontal: 12,
paddingVertical: 6,
marginRight: 8,
marginBottom: 8,
elevation: 1,
}
    shadowColor: '#000,}'';
shadowOffset: { width: 0, height: 1 }
shadowOpacity: 0.05,
const shadowRadius = 2;
  }
achievementText: {,'fontSize: 12,'
fontWeight: '500,'';
color: colors.text,
}
    const marginLeft = 4}
  }
leaderboardSection: {,}
  const paddingVertical = 16}
  }
leaderboardList: {backgroundColor: colors.surface,
borderRadius: 12,'
overflow: 'hidden,'';
elevation: 2,
}
    shadowColor: '#000,'}'';
shadowOffset: { width: 0, height: 2 }
shadowOpacity: 0.1,
const shadowRadius = 4;
  },'
leaderboardEntry: {,'flexDirection: 'row,'
alignItems: 'center,'';
paddingHorizontal: 16,
paddingVertical: 12,
borderBottomWidth: 1,
}
    const borderBottomColor = colors.border}
  },'
currentUserEntry: {,';}}
  const backgroundColor = colors.primary + '10'}
  ;},'
rankContainer: {,'flexDirection: 'row,'
alignItems: 'center,'
}
    const width = 60}
  }
userInfo: {flex: 1,
}
    const marginLeft = 12}
  }
username: {,'fontSize: 16,'
fontWeight: '600,'
}
    const color = colors.text}
  }
currentUserText: {,}
  const color = colors.primary}
  }
mazeName: {fontSize: 12,
color: colors.textSecondary,
}
    const marginTop = 2}
  },'
scoreContainer: {,';}}
  const alignItems = 'flex-end'}
  }
score: {,'fontSize: 16,'
fontWeight: 'bold,'
}
    const color = colors.text}
  }
completionTime: {fontSize: 12,
color: colors.textSecondary,
}
    const marginTop = 2}
  },'
emptyState: {,'alignItems: "center,
}
      const paddingVertical = 60;"};
  },emptyText: {fontSize: 18,fontWeight: '600',color: colors.textSecondary,marginTop: 16;')}
  },emptySubtext: {fontSize: 14,color: colors.textSecondary,marginTop: 8,textAlign: 'center)}
  };);
});
export default MazeStatsScreen;