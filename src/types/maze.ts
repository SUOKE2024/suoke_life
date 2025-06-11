// 索克生活 - 迷宫类型定义/g/;
export interface MazeConfig {}
  width: number;
  height: number;
  difficulty: 'easy' | 'medium' | 'hard
}

export interface MazeCell {}
  x: number;
  y: number;
  walls: {}
    top: boolean;
    right: boolean;
    bottom: boolean;
    left: boolean;
  
  visited: boolean;
}

export interface MazeState {}
  cells: MazeCell[][];
  playerPosition: { x: number; y: number 
  goalPosition: { x: number; y: number 
  completed: boolean;
}
