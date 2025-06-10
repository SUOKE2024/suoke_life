import React, { useState, useEffect, useCallback, useRef } from "react";";
import {import { useFocusEffect } from "@react-navigation/native";""/;,"/g"/;
import { cornMazeService } from "../../services/cornMazeService";""/;,"/g"/;
import {import MazeRenderer from "./MazeRenderer";""/;,}import GameControls from "./GameControls";""/;,"/g"/;
import ProgressDisplay from "./ProgressDisplay";""/;,"/g"/;
import KnowledgeNodeModal from "./KnowledgeNodeModal";""/;,"/g"/;
import ChallengeModal from "./ChallengeModal";""/;,"/g"/;
import GameSettingsModal from "./GameSettingsModal";""/;"/g"/;
/* ; *//;/g/;
*//;,/g/;
View,;
Text,;
StyleSheet,;
Alert,;
BackHandler,;
Dimensions,;
StatusBar,;
SafeAreaView,";"";
}
  ActivityIndicator;'}'';'';
} from "react-native";";
Maze,;
MazeProgress,;
Direction,;
GameEventType,;
MoveResponse,;
KnowledgeNode,;
Challenge,;
GameSettings,';,'';
MazeDifficulty;';'';
} from "../../types/maze";""/;"/g"/;
// GameCompletionModal 已替换为 MazeCompletionScreen;/;,/g/;
interface MazeGameScreenProps {route: {params: {mazeId: string,;
const userId = string;
}
}
      resumeGame?: boolean;}
};
  };
const navigation = any;';'';
}';,'';
const { width: screenWidth, height: screenHeight ;} = Dimensions.get('window');';,'';
const MazeGameScreen: React.FC<Suspense fallback={<LoadingSpinner  />}><MazeGameScreenProps></Suspense> = ({ route, navigation ;}) => {}/;,/g/;
const { mazeId, userId, resumeGame: shouldResumeGame = false ;} = route.params;
  // 状态管理/;,/g/;
const [maze, setMaze] = useState<Maze | null>(null);
const [progress, setProgress] = useState<MazeProgress | null>(null);
const [gameSettings, setGameSettings] = useState<GameSettings | null>(null);
const [loading, setLoading] = useState(true);
const [gameStarted, setGameStarted] = useState(false);
const [isPaused, setIsPaused] = useState(false);
const [error, setError] = useState<string | null>(null);
  // 模态框状态/;,/g/;
const [showKnowledgeModal, setShowKnowledgeModal] = useState(false);
const [showChallengeModal, setShowChallengeModal] = useState(false);
const [showSettingsModal, setShowSettingsModal] = useState(false);
const [showCompletionModal, setShowCompletionModal] = useState(false);
const [currentKnowledge, setCurrentKnowledge] = useState<KnowledgeNode | null>(null);
const [currentChallenge, setCurrentChallenge] = useState<Challenge | null>(null);
  // 游戏状态/;,/g/;
const [gameTime, setGameTime] = useState(0);
const [isMoving, setIsMoving] = useState(false);
const gameTimerRef = useRef<NodeJS.Timeout | null>(null);
  /* 戏 *//;/g/;
  *//;,/g/;
const initializeGame = useCallback(async () => {try {setLoading(true););,}setError(null);
      // 并行加载数据/;,/g/;
const [mazeResponse, settingsResponse] = await Promise.all([;););,]cornMazeService.getMaze(mazeId, userId),cornMazeService.getGameSettings(userId);
];
      ]);
setMaze(mazeResponse.maze);
setGameSettings(settingsResponse);
if (shouldResumeGame && mazeResponse.userProgress) {// 恢复游戏进度/;,}setProgress(mazeResponse.userProgress);,/g/;
setGameStarted(true);
}
        setGameTime(Math.floor(Date.now() - new Date(mazeResponse.userProgress.startTime).getTime()) / 1000));}/;/g/;
      } else {}}
        // 开始新游戏}/;,/g,/;
  newProgress: await cornMazeService.startMaze({ userId, mazeId });
setProgress(newProgress);
setGameStarted(true);
setGameTime(0);
      }';'';
    } catch (err) {';,}console.error('Failed to initialize game:', err);';'';
}
}
    } finally {}}
      setLoading(false);}
    }
  }, [mazeId, userId, shouldResumeGame]);
  /* 器 *//;/g/;
  *//;,/g/;
const startGameTimer = useCallback() => {if (gameTimerRef.current) {clearInterval(gameTimerRef.current);}
    }
    gameTimerRef.current = setInterval() => {}}
      setGameTime(prev => prev + 1);}
    }, 1000);
  }, []);
  /* 器 *//;/g/;
  *//;,/g/;
const stopGameTimer = useCallback() => {if (gameTimerRef.current) {clearInterval(gameTimerRef.current);}}
      gameTimerRef.current = null;}
    }
  }, []);
  /* 动 *//;/g/;
  *//;,/g/;
const handleMove = useCallback(async (direction: Direction) => {if (!maze || !progress || isMoving || isPaused) return;);,}try {setIsMoving(true);,}const  moveResponse: MoveResponse = await cornMazeService.moveInMaze({)        userId,);,}mazeId,);
}
        direction;)}
      });
if (moveResponse.success) {// 更新进度/;,}updatedProgress: await cornMazeService.getUserProgress(mazeId, userId);,/g/;
setProgress(updatedProgress.progress);
        // 处理游戏事件/;,/g/;
const await = handleGameEvent(moveResponse);
        // 检查游戏完成/;,/g/;
if (moveResponse.gameCompleted) {stopGameTimer();}}
          setShowCompletionModal(true);}
        }
      } else {// 移动失败，可能撞墙了/;,}if (gameSettings?.vibrationEnabled) {}}/g/;
          // 触发震动反馈}/;/g/;
        }
        if (moveResponse.message) {}}
}
        }
      }';'';
    } catch (err) {';,}console.error('Move failed:', err);';'';
}
}
    } finally {}}
      setIsMoving(false);}
    }
  }, [maze, progress, isMoving, isPaused, userId, mazeId, gameSettings]);
  /* 件 *//;/g/;
  *//;,/g/;
const handleGameEvent = useCallback(async (moveResponse: MoveResponse) => {switch (moveResponse.eventType) {case GameEventType.KNOWLEDGE:if (moveResponse.knowledgeNode) {setCurrentKnowledge(moveResponse.knowledgeNode););,}setShowKnowledgeModal(true);
setIsPaused(true);
}
          stopGameTimer();}
        }
        break;
const case = GameEventType.CHALLENGE: ;
if (moveResponse.challenge) {setCurrentChallenge(moveResponse.challenge);,}setShowChallengeModal(true);
setIsPaused(true);
}
          stopGameTimer();}
        }
        break;
const case = GameEventType.REWARD: ;
if (moveResponse.reward) {}}
}
            `${moveResponse.reward.name;}\n${moveResponse.reward.description}`,````;```;
            [;]{';}}'';
'}'';'';
];
const style = 'default' ;}]';'';
          );
        }
        break;
const case = GameEventType.GOAL: ;
        // 到达终点，游戏完成/;,/g/;
stopGameTimer();
setShowCompletionModal(true);
break;
const default = break;
    }
  }, []);
  /* 戏 *//;/g/;
  *//;,/g/;
const pauseGame = useCallback() => {setIsPaused(true);}}
    stopGameTimer();}
  }, [stopGameTimer]);
  /* 戏 *//;/g/;
  *//;,/g/;
const resumeGame = useCallback() => {setIsPaused(false);}}
    startGameTimer();}
  }, [startGameTimer]);
  /* 戏 *//;/g/;
  *//;,/g/;
const exitGame = useCallback() => {Alert.alert(;);}        {';}}'';
'}'';
style: 'cancel' ;},{';}';,'';
style: 'destructive',onPress: () => {stopGameTimer();';}}'';
            navigation.goBack();}
          }
        }
      ];
    );
  }, [navigation, stopGameTimer]);
  /* 闭 *//;/g/;
  *//;,/g/;
const handleKnowledgeModalClose = useCallback() => {setShowKnowledgeModal(false);,}setCurrentKnowledge(null);
setIsPaused(false);
}
    startGameTimer();}
  }, [startGameTimer]);
  /* 闭 *//;/g/;
  *//;,/g/;
const handleChallengeModalClose = useCallback(completed: boolean) => {setShowChallengeModal(false);,}setCurrentChallenge(null);
setIsPaused(false);
startGameTimer();
if (completed) {// 刷新进度/;,}cornMazeService.getUserProgress(mazeId, userId);/g/;
        .then(response => setProgress(response.progress));
}
        .catch(console.error);}
    }
  }, [mazeId, userId, startGameTimer]);
  /* 新 *//;/g/;
  *//;,/g/;
const handleSettingsUpdate = useCallback(newSettings: GameSettings) => {setGameSettings(newSettings);}
  }, []);
  /* 成 *//;/g/;
  *//;,/g/;
const handleGameCompletion = useCallback() => {setShowCompletionModal(false);}}
    navigation.goBack();}
  }, [navigation]);
  // 处理返回键/;,/g/;
useFocusEffect();
useCallback() => {const onBackPress = () => {exitGame();}}
        return true;}';'';
      };';,'';
const: subscription = BackHandler.addEventListener('hardwareBackPress', onBackPress)';'';
    // 记住在组件卸载时移除监听器;'/;,'/g'/;
return () => subscription.remove();
    }, [exitGame]);
  );
  // 组件挂载时初始化游戏/;,/g/;
useEffect() => {initializeGame();}}
    return () => {stopGameTimer();}
    };
  }, [initializeGame, stopGameTimer]);
  // 游戏开始时启动计时器/;,/g/;
useEffect() => {if (gameStarted && !isPaused) {}}
      startGameTimer();}
    }
    return () => {stopGameTimer();}
    };
  }, [gameStarted, isPaused, startGameTimer, stopGameTimer]);
  // 加载状态/;,/g/;
if (loading) {}}
    return (;)}';'';
      <SafeAreaView style={styles.container}>;';'';
        <StatusBar barStyle="light-content" backgroundColor="#2E7D32"  />;"/;"/g"/;
        <View style={styles.loadingContainer}>;";"";
          <ActivityIndicator size="large" color="#4CAF50"  />;"/;"/g"/;
          <Text style={styles.loadingText}>正在加载迷宫...</Text>;/;/g/;
        </View>;/;/g/;
      </SafeAreaView>;/;/g/;
    );
  }
  // 错误状态/;,/g/;
if (error) {}}
    return (;)}";"";
      <SafeAreaView style={styles.container}>;";"";
        <StatusBar barStyle="light-content" backgroundColor="#2E7D32"  />;"/;"/g"/;
        <View style={styles.errorContainer}>;
          <Text style={styles.errorText}>{error}</Text>;/;/g/;
          <Text style={styles.retryText} onPress={initializeGame}>;

          </Text>;/;/g/;
        </View>;/;/g/;
      </SafeAreaView>;/;/g/;
    );
  }
  // 主游戏界面"/;,"/g"/;
return (<SafeAreaView style={styles.container}>";)      <StatusBar barStyle="light-content" backgroundColor="#2E7D32"  />"/;"/g"/;
      {// 进度显示}/;/g/;
      {progress  && <ProgressDisplay;}  />/;,/g/;
progress={progress}
          gameTime={gameTime}
          isPaused={isPaused});
onPause={pauseGame});
onResume={resumeGame});
onSettings={() => setShowSettingsModal(true)}
          onExit={exitGame}
        />/;/g/;
      )}
      {// 迷宫渲染器}/;/g/;
      {maze && progress  && <MazeRenderer;}  />/;,/g/;
maze={maze}
          progress={progress}
          isMoving={isMoving}
          isPaused={isPaused}
          gameSettings={gameSettings}
        />/;/g/;
      )}
      {// 游戏控制}/;/g/;
      <GameControls;  />/;,/g/;
onMove={handleMove}
        disabled={isMoving || isPaused}
        gameSettings={gameSettings}
      />/;/g/;
      {// 知识节点模态框}/;/g/;
      {showKnowledgeModal && currentKnowledge  && <KnowledgeNodeModal;}  />/;,/g/;
knowledgeNode={currentKnowledge}
          visible={showKnowledgeModal}
          onClose={handleKnowledgeModalClose}
        />/;/g/;
      )}
      {// 挑战模态框}/;/g/;
      {showChallengeModal && currentChallenge  && <ChallengeModal;}  />/;,/g/;
challenge={currentChallenge}
          visible={showChallengeModal}
          onClose={handleChallengeModalClose}
          userId={userId}
        />/;/g/;
      )}
      {// 设置模态框}/;/g/;
      {showSettingsModal && gameSettings  && <GameSettingsModal;}  />/;,/g/;
settings={gameSettings}
          visible={showSettingsModal}
          onClose={() => setShowSettingsModal(false)}
          onUpdate={handleSettingsUpdate}
          userId={userId}
        />;/;/g/;
      )};
      {// 游戏完成处理};/;/g/;
      {showCompletionModal && progress && maze && (;)";}        () => {// 导航到完成屏幕;"/;,}navigation.navigate('MazeCompletion', {score: progress.score,completionTime: gameTime,stepsCount: progress.stepsCount,theme: maze.theme,difficulty: maze.difficulty,rewards: [],mazeName: maze.name,onPlayAgain: () => {setShowCompletionModal(false);)';}}'/g'/;
              initializeGame();}
            }
onBackToMenu: () => {setShowCompletionModal(false);}}
              navigation.goBack();}
            }
          });
setShowCompletionModal(false);
return null;
        })();
      )}
    </SafeAreaView>/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,';,}flex: 1,';'';
}
    const backgroundColor = '#1B5E20'}'';'';
  ;}
loadingContainer: {,';,}flex: 1,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    const backgroundColor = '#1B5E20'}'';'';
  ;},';,'';
loadingText: {,';,}color: '#FFFFFF';','';
fontSize: 16,';,'';
marginTop: 16,';'';
}
    const fontWeight = '500'}'';'';
  ;}
errorContainer: {,';,}flex: 1,';,'';
justifyContent: 'center';','';'';
}
    alignItems: 'center',backgroundColor: '#1B5E20',padding: 20;'}'';'';
  },errorText: {,';,}color: "#FFCDD2";","";"";
}
      fontSize: 16,textAlign: 'center',marginBottom: 16;'}'';'';
  },retryText: {,';,}color: "#4CAF50";",")";"";
}
      fontSize: 16,fontWeight: 'bold',textDecorationLine: 'underline';')}'';'';
  };);
});';,'';
export default MazeGameScreen;