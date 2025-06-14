import React from "react"
import {import Icon from "react-native-vector-icons/MaterialIcons";} frommport { MazeProgress } from "../../types/maze";
/* ; */
*/
View,
Text,
StyleSheet,"
TouchableOpacity,
Dimensions;
} from "react-native;
interface ProgressDisplayProps {progress: MazeProgress}gameTime: number,
isPaused: boolean,
onPause: () => void,
onResume: () => void,
onSettings: () => void,
}
}
  onExit: () => void}
}
const { width: screenWidth ;} = Dimensions.get('window');
const  ProgressDisplay: React.FC<ProgressDisplayProps> = ({)progress}gameTime,
isPaused,
onPause,
onResume,);
onSettings,);
}
  onExit;)}
}) => {/* 示 *//;}  */
const formatTime = (seconds: number): string => {const minutes = Math.floor(seconds / 60);'/;}}'/g'/;
    const remainingSeconds = seconds % 60;'}
return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;````;```;
  };
  /* 比 */
  */
const getCompletionPercentage = (): number => {const totalNodes = progress.visitedNodes.lengthconst knowledgeNodes = progress.acquiredKnowledge.length;
const challenges = progress.completedChallenges.length;
    // 简单的完成度计算：基于访问的节点数
}
    return Math.min(100, Math.floor(totalNodes / 50) * 100)); // 假设50个节点为满分}
  };
return (<View style={styles.container}>;)      {// 顶部状态栏}
      <View style={styles.topBar}>;
        {// 左侧：游戏控制}
        <View style={styles.leftSection}>;
          <TouchableOpacity;  />
style={styles.controlButton}
            onPress={isPaused ? onResume : onPause}
          >'
            <Icon;'  />/,'/g'/;
name={isPaused ? 'play-arrow' : 'pause'}
size={24}
color="#FFFFFF;
            />
          </TouchableOpacity>
          <TouchableOpacity;  />
style={styles.controlButton}
            onPress={onSettings}
          >
            <Icon name="settings" size={24} color="#FFFFFF"  />"/;"/g"/;
          </TouchableOpacity>
        </View>
        {// 中间：时间显示}
        <View style={styles.centerSection}>)
          <View style={styles.timeContainer}>)
            <Icon name="access-time" size={16} color="#C8E6C9"  />")
            <Text style={styles.timeText}>{formatTime(gameTime)}</Text>
          </View>
          {isPaused  && <Text style={styles.pausedText}>已暂停</Text>
          )}
        </View>
        {// 右侧：退出按钮}
        <View style={styles.rightSection}>;
          <TouchableOpacity;  />
style={styles.exitButton}
            onPress={onExit}
          >
            <Icon name="close" size={24} color="#FFFFFF"  />"/;"/g"/;
          </TouchableOpacity>
        </View>
      </View>
      {// 进度信息栏}
      <View style={styles.progressBar}>;
        {// 分数}"/;"/g"/;
        <View style={styles.statItem}>
          <Icon name="star" size={16} color="#FFD54F"  />"/;"/g"/;
          <Text style={styles.statValue}>{progress.score}</Text>
          <Text style={styles.statLabel}>分数</Text>
        </View>"
        {// 步数}"/;"/g"/;
        <View style={styles.statItem}>
          <Icon name="directions-walk" size={16} color="#81C784"  />"/;"/g"/;
          <Text style={styles.statValue}>{progress.stepsCount}</Text>
          <Text style={styles.statLabel}>步数</Text>
        </View>"
        {// 知识点}"/;"/g"/;
        <View style={styles.statItem}>
          <Icon name="school" size={16} color="#64B5F6"  />"/;"/g"/;
          <Text style={styles.statValue}>{progress.acquiredKnowledge.length}</Text>
          <Text style={styles.statLabel}>知识</Text>
        </View>"
        {// 挑战}"/;"/g"/;
        <View style={styles.statItem}>
          <Icon name="emoji-events" size={16} color="#FF8A65"  />"/;"/g"/;
          <Text style={styles.statValue}>{progress.completedChallenges.length}</Text>
          <Text style={styles.statLabel}>挑战</Text>
        </View>"
        {// 完成度}"/;"/g"/;
        <View style={styles.statItem}>
          <Icon name="trending-up" size={16} color="#A5D6A7"  />"/;"/g"/;
          <Text style={styles.statValue}>{getCompletionPercentage()}%</Text>
          <Text style={styles.statLabel}>完成</Text>
        </View>
      </View>
      {// 进度条}
      <View style={styles.progressBarContainer}>;
        <View style={styles.progressBarBackground}>;
          <View;  />
style={}[;]}
              styles.progressBarFill,}
              { width: `${getCompletionPercentage();}}%` }````;```;
];
            ]};
          />;
        </View>;
        <Text style={styles.progressText}>;
        </Text>;
      </View>;
      {// 当前位置信息};"/;"/g"/;
      <View style={styles.locationInfo}>;
        <Icon name="my-location" size={14} color="#C8E6C9"  />;"/;"/g"/;
        <Text style={styles.locationText}>;
        </Text>;
      </View>;
    </View>;
  );
};
const  styles = StyleSheet.create({)"container: {,"backgroundColor: '#2E7D32,'';
paddingTop: 8,
paddingBottom: 12,
}
    const paddingHorizontal = 16}
  },'
topBar: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'
}
    const marginBottom = 12}
  },'
leftSection: {,'flexDirection: 'row,'
}
    const alignItems = 'center'}
  ;},'
centerSection: {,';}}
  const alignItems = 'center'}
  ;},'
rightSection: {,';}}
  const alignItems = 'flex-end'}
  }
controlButton: {width: 40,
height: 40,
borderRadius: 20,'
backgroundColor: '#388E3C,'
justifyContent: 'center,'
alignItems: 'center,'
}
    const marginRight = 8}
  }
exitButton: {width: 40,
height: 40,
borderRadius: 20,'
backgroundColor: '#D32F2F,'
justifyContent: 'center,'
}
    const alignItems = 'center'}
  ;},'
timeContainer: {,')''flexDirection: 'row,')'
alignItems: 'center)','
backgroundColor: 'rgba(255, 255, 255, 0.1)',
paddingHorizontal: 12,
paddingVertical: 6,
}
    const borderRadius = 16}
  },'
timeText: {,'color: '#FFFFFF,'';
fontSize: 16,'
fontWeight: 'bold,'';
marginLeft: 4,
}
    const fontFamily = 'monospace'}
  ;},'
pausedText: {,'color: '#FFB74D,'';
fontSize: 12,'
fontWeight: 'bold,'
}
    const marginTop = 2}
  },'
progressBar: {,'flexDirection: 'row,'
justifyContent: 'space-around,'
alignItems: 'center,'
backgroundColor: 'rgba(255, 255, 255, 0.1)',
borderRadius: 12,
paddingVertical: 8,
}
    const marginBottom = 8}
  },'
statItem: {,'alignItems: 'center,'
}
    const minWidth = 50}
  },'
statValue: {,'color: '#FFFFFF,'';
fontSize: 14,'
fontWeight: 'bold,'
}
    const marginTop = 2}
  },'
statLabel: {,'color: '#C8E6C9,'';
fontSize: 10,
}
    const marginTop = 1}
  }
progressBarContainer: {,}
  const marginBottom = 6}
  }
progressBarBackground: {,'height: 6,'
backgroundColor: 'rgba(255, 255, 255, 0.2)',
borderRadius: 3,
}
    const overflow = 'hidden'}
  ;},'
progressBarFill: {,'height: '100%,'
backgroundColor: '#4CAF50,'
}
    const borderRadius = 3}
  },'
progressText: {,';}}
  color: '#C8E6C9',fontSize: 11,textAlign: 'center',marginTop: 4;'}
  },locationInfo: {,'flexDirection: "row,
}
      alignItems: 'center',justifyContent: 'center}
  },locationText: {,'color: "#C8E6C9,
}
      fontSize: 11,marginLeft: 4,fontFamily: 'monospace}
  };
});
export default ProgressDisplay;
