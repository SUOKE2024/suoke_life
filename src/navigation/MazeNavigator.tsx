import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { MazeMainScreen, MazeGameScreen, CreateMazeScreen } from '../screens/maze';
import { MazeStatsScreen, MazeCompletionScreen } from '../components/maze';
import { MazeTheme, MazeDifficulty, GameReward } from '../types/maze';

export type MazeStackParamList = {
  MazeMain: undefined;
  MazeGame: {
    mazeId: string;
    userId: string;
  };
  CreateMaze: undefined;
  MazeStats: {
    userId: string;
  };
  MazeCompletion: {
    score: number;
    completionTime: number;
    stepsCount: number;
    theme: MazeTheme;
    difficulty: MazeDifficulty;
    rewards: GameReward[];
    isNewRecord?: boolean;
    mazeName: string;
    onPlayAgain?: () => void;
    onBackToMenu?: () => void;
  };
};

const Stack = createNativeStackNavigator<MazeStackParamList>();

export const MazeNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      initialRouteName="MazeMain"
      screenOptions={{
        headerShown: false,
        animation: 'slide_from_right',
        gestureEnabled: true,
        gestureDirection: 'horizontal',
      }}
    >
      <Stack.Screen
        name="MazeMain"
        component={MazeMainScreen}
        options={{
          gestureEnabled: false,
        }}
      />
      <Stack.Screen
        name="MazeGame"
        component={MazeGameScreen}
        options={{
          animation: 'slide_from_bottom',
          gestureEnabled: false,
        }}
      />
      <Stack.Screen
        name="CreateMaze"
        component={CreateMazeScreen}
        options={{
          animation: 'slide_from_right',
        }}
      />
      <Stack.Screen
        name="MazeStats"
        component={MazeStatsScreen}
        options={{
          animation: 'slide_from_right',
        }}
      />
      <Stack.Screen
        name="MazeCompletion"
        component={MazeCompletionScreen}
        options={{
          animation: 'slide_from_bottom',
          gestureEnabled: false,
        }}
      />
    </Stack.Navigator>
  );
};

export default MazeNavigator; 