import React, { useMemo, useRef, useEffect } from "react";";
import {import Svg, {import {/* ; *//;}*//;,/g/;
View,;
StyleSheet,;
Dimensions,;
Animated,;
PanResponder,;
GestureResponderEvent,";"";
}
  PanResponderGestureState;'}'';'';
} from "react-native";";
Rect,;
Circle,;
Path,;
G,;
Text: as SvgText,;
Defs,;
LinearGradient,;
Stop,;
Pattern,';,'';
const Image = as SvgImage;';'';
} from "react-native-svg";";
Maze,;
MazeProgress,;
GameSettings,;
NodeType,;
Position,;
MazeNode,';,'';
Direction;';'';
} from "../../types/maze";""/;,"/g"/;
interface MazeRendererProps {maze: Maze}progress: MazeProgress,;
isMoving: boolean,;
isPaused: boolean,;
const gameSettings = GameSettings | null;
}
}
  onMove?: (direction: Direction) => void;}';'';
}';,'';
const { width: screenWidth, height: screenHeight ;} = Dimensions.get('window');';'';
// 计算迷宫渲染尺寸/;,/g/;
const MAZE_PADDING = 20;
const AVAILABLE_WIDTH = screenWidth - MAZE_PADDING * 2;
const AVAILABLE_HEIGHT = screenHeight * 0.6; // 60%的屏幕高度用于迷宫/;,/g,/;
  MAX_MAZE_SIZE: Math.min(AVAILABLE_WIDTH, AVAILABLE_HEIGHT);
const  MazeRenderer: React.FC<MazeRendererProps> = ({)maze}progress,;
isMoving,;
isPaused,);
gameSettings,);
}
  onMove;)}
}) => {// 动画值/;}}/g,/;
  playerPosition: useRef(new Animated.ValueXY({x: progress.currentPosition.x,y: progress.currentPosition.y;))}
  })).current;
const scaleAnim = useRef(new Animated.Value(1)).current;
const rotationAnim = useRef(new Animated.Value(0)).current;
  // 计算渲染参数/;,/g/;
const renderParams = useMemo() => {const cellSize = MAX_MAZE_SIZE / maze.size;/;,}const mazeWidth = maze.size * cellSize;,/g/;
const mazeHeight = maze.size * cellSize;
}
    return {cellSize,mazeWidth,mazeHeight,offsetX: (screenWidth - mazeWidth) / 2,offsetY: MAZE_PADDING;}/;/g/;
    };
  }, [maze.size]);
  // 手势处理器/;,/g,/;
  panResponder: useMemo() => PanResponder.create({)onStartShouldSetPanResponder: () => !isPaused && !isMoving,onMoveShouldSetPanResponder: () => !isPaused && !isMoving,onPanResponderGrant: () => {// 开始手势时的反馈;)/;}}/g/;
      Animated.spring(scaleAnim, {toValue: 1.1,useNativeDriver: true;)}
      }).start();
    }
onPanResponderMove: (evt: GestureResponderEvent, gestureState: PanResponderGestureState) => {}}
      // 可以在这里添加实时预览移动方向的逻辑}/;/g/;
    ;}
onPanResponderRelease: (evt: GestureResponderEvent, gestureState: PanResponderGestureState) => {// 恢复缩放/;,}Animated.spring(scaleAnim, {);,}toValue: 1,);/g/;
}
        const useNativeDriver = true;)}
      }).start();
      // 根据手势方向确定移动方向/;,/g/;
const { dx, dy } = gestureState;
const threshold = 30; // 最小滑动距离/;,/g/;
if (Math.abs(dx) > Math.abs(dy)) {// 水平移动/;,}if (Math.abs(dx) > threshold) {const direction = dx > 0 ? Direction.EAST : Direction.WEST;}}/g/;
          onMove?.(direction);}
        }
      } else {// 垂直移动/;,}if (Math.abs(dy) > threshold) {const direction = dy > 0 ? Direction.SOUTH : Direction.NORTH;}}/g/;
          onMove?.(direction);}
        }
      }
    }
  }), [isPaused, isMoving, onMove, scaleAnim]);
  // 更新玩家位置动画/;,/g/;
useEffect() => {Animated.timing(playerPosition, {)      toValue: {x: progress.currentPosition.x * renderParams.cellSize + renderParams.cellSize / 2,/;/g/;
}
        const y = progress.currentPosition.y * renderParams.cellSize + renderParams.cellSize / 2;}'/;'/g'/;
      },';,'';
duration: gameSettings?.animationSpeed === 'fast' ? 200 :')'';
gameSettings?.animationSpeed === 'slow' ? 600 : 400;')'';
const useNativeDriver = false;);
    }).start();
  }, [progress.currentPosition, renderParams, gameSettings]);
  // 暂停时的旋转动画/;,/g/;
useEffect() => {if (isPaused) {}      Animated.loop();
Animated.timing(rotationAnim, {)          toValue: 1,);,}duration: 2000,);
}
          const useNativeDriver = true;)}
        });
      ).start();
    } else {rotationAnim.stopAnimation();}}
      rotationAnim.setValue(0);}
    }
  }, [isPaused, rotationAnim]);
  /* 点 *//;/g/;
  *//;,/g,/;
  renderMazeNode: useCallback((node: MazeNode, x: number, y: number) => {const { cellSize ;} = renderParams;
const isVisited = progress.visitedNodes.some(pos => pos.x === x && pos.y === y);
const isCurrentPosition = progress.currentPosition.x === x && progress.currentPosition.y === y;
switch (node.nodeType) {const case = NodeType.WALL: ;,}return (;);
}
          <Rect;}  />/;,/g/;
key={`wall-${x}-${y}`};````;,```;
x={x * cellSize};
y={y * cellSize};
width={cellSize};';,'';
height={cellSize};';,'';
fill="#2E7D32";";,"";
stroke="#1B5E20";";,"";
strokeWidth={1};
          />;/;/g/;
        );
const case = NodeType.PATH: ;
return (;);
          <Rect;  />/;,/g/;
key={`path-${x}-${y}`};````;,```;
x={x * cellSize};
y={y * cellSize};
width={cellSize};";,"";
height={cellSize};";,"";
fill={isVisited ? "#C8E6C9" : "#E8F5E8"};";,"";
stroke="#A5D6A7";";,"";
strokeWidth={0.5};
opacity={isVisited ? 1 : 0.7};
          />;/;/g/;
        );
const case = NodeType.START: ;
return (<G key={`start-${x;}-${y}`}>````;)            <Rect;  />/;,`/g`/`;
x={x * cellSize}
              y={y * cellSize}
              width={cellSize}";,"";
height={cellSize};";,"";
fill="#4CAF50";";,"";
stroke="#2E7D32";";,"";
strokeWidth={2};
            />;/;/g/;
            <SvgText;  />/;,/g/;
x={x * cellSize + cellSize / 2};/;,/g/;
y={y * cellSize + cellSize / 2};"/;,"/g"/;
fontSize={cellSize * 0.3};";,"";
fill="#FFFFFF";";,"";
textAnchor="middle";";,"";
alignmentBaseline="middle";";"";
            >;
);
            </SvgText>;)/;/g/;
          </G>;)/;/g/;
        );
const case = NodeType.END: ;
return (<G key={`end-${x;}-${y}`}>````;)            <Rect;  />/;,`/g`/`;
x={x * cellSize}
              y={y * cellSize}
              width={cellSize}";,"";
height={cellSize};";,"";
fill="#FF9800";";,"";
stroke="#F57C00";";,"";
strokeWidth={2};
            />;/;/g/;
            <SvgText;  />/;,/g/;
x={x * cellSize + cellSize / 2};/;,/g/;
y={y * cellSize + cellSize / 2};"/;,"/g"/;
fontSize={cellSize * 0.3};";,"";
fill="#FFFFFF";";,"";
textAnchor="middle";";,"";
alignmentBaseline="middle";";"";
            >;
);
            </SvgText>;)/;/g/;
          </G>;)/;/g/;
        );
const case = NodeType.KNOWLEDGE: ;
return (<G key={`knowledge-${x;}-${y}`}>````;)            <Rect;  />/;,`/g`/`;
x={x * cellSize}
              y={y * cellSize}
              width={cellSize}";,"";
height={cellSize}";,"";
fill={isVisited ? "#C8E6C9" : "#E8F5E8"}";,"";
stroke="#A5D6A7";
strokeWidth={0.5}
            />/;/g/;
            <Circle;  />/;,/g/;
cx={x * cellSize + cellSize / 2}/;,/g/;
cy={y * cellSize + cellSize / 2}"/;,"/g"/;
r={cellSize * 0.3};";,"";
fill={isVisited ? "#81C784" : "#2196F3"};";,"";
stroke="#FFFFFF";";,"";
strokeWidth={2};
            />;/;/g/;
            <SvgText;  />/;,/g/;
x={x * cellSize + cellSize / 2};/;,/g/;
y={y * cellSize + cellSize / 2};"/;,"/g"/;
fontSize={cellSize * 0.2};";,"";
fill="#FFFFFF";";,"";
textAnchor="middle";";,"";
alignmentBaseline="middle";";"";
            >;
);
            </SvgText>;)/;/g/;
          </G>;)/;/g/;
        );
const case = NodeType.CHALLENGE: ;
return (<G key={`challenge-${x;}-${y}`}>````;)            <Rect;  />/;,`/g`/`;
x={x * cellSize}
              y={y * cellSize}
              width={cellSize}";,"";
height={cellSize}";,"";
fill={isVisited ? "#C8E6C9" : "#E8F5E8"}";,"";
stroke="#A5D6A7";
strokeWidth={0.5}
            />/;/g/;
            <Rect;  />/;,/g/;
x={x * cellSize + cellSize * 0.2}
              y={y * cellSize + cellSize * 0.2}
              width={cellSize * 0.6}";,"";
height={cellSize * 0.6}";,"";
fill={isVisited ? "#FFA726" : "#FF5722"};";,"";
stroke="#FFFFFF";";,"";
strokeWidth={2};
rx={cellSize * 0.1};
            />;/;/g/;
            <SvgText;  />/;,/g/;
x={x * cellSize + cellSize / 2};/;,/g/;
y={y * cellSize + cellSize / 2};"/;,"/g"/;
fontSize={cellSize * 0.2};";,"";
fill="#FFFFFF";";,"";
textAnchor="middle";";,"";
alignmentBaseline="middle";";"";
            >;
);
            </SvgText>;)/;/g/;
          </G>;)/;/g/;
        );
const case = NodeType.REWARD: ;
return (<G key={`reward-${x;}-${y}`}>````;)            <Rect;  />/;,`/g`/`;
x={x * cellSize}
              y={y * cellSize}
              width={cellSize}";,"";
height={cellSize}";,"";
fill={isVisited ? "#C8E6C9" : "#E8F5E8"}";,"";
stroke="#A5D6A7";
strokeWidth={0.5}
            />/;/g/;
            <Circle;  />/;,/g/;
cx={x * cellSize + cellSize / 2}/;,/g/;
cy={y * cellSize + cellSize / 2}"/;,"/g"/;
r={cellSize * 0.25};";,"";
fill={isVisited ? "#FFD54F" : "#FFC107"};";,"";
stroke="#FFFFFF";";,"";
strokeWidth={2};
            />;/;/g/;
            <SvgText;  />/;,/g/;
x={x * cellSize + cellSize / 2};/;,/g/;
y={y * cellSize + cellSize / 2};"/;,"/g"/;
fontSize={cellSize * 0.15};";,"";
fill="#FFFFFF";";,"";
textAnchor="middle";";,"";
alignmentBaseline="middle";";"";
            >;
);
            </SvgText>;)/;/g/;
          </G>;)/;/g/;
        );
const default = return (;);
          <Rect;  />/;,/g/;
key={`empty-${x}-${y}`};````;,```;
x={x * cellSize};
y={y * cellSize};
width={cellSize};";,"";
height={cellSize};";,"";
fill="#F1F8E9";";,"";
stroke="#DCEDC8";";,"";
strokeWidth={0.5};
          />;/;/g/;
        );
    }
  };
  /* 家 *//;/g/;
  *//;,/g/;
const renderPlayer = useCallback(() => {const { cellSize } = renderParams;
const playerRadius = cellSize * 0.35;
return (;);
      <Animated.View;  />/;,/g/;
style={[;];";}}"";
          styles.playerContainer,{transform: [;"}"";]];"";
              { translateX: playerPosition.x ;}},{ translateY: playerPosition.y ;},{ scale: scaleAnim ;},{rotate: rotationAnim.interpolate({inputRange: [0, 1],outputRange: ["0deg",360deg'];)'}'';'';
                });
              }
            ];
          }
        ]}
        {...panResponder.panHandlers}
      >;
        <Svg width={playerRadius * 2} height={playerRadius * 2}>';'';
          <Defs>';'';
            <LinearGradient id="playerGradient" x1="0%" y1="0%" x2="100%" y2="100%">";"";
              <Stop offset="0%" stopColor="#E91E63"  />"/;"/g"/;
              <Stop offset="100%" stopColor="#AD1457"  />"/;"/g"/;
            </LinearGradient>/;/g/;
          </Defs>/;/g/;
          <Circle;  />/;,/g/;
cx={playerRadius}
            cy={playerRadius}";,"";
r={playerRadius * 0.8}";,"";
fill="url(#playerGradient)";
stroke="#FFFFFF";
strokeWidth={3}
          />/;/g/;
          <Circle;  />/;,/g/;
cx={playerRadius * 0.7}
            cy={playerRadius * 0.7}";,"";
r={playerRadius * 0.15}";,"";
fill="#FFFFFF"";"";
          />/;/g/;
          <Circle;  />/;,/g/;
cx={playerRadius * 1.3}
            cy={playerRadius * 0.7}";,"";
r={playerRadius * 0.15}";,"";
fill="#FFFFFF"";"";
          />/;/g/;
          <Path;"  />/;,"/g"/;
d={`M ${playerRadius * 0.6} ${playerRadius * 1.2} Q ${playerRadius} ${playerRadius * 1.4} ${playerRadius * 1.4} ${playerRadius * 1.2}`}``"`;,```;
stroke="#FFFFFF";
strokeWidth={2}";,"";
fill="none"";"";
          />/;/g/;
        </Svg>/;/g/;
      </Animated.View>;/;/g/;
    );
  };
  /* 径 *//;/g/;
  *//;,/g/;
const renderVisitedPath = useCallback(() => {if (progress.visitedNodes.length < 2) return null;}
    const { cellSize } = renderParams;
const pathData = progress.visitedNodes;
      .map(pos, index) => {const x = pos.x * cellSize + cellSize / 2;)/;}}/g/;
        const y = pos.y * cellSize + cellSize / 2;}/;,/g/;
return index === 0 ? `M ${x} ${y}` : `L ${x} ${y}`;``"`;```;
      })";"";
      .join(' ');';,'';
return (;);
      <Path;'  />/;,'/g'/;
d={pathData};';,'';
stroke="#E91E63";";,"";
strokeWidth={3};";,"";
strokeOpacity={0.6};";,"";
fill="none";";,"";
strokeDasharray="5,5";";"";
      />;/;/g/;
    );
  };
return (<View style={styles.container}>;)      <View style={ />/;}[;,]styles.mazeContainer, {width: renderParams.mazeWidth}height: renderParams.mazeHeight,;,/g,/;
  marginLeft: renderParams.offsetX,;
}
        const marginTop = renderParams.offsetY;}
];
      }}]}>;
        <Svg;  />/;,/g/;
width={renderParams.mazeWidth}
          height={renderParams.mazeHeight}
          style={styles.mazeSvg}
        >";"";
          <Defs>";"";
            <LinearGradient id="backgroundGradient" x1="0%" y1="0%" x2="100%" y2="100%">";"";
              <Stop offset="0%" stopColor="#F1F8E9"  />"/;"/g"/;
              <Stop offset="100%" stopColor="#DCEDC8"  />"/;"/g"/;
            </LinearGradient>/;/g/;
          </Defs>/;/g/;
          {// 背景}/;/g/;
          <Rect;)  />/;,/g/;
width={renderParams.mazeWidth})";,"";
height={renderParams.mazeHeight})";,"";
fill="url(#backgroundGradient)"";"";
          />/;/g/;
          {// 渲染迷宫节点}/;/g/;
          {maze.nodes.map(row, y) =>);}}
            row.map(node, x) => renderMazeNode(node, x, y))}
          )}
          {// 渲染访问路径}/;/g/;
          {renderVisitedPath()}
        </Svg>/;/g/;
        {// 渲染玩家}/;/g/;
        {renderPlayer()}
        {// 暂停遮罩}/;/g/;
        {isPaused && (;)}
          <View style={styles.pauseOverlay}>;";"";
            <SvgText;"  />/;,"/g"/;
x="50%";";,"";
y="50%";";,"";
fontSize={24};";,"";
fill="#FFFFFF";";,"";
textAnchor="middle";";,"";
alignmentBaseline="middle";";"";
            >;

            </SvgText>;/;/g/;
          </View>;/;/g/;
        )};
      </View>;/;/g/;
    </View>;/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,";,}flex: 1,";,"";
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;},';,'';
mazeContainer: {,';,}position: 'relative';','';
borderRadius: 10,';,'';
overflow: 'hidden';','';
elevation: 5,';'';
}
    shadowColor: '#000';','}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.25,;
const shadowRadius = 3.84;
  },';,'';
mazeSvg: {,';,}position: 'absolute';','';
top: 0,;
}
    const left = 0;}';'';
  },playerContainer: {,';,}position: "absolute";","";"";
}
      const zIndex = 10;)}";"";
  },pauseOverlay: {,)";,}position: "absolute";",)"";"";
}
      top: 0,left: 0,right: 0,bottom: 0,backgroundColor: 'rgba(0, 0, 0, 0.5)',justifyContent: 'center',alignItems: 'center',zIndex: 20;'}'';'';
  };
});';,'';
export default MazeRenderer;