import React, { useState, useEffect, useCallback } from "react";
import {View,
Text,
StyleSheet,
ScrollView,
TouchableOpacity,
RefreshControl,"
Alert,";
} fromimensions;'}
} from "react-native;
import {  SafeAreaView  } from "react-native-safe-area-context"
import {  useSelector  } from "react-redux"
import { colors } from "../../constants/theme"
import { cornMazeService } from "../../services/cornMazeService"
import {Maze,
MazeTemplate,
MazeTheme,
MazeDifficulty,"
MazeProgress,";
} fromrogressStatus;'}
} from "../../types/maze"
const { width } = Dimensions.get('window');
interface MazeMainScreenProps {
}
  const navigation = any}
}
const MazeMainScreen: React.FC<Suspense fallback={<LoadingSpinner  />}><MazeMainScreenProps></Suspense> = ({  navigation ; }) => {/const [mazes, setMazes] = useState<Maze[]>([]),/g/;
const [templates, setTemplates] = useState<MazeTemplate[]>([]);
const [userProgress, setUserProgress] = useState<MazeProgress[]>([]);
const [loading, setLoading] = useState(true);
const [refreshing, setRefreshing] = useState(false);
const [selectedTab, setSelectedTab] = useState<'my' | 'templates' | 'progress'>('my');
const userId = useSelector(state: any) => state.auth.user?.id || 'guest-user');
  // 主题配置'
const  themeConfig = {[MazeTheme.HEALTH_PATH]: {'}
color: '#4CAF50,'
const icon = 'heart-pulse';
}
}
    }
    [MazeTheme.NUTRITION_GARDEN]: {}
}
    },[MazeTheme.TCM_JOURNEY]: {}
}
    },[MazeTheme.BALANCED_LIFE]: {}
}
    };
  };
const  difficultyConfig = {[MazeDifficulty.EASY]: {';}}'}
color: '#4CAF50' ;},[MazeDifficulty.NORMAL]: {';}}'}
color: '#FF9800' ;},[MazeDifficulty.HARD]: {';}}'}
color: '#F44336' ;},[MazeDifficulty.EXPERT]: {';}}'}
const color = '#9C27B0' ;};
  };
  // 加载数据
const loadData = useCallback(async () => {try {setLoading(true);)const [mazesResponse, templatesResponse] = await Promise.all([;);)]cornMazeService.listMazes(),cornMazeService.listMazeTemplates(undefined, undefined, 1, 20);
];
      ]);
setMazes(mazesResponse.mazes);
setTemplates(templatesResponse.templates);
      // 加载用户进度
const progressPromises = mazesResponse.mazes.map(maze =>;);
cornMazeService.getUserProgress(maze.id, userId).catch() => null);
      );
const progressResults = await Promise.all(progressPromises);
const validProgress = progressResults.filter(Boolean) as any[];
}
      setUserProgress(validProgress.map(p => p.progress))}
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
  // 开始游戏'/,'/g,'/;
  startMaze: async (mazeId: string) => {try {await cornMazeService.startMaze({  userId, mazeId ; });
navigation.navigate('MazeGame', { mazeId, userId });
    } catch (error) {}
}
    }
  };
  // 继续游戏'/,'/g,'/;
  continueMaze: (mazeId: string) => {navigation.navigate('MazeGame', { mazeId, userId ;});
  };
  // 从模板创建迷宫
      });
        [;]{';}}'}
style: 'cancel' ;},
          {}
}
      onPress: () => startMaze(maze.id) }
];
        ];
      );
const await = loadData(); // 刷新列表
    } catch (error) {}
}
    }
  };
  // 渲染迷宫卡片
const renderMazeCard = (maze: Maze) => {const theme = themeConfig[maze.theme]const difficulty = difficultyConfig[maze.difficulty];
const progress = userProgress.find(p => p.mazeId === maze.id);
return (;);
}
      <TouchableOpacity;}  />
key={maze.id};
style={[styles.mazeCard, { borderLeftColor: theme.color ;}}]};
onPress={() => progress?.status === ProgressStatus.IN_PROGRESS ;}          ? continueMaze(maze.id);
}
          : startMaze(maze.id)}
        }
      >;
        <View style={styles.mazeHeader}>;
          <View style={styles.mazeInfo}>;
            <Icon name={theme.icon} size={24} color={theme.color}  />
            <View style={styles.mazeText}>;
              <Text style={styles.mazeName}>{maze.name}</Text>
              <Text style={styles.mazeTheme}>{theme.name}</Text>
            </View>
          </View>
          <View style={[styles.difficultyBadge, { backgroundColor: difficulty.color ;}}]}>;
            <Text style={styles.difficultyText}>{difficulty.name}</Text>
          </View>
        </View>
        {maze.description  && <Text style={styles.mazeDescription}>{maze.description}</Text>
        )}
        <View style={styles.mazeStats}>
          <View style={styles.statItem}>'
            <Icon name="grid" size={16} color={colors.textSecondary}  />"/;"/g"/;
            <Text style={styles.statText}>{maze.size}×{maze.size}</Text>"
          </View>"/;"/g"/;
          <View style={styles.statItem}>
            <Icon name="clock-outline" size={16} color={colors.textSecondary}  />"/;"/g"/;
            <Text style={styles.statText}>{maze.estimatedTime || 15}分钟</Text>
          </View>"
          {progress  && <View style={styles.statItem}>
              <Icon;"  />"
name={progress.status === ProgressStatus.COMPLETED ? "check-circle" : "play-circle"};
size={16}
                color={progress.status === ProgressStatus.COMPLETED ? colors.success : colors.primary}
              />
              <Text style={styles.statText}>;
              </Text>
            </View>
          )}
        </View>
      </TouchableOpacity>;
    );
  };
  // 渲染模板卡片
const renderTemplateCard = (template: MazeTemplate) => {const theme = themeConfig[template.mazeType]const difficulty = difficultyConfig[template.difficulty];
}
    return (<TouchableOpacity;)}  />
key={template.templateId});
style={[styles.templateCard, { borderLeftColor: theme.color ;}}]});
onPress={() => createFromTemplate(template)}
      >;
        <View style={styles.templateHeader}>;
          <View style={styles.templateInfo}>;
            <Icon name={theme.icon} size={20} color={theme.color}  />
            <View style={styles.templateText}>;
              <Text style={styles.templateName}>{template.name}</Text>
              <Text style={styles.templateTheme}>{theme.name}</Text>
            </View>
          </View>
          <View style={[styles.difficultyBadge, { backgroundColor: difficulty.color ;}}]}>;
            <Text style={styles.difficultyText}>{difficulty.name}</Text>
          </View>
        </View>
        <Text style={styles.templateDescription}>{template.description}</Text>"
        <View style={styles.templateStats}>
          <View style={styles.statItem}>
            <Icon name="grid" size={14} color={colors.textSecondary}  />"/;"/g"/;
            <Text style={styles.statText}>{template.sizeX}×{template.sizeY}</Text>"
          </View>"/;"/g"/;
          <View style={styles.statItem}>
            <Icon name="book-open" size={14} color={colors.textSecondary}  />;"/;"/g"/;
            <Text style={styles.statText}>{template.knowledgeNodeCount}个知识点</Text>;
          </View>;"/;"/g"/;
          <View style={styles.statItem}>;
            <Icon name="trophy" size={14} color={colors.textSecondary}  />;"/;"/g"/;
            <Text style={styles.statText}>{template.challengeCount}个挑战</Text>;
          </View>;
        </View>;
        {template.isPopular && (;)}
          <View style={styles.popularBadge}>;
            <Icon name="fire" size={12} color="#FF5722"  />;"/;"/g"/;
            <Text style={styles.popularText}>热门</Text>;
          </View>;
        )};
      </TouchableOpacity>;
    );
  };
  // 渲染进度卡片
const renderProgressCard = (progress: MazeProgress) => {const maze = mazes.find(m => m.id === progress.mazeId)if (!maze) return null;
const theme = themeConfig[maze.theme];
const completionRate = (progress.visitedNodes.length / (maze.size * maze.size)) * 100;
}
    return (<TouchableOpacity;)}  />
key={progress.mazeId});
style={[styles.progressCard, { borderLeftColor: theme.color ;}}]});
onPress={() => continueMaze(progress.mazeId)}
      >;
        <View style={styles.progressHeader}>;
          <View style={styles.progressInfo}>;
            <Icon name={theme.icon} size={20} color={theme.color}  />
            <View style={styles.progressText}>;
              <Text style={styles.progressMazeName}>{maze.name}</Text>
              <Text style={styles.progressStatus}>;
              </Text>
            </View>
          </View>
          <Text style={styles.progressScore}>{progress.score}分</Text>
        </View>
        <View style={styles.progressBar}>;
          <View;  />
style={[]styles.progressFill,}
              {}
                width: `${completionRate;}}%`,````,```;
const backgroundColor = theme.color;
              }
];
            ]} ;
          />;
        </View>;
        <View style={styles.progressStats}>;
          <Text style={styles.progressStatText}>;
          </Text>;
          <Text style={styles.progressStatText}>;
          </Text>;
          <Text style={styles.progressStatText}>;
          </Text>;
        </View>;
      </TouchableOpacity>;
    );
  };
return (<SafeAreaView style={styles.container}>;)      <View style={styles.header}>;
        <Text style={styles.title}>玉米迷宫</Text>)"
        <TouchableOpacity;)"  />"
style={styles.createButton})","
onPress={() => navigation.navigate('CreateMaze')}
        >'
          <Icon name="plus" size={20} color={colors.white}  />"/;"/g"/;
        </TouchableOpacity>
      </View>"
      <View style={styles.tabContainer}>
        <TouchableOpacity;"  />"
style={[styles.tab, selectedTab === 'my' && styles.activeTab]}
onPress={() => setSelectedTab('my')}
        >'
          <Text style={[styles.tabText, selectedTab === 'my' && styles.activeTabText]}>
          </Text>'
        </TouchableOpacity>'/;'/g'/;
        <TouchableOpacity;'  />/,'/g'/;
style={[styles.tab, selectedTab === 'templates' && styles.activeTab]}
onPress={() => setSelectedTab('templates')}
        >'
          <Text style={[styles.tabText, selectedTab === 'templates' && styles.activeTabText]}>
          </Text>'
        </TouchableOpacity>'/;'/g'/;
        <TouchableOpacity;'  />/,'/g'/;
style={[styles.tab, selectedTab === 'progress' && styles.activeTab]}
onPress={() => setSelectedTab('progress')}
        >'
          <Text style={[styles.tabText, selectedTab === 'progress' && styles.activeTabText]}>;
          </Text>;
        </TouchableOpacity>;
      </View>;
      <ScrollView;  />
style={styles.content};
refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh}  />;
        };
      >;
        {selectedTab === 'my' && (;)'}
          <View style={styles.section}>;
            {mazes.length > 0 ? (;)}
              mazes.map(renderMazeCard)}
            ) : (<View style={styles.emptyState}>';)                <Icon name="maze" size={64} color={colors.textSecondary}  />"/;"/g"/;
                <Text style={styles.emptyText}>还没有迷宫</Text>)
                <Text style={styles.emptySubtext}>从模板创建你的第一个迷宫吧</Text>)
              </View>)
            )}
          </View>"/;"/g"/;
        )}
        {selectedTab === 'templates'  && <View style={styles.section}>
            {templates.map(renderTemplateCard)}
          </View>'/;'/g'/;
        )}
        {selectedTab === 'progress'  && <View style={styles.section}>
            {userProgress.length > 0 ? ()}
              userProgress.map(renderProgressCard)}
            ) : (<View style={styles.emptyState}>';)                <Icon name="chart-line" size={64} color={colors.textSecondary}  />"/;"/g"/;
                <Text style={styles.emptyText}>暂无游戏记录</Text>)
                <Text style={styles.emptySubtext}>开始你的第一个迷宫冒险吧</Text>)
              </View>)
            )}
          </View>
        )}
      </ScrollView>
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
title: {,'fontSize: 24,'
fontWeight: 'bold,'
}
    const color = colors.text}
  }
createButton: {backgroundColor: colors.primary,
borderRadius: 20,
width: 40,
height: 40,'
justifyContent: 'center,'
}
    const alignItems = 'center'}
  ;},'
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
section: {,}
  const paddingVertical = 16}
  }
mazeCard: {backgroundColor: colors.surface,
borderRadius: 12,
padding: 16,
marginBottom: 12,
borderLeftWidth: 4,
elevation: 2,
}
    shadowColor: '#000,'}'';
shadowOffset: { width: 0, height: 2 }
shadowOpacity: 0.1,
const shadowRadius = 4;
  },'
mazeHeader: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'
}
    const marginBottom = 8}
  },'
mazeInfo: {,'flexDirection: 'row,'
alignItems: 'center,'
}
    const flex = 1}
  }
mazeText: {marginLeft: 12,
}
    const flex = 1}
  }
mazeName: {,'fontSize: 16,'
fontWeight: '600,'
}
    const color = colors.text}
  }
mazeTheme: {fontSize: 14,
color: colors.textSecondary,
}
    const marginTop = 2}
  }
difficultyBadge: {paddingHorizontal: 8,
paddingVertical: 4,
}
    const borderRadius = 12}
  }
difficultyText: {,'fontSize: 12,'
fontWeight: '600,'
}
    const color = colors.white}
  }
mazeDescription: {fontSize: 14,
color: colors.textSecondary,
marginBottom: 12,
}
    const lineHeight = 20}
  },'
mazeStats: {,'flexDirection: 'row,'
}
    const justifyContent = 'space-between'}
  ;},'
statItem: {,'flexDirection: 'row,'
}
    const alignItems = 'center'}
  }
statText: {fontSize: 12,
color: colors.textSecondary,
}
    const marginLeft = 4}
  }
templateCard: {backgroundColor: colors.surface,
borderRadius: 12,
padding: 12,
marginBottom: 8,
borderLeftWidth: 4,
elevation: 1,
}
    shadowColor: '#000,'}'';
shadowOffset: { width: 0, height: 1 }
shadowOpacity: 0.05,
const shadowRadius = 2;
  },'
templateHeader: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'
}
    const marginBottom = 6}
  },'
templateInfo: {,'flexDirection: 'row,'
alignItems: 'center,'
}
    const flex = 1}
  }
templateText: {marginLeft: 8,
}
    const flex = 1}
  }
templateName: {,'fontSize: 14,'
fontWeight: '600,'
}
    const color = colors.text}
  }
templateTheme: {fontSize: 12,
color: colors.textSecondary,
}
    const marginTop = 1}
  }
templateDescription: {fontSize: 12,
color: colors.textSecondary,
marginBottom: 8,
}
    const lineHeight = 16}
  },'
templateStats: {,'flexDirection: 'row,'
}
    const justifyContent = 'space-between'}
  ;},'
popularBadge: {,'position: 'absolute,'';
top: 8,
right: 8,'
flexDirection: 'row,'
alignItems: 'center,'
backgroundColor: '#FFF3E0,'';
paddingHorizontal: 6,
paddingVertical: 2,
}
    const borderRadius = 8}
  }
popularText: {,'fontSize: 10,'
fontWeight: '600,'
color: '#FF5722,'
}
    const marginLeft = 2}
  }
progressCard: {backgroundColor: colors.surface,
borderRadius: 12,
padding: 16,
marginBottom: 12,
borderLeftWidth: 4,
elevation: 2,
}
    shadowColor: '#000,'}'';
shadowOffset: { width: 0, height: 2 }
shadowOpacity: 0.1,
const shadowRadius = 4;
  },'
progressHeader: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'
}
    const marginBottom = 12}
  },'
progressInfo: {,'flexDirection: 'row,'
alignItems: 'center,'
}
    const flex = 1}
  }
progressText: {marginLeft: 12,
}
    const flex = 1}
  }
progressMazeName: {,'fontSize: 16,'
fontWeight: '600,'
}
    const color = colors.text}
  }
progressStatus: {fontSize: 14,
color: colors.textSecondary,
}
    const marginTop = 2}
  }
progressScore: {,'fontSize: 18,'
fontWeight: 'bold,'
}
    const color = colors.primary}
  }
progressBar: {height: 6,
backgroundColor: colors.border,
borderRadius: 3,
}
    const marginBottom = 12}
  },'
progressFill: {,'height: '100%,'
}
    const borderRadius = 3}
  },'
progressStats: {,'flexDirection: 'row,'
}
    const justifyContent = 'space-between'}
  }
progressStatText: {fontSize: 12,
}
    const color = colors.textSecondary}
  },'
emptyState: {,'alignItems: "center,
}
      const paddingVertical = 60;"};
  },emptyText: {fontSize: 18,fontWeight: '600',color: colors.textSecondary,marginTop: 16;')}
  },emptySubtext: {fontSize: 14,color: colors.textSecondary,marginTop: 8,textAlign: 'center)}
  };);
});
export default MazeMainScreen;