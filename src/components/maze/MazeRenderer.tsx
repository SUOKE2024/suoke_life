import React, { useMemo, useRef, useEffect } from 'react';
import {import Svg, {import {/**
* 迷宫渲染器组件
* Maze Renderer Component;
*/
  View,
  StyleSheet,
  Dimensions,
  Animated,
  PanResponder,
  GestureResponderEvent,
  PanResponderGestureState;
} from 'react-native';
  Rect,
  Circle,
  Path,
  G,
  Text as SvgText,
  Defs,
  LinearGradient,
  Stop,
  Pattern,
  Image as SvgImage;
} from 'react-native-svg';
  Maze,
  MazeProgress,
  GameSettings,
  NodeType,
  Position,
  MazeNode,
  Direction;
} from '../../types/maze';
interface MazeRendererProps {
  maze: Maze;
  progress: MazeProgress;
  isMoving: boolean;
  isPaused: boolean;
  gameSettings: GameSettings | null;
  onMove?: (direction: Direction) => void;
}
const { width: screenWidth, height: screenHeight } = Dimensions.get('window');
// 计算迷宫渲染尺寸
const MAZE_PADDING = 20;
const AVAILABLE_WIDTH = screenWidth - MAZE_PADDING * 2;
const AVAILABLE_HEIGHT = screenHeight * 0.6; // 60%的屏幕高度用于迷宫
const MAX_MAZE_SIZE = Math.min(AVAILABLE_WIDTH, AVAILABLE_HEIGHT);
const MazeRenderer: React.FC<MazeRendererProps> = ({
  maze,
  progress,
  isMoving,
  isPaused,
  gameSettings,
  onMove;
}) => {
  // 动画值
  const playerPosition = useRef(new Animated.ValueXY({x: progress.currentPosition.x,y: progress.currentPosition.y;
  })).current;
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const rotationAnim = useRef(new Animated.Value(0)).current;
  // 计算渲染参数
  const renderParams = useMemo() => {const cellSize = MAX_MAZE_SIZE / maze.size;
    const mazeWidth = maze.size * cellSize;
    const mazeHeight = maze.size * cellSize;
    return {cellSize,mazeWidth,mazeHeight,offsetX: (screenWidth - mazeWidth) / 2,offsetY: MAZE_PADDING;
    };
  }, [maze.size]);
  // 手势处理器
  const panResponder = useMemo() => PanResponder.create({onStartShouldSetPanResponder: () => !isPaused && !isMoving,onMoveShouldSetPanResponder: () => !isPaused && !isMoving,onPanResponderGrant: () => {// 开始手势时的反馈;
      Animated.spring(scaleAnim, {toValue: 1.1,useNativeDriver: true;
      }).start();
    },
    onPanResponderMove: (evt: GestureResponderEvent, gestureState: PanResponderGestureState) => {
      // 可以在这里添加实时预览移动方向的逻辑
    },
    onPanResponderRelease: (evt: GestureResponderEvent, gestureState: PanResponderGestureState) => {
      // 恢复缩放
      Animated.spring(scaleAnim, {
        toValue: 1,
        useNativeDriver: true;
      }).start();
      // 根据手势方向确定移动方向
      const { dx, dy } = gestureState;
      const threshold = 30; // 最小滑动距离
      if (Math.abs(dx) > Math.abs(dy)) {
        // 水平移动
        if (Math.abs(dx) > threshold) {
          const direction = dx > 0 ? Direction.EAST : Direction.WEST;
          onMove?.(direction);
        }
      } else {
        // 垂直移动
        if (Math.abs(dy) > threshold) {
          const direction = dy > 0 ? Direction.SOUTH : Direction.NORTH;
          onMove?.(direction);
        }
      }
    }
  }), [isPaused, isMoving, onMove, scaleAnim]);
  // 更新玩家位置动画
  useEffect() => {
    Animated.timing(playerPosition, {
      toValue: {,
  x: progress.currentPosition.x * renderParams.cellSize + renderParams.cellSize / 2,
        y: progress.currentPosition.y * renderParams.cellSize + renderParams.cellSize / 2;
      },
      duration: gameSettings?.animationSpeed === 'fast' ? 200 :
                gameSettings?.animationSpeed === 'slow' ? 600 : 400,
      useNativeDriver: false;
    }).start();
  }, [progress.currentPosition, renderParams, gameSettings]);
  // 暂停时的旋转动画
  useEffect() => {
    if (isPaused) {
      Animated.loop(
        Animated.timing(rotationAnim, {
          toValue: 1,
          duration: 2000,
          useNativeDriver: true;
        });
      ).start();
    } else {
      rotationAnim.stopAnimation();
      rotationAnim.setValue(0);
    }
  }, [isPaused, rotationAnim]);
  /**
  * 渲染迷宫节点
  */
  const renderMazeNode = (node: MazeNode, x: number, y: number) => {const { cellSize } = renderParams;
    const isVisited = progress.visitedNodes.some(pos => pos.x === x && pos.y === y);
    const isCurrentPosition = progress.currentPosition.x === x && progress.currentPosition.y === y;
    switch (node.nodeType) {
      case NodeType.WALL:
        return (;
          <Rect;
            key={`wall-${x}-${y}`};
            x={x * cellSize};
            y={y * cellSize};
            width={cellSize};
            height={cellSize};
            fill="#2E7D32";
            stroke="#1B5E20";
            strokeWidth={1};
          />;
        );
      case NodeType.PATH:
        return (;
          <Rect;
            key={`path-${x}-${y}`};
            x={x * cellSize};
            y={y * cellSize};
            width={cellSize};
            height={cellSize};
            fill={isVisited ? "#C8E6C9" : "#E8F5E8"};
            stroke="#A5D6A7";
            strokeWidth={0.5};
            opacity={isVisited ? 1 : 0.7};
          />;
        );
      case NodeType.START:
        return (
          <G key={`start-${x}-${y}`}>
            <Rect;
              x={x * cellSize}
              y={y * cellSize}
              width={cellSize}
              height={cellSize};
              fill="#4CAF50";
              stroke="#2E7D32";
              strokeWidth={2};
            />;
            <SvgText;
              x={x * cellSize + cellSize / 2};
              y={y * cellSize + cellSize / 2};
              fontSize={cellSize * 0.3};
              fill="#FFFFFF";
              textAnchor="middle";
              alignmentBaseline="middle";
            >;
              起;
            </SvgText>;
          </G>;
        );
      case NodeType.END:
        return (
          <G key={`end-${x}-${y}`}>
            <Rect;
              x={x * cellSize}
              y={y * cellSize}
              width={cellSize}
              height={cellSize};
              fill="#FF9800";
              stroke="#F57C00";
              strokeWidth={2};
            />;
            <SvgText;
              x={x * cellSize + cellSize / 2};
              y={y * cellSize + cellSize / 2};
              fontSize={cellSize * 0.3};
              fill="#FFFFFF";
              textAnchor="middle";
              alignmentBaseline="middle";
            >;
              终;
            </SvgText>;
          </G>;
        );
      case NodeType.KNOWLEDGE:
        return (
          <G key={`knowledge-${x}-${y}`}>
            <Rect;
              x={x * cellSize}
              y={y * cellSize}
              width={cellSize}
              height={cellSize}
              fill={isVisited ? "#C8E6C9" : "#E8F5E8"}
              stroke="#A5D6A7"
              strokeWidth={0.5}
            />
            <Circle;
              cx={x * cellSize + cellSize / 2}
              cy={y * cellSize + cellSize / 2}
              r={cellSize * 0.3};
              fill={isVisited ? "#81C784" : "#2196F3"};
              stroke="#FFFFFF";
              strokeWidth={2};
            />;
            <SvgText;
              x={x * cellSize + cellSize / 2};
              y={y * cellSize + cellSize / 2};
              fontSize={cellSize * 0.2};
              fill="#FFFFFF";
              textAnchor="middle";
              alignmentBaseline="middle";
            >;
              知;
            </SvgText>;
          </G>;
        );
      case NodeType.CHALLENGE:
        return (
          <G key={`challenge-${x}-${y}`}>
            <Rect;
              x={x * cellSize}
              y={y * cellSize}
              width={cellSize}
              height={cellSize}
              fill={isVisited ? "#C8E6C9" : "#E8F5E8"}
              stroke="#A5D6A7"
              strokeWidth={0.5}
            />
            <Rect;
              x={x * cellSize + cellSize * 0.2}
              y={y * cellSize + cellSize * 0.2}
              width={cellSize * 0.6}
              height={cellSize * 0.6}
              fill={isVisited ? "#FFA726" : "#FF5722"};
              stroke="#FFFFFF";
              strokeWidth={2};
              rx={cellSize * 0.1};
            />;
            <SvgText;
              x={x * cellSize + cellSize / 2};
              y={y * cellSize + cellSize / 2};
              fontSize={cellSize * 0.2};
              fill="#FFFFFF";
              textAnchor="middle";
              alignmentBaseline="middle";
            >;
              战;
            </SvgText>;
          </G>;
        );
      case NodeType.REWARD:
        return (
          <G key={`reward-${x}-${y}`}>
            <Rect;
              x={x * cellSize}
              y={y * cellSize}
              width={cellSize}
              height={cellSize}
              fill={isVisited ? "#C8E6C9" : "#E8F5E8"}
              stroke="#A5D6A7"
              strokeWidth={0.5}
            />
            <Circle;
              cx={x * cellSize + cellSize / 2}
              cy={y * cellSize + cellSize / 2}
              r={cellSize * 0.25};
              fill={isVisited ? "#FFD54F" : "#FFC107"};
              stroke="#FFFFFF";
              strokeWidth={2};
            />;
            <SvgText;
              x={x * cellSize + cellSize / 2};
              y={y * cellSize + cellSize / 2};
              fontSize={cellSize * 0.15};
              fill="#FFFFFF";
              textAnchor="middle";
              alignmentBaseline="middle";
            >;
              奖;
            </SvgText>;
          </G>;
        );
      default:
        return (;
          <Rect;
            key={`empty-${x}-${y}`};
            x={x * cellSize};
            y={y * cellSize};
            width={cellSize};
            height={cellSize};
            fill="#F1F8E9";
            stroke="#DCEDC8";
            strokeWidth={0.5};
          />;
        );
    }
  };
  /**
  * 渲染玩家
  */
  const renderPlayer = () => {const { cellSize } = renderParams;
    const playerRadius = cellSize * 0.35;
    return (;
      <Animated.View;
        style={[;
          styles.playerContainer,{transform: [;
              { translateX: playerPosition.x },{ translateY: playerPosition.y },{ scale: scaleAnim },{rotate: rotationAnim.interpolate({inputRange: [0, 1],outputRange: ["0deg",360deg'];
                });
              }
            ]
          }
        ]}
        {...panResponder.panHandlers}
      >
        <Svg width={playerRadius * 2} height={playerRadius * 2}>
          <Defs>
            <LinearGradient id="playerGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <Stop offset="0%" stopColor="#E91E63" />
              <Stop offset="100%" stopColor="#AD1457" />
            </LinearGradient>
          </Defs>
          <Circle;
            cx={playerRadius}
            cy={playerRadius}
            r={playerRadius * 0.8}
            fill="url(#playerGradient)"
            stroke="#FFFFFF"
            strokeWidth={3}
          />
          <Circle;
            cx={playerRadius * 0.7}
            cy={playerRadius * 0.7}
            r={playerRadius * 0.15}
            fill="#FFFFFF"
          />
          <Circle;
            cx={playerRadius * 1.3}
            cy={playerRadius * 0.7}
            r={playerRadius * 0.15}
            fill="#FFFFFF"
          />
          <Path;
            d={`M ${playerRadius * 0.6} ${playerRadius * 1.2} Q ${playerRadius} ${playerRadius * 1.4} ${playerRadius * 1.4} ${playerRadius * 1.2}`}
            stroke="#FFFFFF"
            strokeWidth={2}
            fill="none"
          />
        </Svg>
      </Animated.View>;
    );
  };
  /**
  * 渲染访问路径
  */
  const renderVisitedPath = () => {if (progress.visitedNodes.length < 2) return null;
    const { cellSize } = renderParams;
    const pathData = progress.visitedNodes;
      .map((pos, index) => {const x = pos.x * cellSize + cellSize / 2;
        const y = pos.y * cellSize + cellSize / 2;
        return index === 0 ? `M ${x} ${y}` : `L ${x} ${y}`;
      })
      .join(' ');
    return (;
      <Path;
        d={pathData};
        stroke="#E91E63";
        strokeWidth={3};
        strokeOpacity={0.6};
        fill="none";
        strokeDasharray="5,5";
      />;
    );
  };
  return (
    <View style={styles.container}>
      <View style={[styles.mazeContainer, {
        width: renderParams.mazeWidth,
        height: renderParams.mazeHeight,
        marginLeft: renderParams.offsetX,
        marginTop: renderParams.offsetY;
      }]}>
        <Svg;
          width={renderParams.mazeWidth}
          height={renderParams.mazeHeight}
          style={styles.mazeSvg}
        >
          <Defs>
            <LinearGradient id="backgroundGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <Stop offset="0%" stopColor="#F1F8E9" />
              <Stop offset="100%" stopColor="#DCEDC8" />
            </LinearGradient>
          </Defs>
          {// 背景}
          <Rect;
            width={renderParams.mazeWidth}
            height={renderParams.mazeHeight}
            fill="url(#backgroundGradient)"
          />
          {// 渲染迷宫节点}
          {maze.nodes.map((row, y) =>
            row.map((node, x) => renderMazeNode(node, x, y))
          )}
          {// 渲染访问路径}
          {renderVisitedPath()}
        </Svg>
        {// 渲染玩家}
        {renderPlayer()}
        {// 暂停遮罩}
        {isPaused && (;
          <View style={styles.pauseOverlay}>;
            <SvgText;
              x="50%";
              y="50%";
              fontSize={24};
              fill="#FFFFFF";
              textAnchor="middle";
              alignmentBaseline="middle";
            >;
              游戏暂停;
            </SvgText>;
          </View>;
        )};
      </View>;
    </View>;
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  mazeContainer: {,
  position: 'relative',
    borderRadius: 10,
    overflow: 'hidden',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84;
  },
  mazeSvg: {,
  position: 'absolute',
    top: 0,
    left: 0;
  },playerContainer: {
      position: "absolute",
      zIndex: 10;
  },pauseOverlay: {
      position: "absolute",
      top: 0,left: 0,right: 0,bottom: 0,backgroundColor: 'rgba(0, 0, 0, 0.5)',justifyContent: 'center',alignItems: 'center',zIndex: 20;
  };
});
export default MazeRenderer;
