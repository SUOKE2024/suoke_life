import React from 'react';
import { useState, useEffect, useCallback, useRef } from 'react';
import { Alert, Vibration } from 'react-native';
import { cornMazeService } from '../services/cornMazeService';
import {Maze,
  MazeProgress,
  Position,
  Direction,
  GameEventType,
  MoveResponse,
  GameSettings,
  KnowledgeNode,
  Challenge,
  GameReward;
} from '../types/maze';
interface UseMazeGameProps {
  mazeId: string;
  userId: string;
  onGameComplete?: (score: number, rewards: GameReward[]) => void;
  onError?: (error: string) => void;
}
interface MazeGameState {
  maze: Maze | null;
  progress: MazeProgress | null;
  settings: GameSettings | null;
  loading: boolean;
  error: string | null;
  isPaused: boolean;
  currentEvent: {;
  type: GameEventType;
    data?: any;
} | null;
}
export const useMazeGame = ({mazeId,userId,onGameComplete,onError;
}: UseMazeGameProps) => {const [state, setState] = useState<MazeGameState>({maze: null,progress: null,settings: null,loading: true,error: null,isPaused: false,currentEvent: null;
  });
  const gameTimerRef = useRef<NodeJS.Timeout | null>(null);
  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null);
  // 初始化游戏
  const initializeGame = useCallback(async () => {try {setState(prev => ({ ...prev, loading: true, error: null }));
      const [mazeResponse, settingsResponse] = await Promise.all([;
        cornMazeService.getMaze(mazeId, userId),cornMazeService.getGameSettings(userId);
      ]);
      setState(prev => ({
        ...prev,
        maze: mazeResponse.maze,
        progress: mazeResponse.userProgress || null,
        settings: settingsResponse,
        loading: false;
      }));
      // 如果没有进度，开始新游戏
      if (!mazeResponse.userProgress) {
        await startNewGame();
      }
      // 启动自动保存
      if (settingsResponse.autoSave) {
        startAutoSave();
      }
    } catch (error) {
      const errorMessage = '初始化游戏失败';
      setState(prev => ({ ...prev, error: errorMessage, loading: false }));
      onError?.(errorMessage);
    }
  }, [mazeId, userId, onError]);
  // 开始新游戏
  const startNewGame = useCallback(async () => {try {const newProgress = await cornMazeService.startMaze({ userId, mazeId });
      setState(prev => ({ ...prev, progress: newProgress }));
    } catch (error) {
      const errorMessage = '开始游戏失败';
      setState(prev => ({ ...prev, error: errorMessage }));
      onError?.(errorMessage);
    }
  }, [userId, mazeId, onError]);
  // 移动玩家
  const movePlayer = useCallback(async (direction: Direction) => {if (!state.progress || state.isPaused || state.loading) {return;
    }
    try {
      const moveResponse: MoveResponse = await cornMazeService.moveInMaze({
        userId,
        mazeId,
        direction;
      });
      // 更新进度
      const updatedProgress = await cornMazeService.getUserProgress(mazeId, userId);
      setState(prev => ({
        ...prev,
        progress: updatedProgress.progress,
        currentEvent: {,
  type: moveResponse.eventType,
          data: {,
  knowledgeNode: moveResponse.knowledgeNode,
            challenge: moveResponse.challenge,
            reward: moveResponse.reward,
            message: moveResponse.message;
          }
        }
      }));
      // 触觉反馈
      if (state.settings?.vibrationEnabled) {
        if (moveResponse.eventType === GameEventType.WALL_HIT) {
          Vibration.vibrate(100);
        } else if (moveResponse.eventType === GameEventType.REWARD) {
          Vibration.vibrate([100, 50, 100]);
        }
      }
      // 游戏完成检查
      if (moveResponse.gameCompleted) {
        handleGameComplete(moveResponse.score || 0, moveResponse.reward ? [moveResponse.reward] : []);
      }
      return moveResponse;
    } catch (error) {
      const errorMessage = '移动失败';
      setState(prev => ({ ...prev, error: errorMessage }));
      onError?.(errorMessage);
    }
  }, [state.progress, state.isPaused, state.loading, state.settings, userId, mazeId, onError]);
  // 处理游戏完成
  const handleGameComplete = useCallback(async (score: number, rewards: GameReward[]) => {try {if (state.progress) {await cornMazeService.recordMazeCompletion(;
          userId,mazeId,state.progress.stepsCount,Date.now() - state.progress.startTime.getTime(),score;
        );
      }
      onGameComplete?.(score, rewards);
    } catch (error) {
      console.error('记录游戏完成失败:', error);
    }
  }, [state.progress, userId, mazeId, onGameComplete]);
  // 暂停/继续游戏
  const togglePause = useCallback() => {setState(prev => ({ ...prev, isPaused: !prev.isPaused }));
  }, []);
  // 重置游戏
  const resetGame = useCallback(async () => {Alert.alert(;
      "重置游戏",确定要重置当前游戏吗？所有进度将丢失。',[;
        {
      text: "取消",
      style: 'cancel' },{
      text: "确定",
      style: 'destructive',onPress: async () => {await startNewGame();
            setState(prev => ({ ...prev, currentEvent: null }));
          }
        }
      ]
    );
  }, [startNewGame]);
  // 获取提示
  const getHint = useCallback(async () => {if (!state.progress || !state.maze) {return;
    }
    try {
      // 这里可以实现提示逻辑
      const hints = [;
        "尝试探索不同的方向",注意寻找知识节点',"完成挑战可以获得更多分数",收集所有奖励物品';
      ];
      const randomHint = hints[Math.floor(Math.random() * hints.length)];
      Alert.alert('提示', randomHint);
      // 更新提示使用次数
      setState(prev => ({
        ...prev,
        progress: prev.progress ? {
          ...prev.progress,
          hints: (prev.progress.hints || 0) + 1;
        } : null;
      }));
    } catch (error) {
      console.error('获取提示失败:', error);
    }
  }, [state.progress, state.maze]);
  // 清除当前事件
  const clearCurrentEvent = useCallback() => {setState(prev => ({ ...prev, currentEvent: null }));
  }, []);
  // 更新游戏设置
  const updateSettings = useCallback(async (newSettings: Partial<GameSettings>) => {try {const updatedSettings = await cornMazeService.updateGameSettings(userId, newSettings);
      setState(prev => ({ ...prev, settings: updatedSettings }));
      // 重新启动自动保存
      if (updatedSettings.autoSave) {
        startAutoSave();
      } else {
        stopAutoSave();
      }
    } catch (error) {
      console.error('更新设置失败:', error);
    }
  }, [userId]);
  // 启动自动保存
  const startAutoSave = useCallback() => {stopAutoSave(); // 清除现有定时器
    autoSaveTimerRef.current = setInterval(async () => {
      if (state.progress && !state.isPaused) {
        try {
          // 这里可以实现自动保存逻辑
          console.log('自动保存游戏进度');
        } catch (error) {
          console.error('自动保存失败:', error);
        }
      }
    }, 30000); // 每30秒自动保存
  }, [state.progress, state.isPaused]);
  // 停止自动保存
  const stopAutoSave = useCallback() => {if (autoSaveTimerRef.current) {clearInterval(autoSaveTimerRef.current);
      autoSaveTimerRef.current = null;
    }
  }, []);
  // 获取当前位置的可移动方向
  const getAvailableDirections = useCallback(): Direction[] => {if (!state.maze || !state.progress) {return [];
    }
    const { currentPosition } = state.progress;
    const { nodes, size } = state.maze;
    const availableDirections: Direction[] = [];
    // 检查北方
    if (currentPosition.y > 0 && nodes[currentPosition.y - 1][currentPosition.x].accessible) {
      availableDirections.push(Direction.NORTH);
    }
    // 检查南方
    if (currentPosition.y < size - 1 && nodes[currentPosition.y + 1][currentPosition.x].accessible) {
      availableDirections.push(Direction.SOUTH);
    }
    // 检查西方
    if (currentPosition.x > 0 && nodes[currentPosition.y][currentPosition.x - 1].accessible) {
      availableDirections.push(Direction.WEST);
    }
    // 检查东方
    if (currentPosition.x < size - 1 && nodes[currentPosition.y][currentPosition.x + 1].accessible) {
      availableDirections.push(Direction.EAST);
    }
    return availableDirections;
  }, [state.maze, state.progress]);
  // 计算完成百分比
  const getCompletionPercentage = useCallback(): number => {if (!state.maze || !state.progress) {return 0;
    }
    const totalNodes = state.maze.size * state.maze.size;
    const visitedNodes = state.progress.visitedNodes.length;
    return Math.round(visitedNodes / totalNodes) * 100);
  }, [state.maze, state.progress]);
  // 初始化
  useEffect() => {
    initializeGame();
    return () => {stopAutoSave();
      if (gameTimerRef.current) {
        clearInterval(gameTimerRef.current);
      }
    };
  }, [initializeGame, stopAutoSave]);
  return {
    // 状态
    maze: state.maze,
    progress: state.progress,
    settings: state.settings,
    loading: state.loading,
    error: state.error,
    isPaused: state.isPaused,
    currentEvent: state.currentEvent,// 操作;
    movePlayer,togglePause,resetGame,getHint,clearCurrentEvent,updateSettings;
    // 计算属性;
    availableDirections: getAvailableDirections(),completionPercentage: getCompletionPercentage(),// 工具函数;
    initializeGame,startNewGame;
  };
};
export default React.memo(useMazeGame);