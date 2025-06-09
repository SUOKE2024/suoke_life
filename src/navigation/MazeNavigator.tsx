import { createNativeStackNavigator } from '@react-navigation/native-stack';
import React from 'react';
import { Text, View } from 'react-native';

// 临时类型定义
export type MazeTheme = 'classic' | 'dark' | 'nature';
export type MazeDifficulty = 'easy' | 'medium' | 'hard';
export interface GameReward {
  id: string;,
  type: string;
  value: number;
}

export type MazeStackParamList = {
  MazeMain: undefined;,
  MazeGame: {
    mazeId: string;,
  userId: string;
  };
  CreateMaze: undefined;,
  MazeStats: {
    userId: string;
  };
  MazeCompletion: {,
  score: number;
    completionTime: number;,
  stepsCount: number;
    theme: MazeTheme;,
  difficulty: MazeDifficulty;
    rewards: GameReward[];
    isNewRecord?: boolean;
    mazeName: string;
    onPlayAgain?: () => void;
    onBackToMenu?: () => void;
  };
};

// 临时占位符组件
const MazeMainScreen: React.FC = () => (
  <View style={ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
    <Text style={ fontSize: 18, color: '#666' }}>迷宫主屏幕</Text>
    <Text style={ fontSize: 14, color: '#999', marginTop: 8 }}>
      功能开发中...
    </Text>
  </View>
);

const MazeGameScreen: React.FC = () => (
  <View style={ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
    <Text style={ fontSize: 18, color: '#666' }}>迷宫游戏</Text>
    <Text style={ fontSize: 14, color: '#999', marginTop: 8 }}>
      功能开发中...
    </Text>
  </View>
);

const CreateMazeScreen: React.FC = () => (
  <View style={ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
    <Text style={ fontSize: 18, color: '#666' }}>创建迷宫</Text>
    <Text style={ fontSize: 14, color: '#999', marginTop: 8 }}>
      功能开发中...
    </Text>
  </View>
);

const MazeStatsScreen: React.FC = () => (
  <View style={ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
    <Text style={ fontSize: 18, color: '#666' }}>迷宫统计</Text>
    <Text style={ fontSize: 14, color: '#999', marginTop: 8 }}>
      功能开发中...
    </Text>
  </View>
);

const MazeCompletionScreen: React.FC = () => (
  <View style={ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
    <Text style={ fontSize: 18, color: '#666' }}>迷宫完成</Text>
    <Text style={ fontSize: 14, color: '#999', marginTop: 8 }}>
      功能开发中...
    </Text>
  </View>
);

const Stack = createNativeStackNavigator<MazeStackParamList>();

export const MazeNavigator: React.FC = () => {
  return (
    <Stack.Navigator;
      initialRouteName="MazeMain"
      screenOptions={
        headerShown: false,
        animation: 'slide_from_right',
        gestureEnabled: true,
        gestureDirection: 'horizontal',
      }}
    >
      <Stack.Screen;
        name="MazeMain"
        component={MazeMainScreen}
        options={
          gestureEnabled: false,
        }}
      />
      <Stack.Screen;
        name="MazeGame"
        component={MazeGameScreen}
        options={
          animation: 'slide_from_bottom',
          gestureEnabled: false,
        }}
      />
      <Stack.Screen;
        name="CreateMaze"
        component={CreateMazeScreen}
        options={
          animation: 'slide_from_right',
        }}
      />
      <Stack.Screen;
        name="MazeStats"
        component={MazeStatsScreen}
        options={
          animation: 'slide_from_right',
        }}
      />
      <Stack.Screen;
        name="MazeCompletion"
        component={MazeCompletionScreen}
        options={
          animation: 'slide_from_bottom',
          gestureEnabled: false,
        }}
      />
    </Stack.Navigator>
  );
};

export default MazeNavigator;
