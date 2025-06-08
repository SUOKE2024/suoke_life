import React, { useState, useEffect, useCallback, useRef } from 'react';
import {import { useFocusEffect } from '@react-navigation/native';
import { cornMazeService } from '../../services/cornMazeService';
import {import MazeRenderer from './MazeRenderer';
import GameControls from './GameControls';
import ProgressDisplay from './ProgressDisplay';
import KnowledgeNodeModal from './KnowledgeNodeModal';
import ChallengeModal from './ChallengeModal';
import GameSettingsModal from './GameSettingsModal';
/**
* 迷宫游戏主屏幕
* Maze Game Main Screen;
*/
  View,
  Text,
  StyleSheet,
  Alert,
  BackHandler,
  Dimensions,
  StatusBar,
  SafeAreaView,
  ActivityIndicator;
} from 'react-native';
  Maze,
  MazeProgress,
  Direction,
  GameEventType,
  MoveResponse,
  KnowledgeNode,
  Challenge,
  GameSettings,
  MazeDifficulty;
} from '../../types/maze';
// GameCompletionModal 已替换为 MazeCompletionScreen;
interface MazeGameScreenProps {
  route: {;
  params: {;
      mazeId: string;
  userId: string;
      resumeGame?: boolean;
};
  };
  navigation: any;
}
const { width: screenWidth, height: screenHeight } = Dimensions.get('window');
const MazeGameScreen: React.FC<MazeGameScreenProps> = ({ route, navigation }) => {
  const { mazeId, userId, resumeGame: shouldResumeGame = false } = route.params;
  // 状态管理
  const [maze, setMaze] = useState<Maze | null>(null);
  const [progress, setProgress] = useState<MazeProgress | null>(null);
  const [gameSettings, setGameSettings] = useState<GameSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [gameStarted, setGameStarted] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // 模态框状态
  const [showKnowledgeModal, setShowKnowledgeModal] = useState(false);
  const [showChallengeModal, setShowChallengeModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [showCompletionModal, setShowCompletionModal] = useState(false);
  const [currentKnowledge, setCurrentKnowledge] = useState<KnowledgeNode | null>(null);
  const [currentChallenge, setCurrentChallenge] = useState<Challenge | null>(null);
  // 游戏状态
  const [gameTime, setGameTime] = useState(0);
  const [isMoving, setIsMoving] = useState(false);
  const gameTimerRef = useRef<NodeJS.Timeout | null>(null);
  /**
  * 初始化游戏
  */
  const initializeGame = useCallback(async () => {try {setLoading(true);
      setError(null);
      // 并行加载数据
      const [mazeResponse, settingsResponse] = await Promise.all([;
        cornMazeService.getMaze(mazeId, userId),cornMazeService.getGameSettings(userId);
      ]);
      setMaze(mazeResponse.maze);
      setGameSettings(settingsResponse);
      if (shouldResumeGame && mazeResponse.userProgress) {
        // 恢复游戏进度
        setProgress(mazeResponse.userProgress);
        setGameStarted(true);
        setGameTime(Math.floor(Date.now() - new Date(mazeResponse.userProgress.startTime).getTime()) / 1000));
      } else {
        // 开始新游戏
        const newProgress = await cornMazeService.startMaze({ userId, mazeId });
        setProgress(newProgress);
        setGameStarted(true);
        setGameTime(0);
      }
    } catch (err) {
      console.error('Failed to initialize game:', err);
      setError('游戏初始化失败，请重试');
    } finally {
      setLoading(false);
    }
  }, [mazeId, userId, shouldResumeGame]);
  /**
  * 开始游戏计时器
  */
  const startGameTimer = useCallback() => {if (gameTimerRef.current) {clearInterval(gameTimerRef.current);
    }
    gameTimerRef.current = setInterval() => {
      setGameTime(prev => prev + 1);
    }, 1000);
  }, []);
  /**
  * 停止游戏计时器
  */
  const stopGameTimer = useCallback() => {if (gameTimerRef.current) {clearInterval(gameTimerRef.current);
      gameTimerRef.current = null;
    }
  }, []);
  /**
  * 处理玩家移动
  */
  const handleMove = useCallback(async (direction: Direction) => {if (!maze || !progress || isMoving || isPaused) return;
    try {
      setIsMoving(true);
      const moveResponse: MoveResponse = await cornMazeService.moveInMaze({
        userId,
        mazeId,
        direction;
      });
      if (moveResponse.success) {
        // 更新进度
        const updatedProgress = await cornMazeService.getUserProgress(mazeId, userId);
        setProgress(updatedProgress.progress);
        // 处理游戏事件
        await handleGameEvent(moveResponse);
        // 检查游戏完成
        if (moveResponse.gameCompleted) {
          stopGameTimer();
          setShowCompletionModal(true);
        }
      } else {
        // 移动失败，可能撞墙了
        if (gameSettings?.vibrationEnabled) {
          // 触发震动反馈
        }
        if (moveResponse.message) {
          Alert.alert('提示', moveResponse.message);
        }
      }
    } catch (err) {
      console.error('Move failed:', err);
      Alert.alert("错误",移动失败，请重试');
    } finally {
      setIsMoving(false);
    }
  }, [maze, progress, isMoving, isPaused, userId, mazeId, gameSettings]);
  /**
  * 处理游戏事件
  */
  const handleGameEvent = useCallback(async (moveResponse: MoveResponse) => {switch (moveResponse.eventType) {case GameEventType.KNOWLEDGE:if (moveResponse.knowledgeNode) {setCurrentKnowledge(moveResponse.knowledgeNode);
          setShowKnowledgeModal(true);
          setIsPaused(true);
          stopGameTimer();
        }
        break;
      case GameEventType.CHALLENGE:
        if (moveResponse.challenge) {
          setCurrentChallenge(moveResponse.challenge);
          setShowChallengeModal(true);
          setIsPaused(true);
          stopGameTimer();
        }
        break;
      case GameEventType.REWARD:
        if (moveResponse.reward) {
          Alert.alert(
            '🎉 获得奖励！',
            `${moveResponse.reward.name}\n${moveResponse.reward.description}`,
            [{
      text: "太棒了！",
      style: 'default' }]
          );
        }
        break;
      case GameEventType.GOAL:
        // 到达终点，游戏完成
        stopGameTimer();
        setShowCompletionModal(true);
        break;
      default:
        break;
    }
  }, []);
  /**
  * 暂停游戏
  */
  const pauseGame = useCallback() => {setIsPaused(true);
    stopGameTimer();
  }, [stopGameTimer]);
  /**
  * 恢复游戏
  */
  const resumeGame = useCallback() => {setIsPaused(false);
    startGameTimer();
  }, [startGameTimer]);
  /**
  * 退出游戏
  */
  const exitGame = useCallback() => {Alert.alert(;
      "退出游戏",确定要退出当前游戏吗？游戏进度将会保存。',[;
        {
      text: "取消",
      style: 'cancel' },{
      text: "退出",
      style: 'destructive',onPress: () => {stopGameTimer();
            navigation.goBack();
          }
        }
      ]
    );
  }, [navigation, stopGameTimer]);
  /**
  * 处理知识节点模态框关闭
  */
  const handleKnowledgeModalClose = useCallback() => {setShowKnowledgeModal(false);
    setCurrentKnowledge(null);
    setIsPaused(false);
    startGameTimer();
  }, [startGameTimer]);
  /**
  * 处理挑战模态框关闭
  */
  const handleChallengeModalClose = useCallback(completed: boolean) => {setShowChallengeModal(false);
    setCurrentChallenge(null);
    setIsPaused(false);
    startGameTimer();
    if (completed) {
      // 刷新进度
      cornMazeService.getUserProgress(mazeId, userId);
        .then(response => setProgress(response.progress))
        .catch(console.error);
    }
  }, [mazeId, userId, startGameTimer]);
  /**
  * 处理设置更新
  */
  const handleSettingsUpdate = useCallback(newSettings: GameSettings) => {setGameSettings(newSettings);
  }, []);
  /**
  * 处理游戏完成
  */
  const handleGameCompletion = useCallback() => {setShowCompletionModal(false);
    navigation.goBack();
  }, [navigation]);
  // 处理返回键
  useFocusEffect(
    useCallback() => {
      const onBackPress = () => {exitGame();
        return true;
      };
      const subscription = BackHandler.addEventListener('hardwareBackPress', onBackPress);
      return () => subscription.remove();
    }, [exitGame])
  );
  // 组件挂载时初始化游戏
  useEffect() => {
    initializeGame();
    return () => {stopGameTimer();
    };
  }, [initializeGame, stopGameTimer]);
  // 游戏开始时启动计时器
  useEffect() => {
    if (gameStarted && !isPaused) {
      startGameTimer();
    }
    return () => {stopGameTimer();
    };
  }, [gameStarted, isPaused, startGameTimer, stopGameTimer]);
  // 加载状态
  if (loading) {
    return (;
      <SafeAreaView style={styles.container}>;
        <StatusBar barStyle="light-content" backgroundColor="#2E7D32" />;
        <View style={styles.loadingContainer}>;
          <ActivityIndicator size="large" color="#4CAF50" />;
          <Text style={styles.loadingText}>正在加载迷宫...</Text>;
        </View>;
      </SafeAreaView>;
    );
  }
  // 错误状态
  if (error) {
    return (;
      <SafeAreaView style={styles.container}>;
        <StatusBar barStyle="light-content" backgroundColor="#2E7D32" />;
        <View style={styles.errorContainer}>;
          <Text style={styles.errorText}>{error}</Text>;
          <Text style={styles.retryText} onPress={initializeGame}>;
            点击重试;
          </Text>;
        </View>;
      </SafeAreaView>;
    );
  }
  // 主游戏界面
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#2E7D32" />
      {// 进度显示}
      {progress && (
        <ProgressDisplay;
          progress={progress}
          gameTime={gameTime}
          isPaused={isPaused}
          onPause={pauseGame}
          onResume={resumeGame}
          onSettings={() => setShowSettingsModal(true)}
          onExit={exitGame}
        />
      )}
      {// 迷宫渲染器}
      {maze && progress && (
        <MazeRenderer;
          maze={maze}
          progress={progress}
          isMoving={isMoving}
          isPaused={isPaused}
          gameSettings={gameSettings}
        />
      )}
      {// 游戏控制}
      <GameControls;
        onMove={handleMove}
        disabled={isMoving || isPaused}
        gameSettings={gameSettings}
      />
      {// 知识节点模态框}
      {showKnowledgeModal && currentKnowledge && (
        <KnowledgeNodeModal;
          knowledgeNode={currentKnowledge}
          visible={showKnowledgeModal}
          onClose={handleKnowledgeModalClose}
        />
      )}
      {// 挑战模态框}
      {showChallengeModal && currentChallenge && (
        <ChallengeModal;
          challenge={currentChallenge}
          visible={showChallengeModal}
          onClose={handleChallengeModalClose}
          userId={userId}
        />
      )}
      {// 设置模态框}
      {showSettingsModal && gameSettings && (
        <GameSettingsModal;
          settings={gameSettings}
          visible={showSettingsModal}
          onClose={() => setShowSettingsModal(false)}
          onUpdate={handleSettingsUpdate}
          userId={userId}
        />;
      )};
      {// 游戏完成处理};
      {showCompletionModal && progress && maze && (;
        () => {// 导航到完成屏幕;
          navigation.navigate('MazeCompletion', {score: progress.score,completionTime: gameTime,stepsCount: progress.stepsCount,theme: maze.theme,difficulty: maze.difficulty,rewards: [],mazeName: maze.name,onPlayAgain: () => {setShowCompletionModal(false);
              initializeGame();
            },
            onBackToMenu: () => {
              setShowCompletionModal(false);
              navigation.goBack();
            }
          });
          setShowCompletionModal(false);
          return null;
        })()
      )}
    </SafeAreaView>
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#1B5E20'
  },
  loadingContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1B5E20'
  },
  loadingText: {,
  color: '#FFFFFF',
    fontSize: 16,
    marginTop: 16,
    fontWeight: '500'
  },
  errorContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',backgroundColor: '#1B5E20',padding: 20;
  },errorText: {
      color: "#FFCDD2",
      fontSize: 16,textAlign: 'center',marginBottom: 16;
  },retryText: {
      color: "#4CAF50",
      fontSize: 16,fontWeight: 'bold',textDecorationLine: 'underline';
  };
});
export default MazeGameScreen;