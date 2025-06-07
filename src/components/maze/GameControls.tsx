import React, { useRef } from 'react';
import {import Icon from 'react-native-vector-icons/MaterialIcons';
import { Direction, GameSettings } from '../../types/maze';
/**
* 游戏控制组件
* Game Controls Component;
*/
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Vibration,
  Dimensions;
} from 'react-native';
interface GameControlsProps {
  onMove: (direction: Direction) => void;
  disabled: boolean;
  gameSettings: GameSettings | null;
}
const { width: screenWidth } = Dimensions.get('window');
const GameControls: React.FC<GameControlsProps> = ({
  onMove,
  disabled,
  gameSettings;
}) => {
  // 动画引用
  const buttonScales = useRef({[Direction.NORTH]: new Animated.Value(1),[Direction.EAST]: new Animated.Value(1),[Direction.SOUTH]: new Animated.Value(1),[Direction.WEST]: new Animated.Value(1);
  }).current;
  /**
  * 处理按钮按下
  */
  const handlePressIn = (direction: Direction) => {if (disabled) return;
    // 触觉反馈
    if (gameSettings?.vibrationEnabled) {
      Vibration.vibrate(50);
    }
    // 按钮缩放动画
    Animated.spring(buttonScales[direction], {
      toValue: 0.9,
      useNativeDriver: true;
    }).start();
  };
  /**
  * 处理按钮释放
  */
  const handlePressOut = (direction: Direction) => {// 恢复按钮大小;
    Animated.spring(buttonScales[direction], {toValue: 1,useNativeDriver: true;
    }).start();
    if (!disabled) {
      onMove(direction);
    }
  };
  /**
  * 渲染方向按钮
  */
  const renderDirectionButton = (
    direction: Direction,iconName: string,style: any,label: string;
  ) => {return (;
      <Animated.View;
        style={[;
          styles.directionButton,style,{transform: [{ scale: buttonScales[direction] }],opacity: disabled ? 0.5 : 1;
          };
        ]};
      >;
        <TouchableOpacity;
          style={styles.buttonTouchable};
          onPressIn={() => handlePressIn(direction)};
          onPressOut={() => handlePressOut(direction)};
          disabled={disabled};
          activeOpacity={0.8};
        >;
          <Icon name={iconName} size={32} color="#FFFFFF" />;
          <Text style={styles.buttonLabel}>{label}</Text>;
        </TouchableOpacity>;
      </Animated.View>;
    );
  };
  return (
    <View style={styles.container}>
      {// 控制说明}
      <View style={styles.instructionContainer}>
        <Text style={styles.instructionText}>
          {disabled ? '移动中...' : '点击方向键或滑动屏幕移动'}
        </Text>
      </View>
      {// 方向控制器}
      <View style={styles.controlsContainer}>
        {// 上方向键}
        {renderDirectionButton(
          Direction.NORTH,
          'keyboard-arrow-up',
          styles.northButton,
          '北'
        )}
        {// 中间行：左、右方向键}
        <View style={styles.middleRow}>
          {renderDirectionButton(
            Direction.WEST,
            'keyboard-arrow-left',
            styles.westButton,
            '西'
          )}
          {// 中心指示器}
          <View style={styles.centerIndicator}>
            <Icon name="my-location" size={24} color="#4CAF50" />
          </View>
          {renderDirectionButton(
            Direction.EAST,
            'keyboard-arrow-right',
            styles.eastButton,
            '东'
          )}
        </View>
        {// 下方向键}
        {renderDirectionButton(
          Direction.SOUTH,
          'keyboard-arrow-down',
          styles.southButton,
          '南'
        )}
      </View>
      {// 控制提示}
      <View style={styles.hintContainer}>
        <View style={styles.hintItem}>;
          <Icon name="touch-app" size={16} color="#81C784" />;
          <Text style={styles.hintText}>点击移动</Text>;
        </View>;
        <View style={styles.hintItem}>;
          <Icon name="swipe" size={16} color="#81C784" />;
          <Text style={styles.hintText}>滑动控制</Text>;
        </View>;
        {gameSettings?.vibrationEnabled && (;
          <View style={styles.hintItem}>;
            <Icon name="vibration" size={16} color="#81C784" />;
            <Text style={styles.hintText}>触觉反馈</Text>;
          </View>;
        )};
      </View>;
    </View>;
  );
};
const styles = StyleSheet.create({
  container: {,
  backgroundColor: '#1B5E20',
    paddingVertical: 20,
    paddingHorizontal: 16,
    alignItems: 'center'
  },
  instructionContainer: {,
  marginBottom: 16;
  },
  instructionText: {,
  color: '#C8E6C9',
    fontSize: 14,
    textAlign: 'center',
    fontWeight: '500'
  },
  controlsContainer: {,
  alignItems: 'center',
    marginBottom: 16;
  },
  directionButton: {,
  width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#2E7D32',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84;
  },
  buttonTouchable: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 30;
  },
  buttonLabel: {,
  color: '#FFFFFF',
    fontSize: 10,
    fontWeight: 'bold',
    marginTop: 2;
  },
  northButton: {,
  marginBottom: 12;
  },
  southButton: {,
  marginTop: 12;
  },
  middleRow: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center'
  },
  westButton: {,
  marginRight: 20;
  },
  eastButton: {,
  marginLeft: 20;
  },
  centerIndicator: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#388E3C',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#4CAF50'
  },
  hintContainer: {,
  flexDirection: 'row',justifyContent: 'center',flexWrap: 'wrap',marginTop: 8;
  },hintItem: {
      flexDirection: "row",
      alignItems: 'center',marginHorizontal: 8,marginVertical: 4;
  },hintText: {
      color: "#81C784",
      fontSize: 12,marginLeft: 4;
  };
});
export default GameControls;
