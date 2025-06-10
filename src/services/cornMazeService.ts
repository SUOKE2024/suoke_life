import { apiClient } from "./apiClient";""/;,"/g"/;
import {/* ; *//;}*//;,/g/;
Maze,;
MazeProgress,;
MazeTemplate,;
KnowledgeNode,;
Challenge,;
MazeStats,;
LeaderboardEntry,;
GameSettings,;
MazeInteraction,;
CreateMazeRequest,;
UpdateMazeRequest,;
StartMazeRequest,;
MoveRequest,;
ListMazesRequest,;
MazeResponse,;
MoveResponse,;
UserProgressResponse,;
ListMazesResponse,;
ListTemplatesResponse,;
Direction,;
Position,;
MazeTheme,;
MazeDifficulty,";"";
}
  GameReward;'}'';'';
} from "../types/maze";""/;"/g"/;
/* 置 *//;/g/;
*//;,/g/;
interface CornMazeServiceConfig {baseURL: string}timeout: number,;
retryAttempts: number,;
}
}
  const enableCache = boolean;}
}
/* 置 *//;/g/;
*/'/;,'/g,'/;
  const: DEFAULT_CONFIG: CornMazeServiceConfig = {,';,}baseURL: process.env.CORN_MAZE_SERVICE_URL || 'http://localhost:51057';',''/;,'/g,'/;
  timeout: 10000,;
retryAttempts: 3,;
}
  const enableCache = true;}
};
/* 类 *//;/g/;
*//;,/g/;
export class CornMazeService {;,}private config: CornMazeServiceConfig;
private cache: Map<string, any> = new Map();
private cacheTimeout: number = 5 * 60 * 1000; // 5分钟缓存/;/g/;
}
}
  constructor(config?: Partial<CornMazeServiceConfig>) {}
    this.config = { ...DEFAULT_CONFIG; ...config };
  }
  /* 查 *//;/g/;
  *//;,/g/;
const async = healthCheck(): Promise<{ status: string; version: string; timestamp: string ;}> {}}
    try {}
      const response = await apiClient.get(`${this.config.baseURL}/health`);```/`;,`/g`/`;
return response.data;';'';
    } catch (error) {';,}console.error('Corn Maze Service health check failed:', error);';'';
}
}
    }
  }
  /* 宫 *//;/g/;
  *//;,/g/;
const async = createMaze(request: CreateMazeRequest): Promise<Maze> {try {}}
      const response = await apiClient.post<MazeResponse>(;)}
        `${this.config.baseURL}/api/v1/mazes`,request;```/`;`/g`/`;
      );
return response.data.maze;';'';
    } catch (error) {';,}console.error('Failed to create maze:', error);';'';
}
}
    }
  }
  /* 息 *//;/g/;
  */'/;,'/g,'/;
  async: getMaze(mazeId: string, userId?: string): Promise<MazeResponse> {'}'';
const cacheKey = `maze_${mazeId;}_${userId || 'anonymous'}`;````;```;
    // 检查缓存/;,/g/;
if (this.config.enableCache && this.cache.has(cacheKey)) {const cached = this.cache.get(cacheKey);,}if (Date.now() - cached.timestamp < this.cacheTimeout) {}}
        return cached.data;}
      }
    }
    try {}
      const params = userId ? { user_id: userId ;} : {};
const response = await apiClient.get<MazeResponse>(;);
        `${this.config.baseURL}/api/v1/mazes/${mazeId}`,{ params };```/`;`/g`/`;
      );
      // 缓存结果/;,/g/;
if (this.config.enableCache) {this.cache.set(cacheKey, {);,}data: response.data,);
}
          const timestamp = Date.now();}
        });
      }
      return response.data;';'';
    } catch (error) {';,}console.error('Failed to get maze:', error);';'';
}
}
    }
  }
  /* 宫 *//;/g/;
  *//;,/g,/;
  async: updateMaze(mazeId: string, request: UpdateMazeRequest): Promise<Maze> {try {}}
      const response = await apiClient.put<MazeResponse>(;)}
        `${this.config.baseURL}/api/v1/mazes/${mazeId}`,request;```/`;`/g`/`;
      );
      // 清除相关缓存/;,/g/;
this.clearMazeCache(mazeId);
return response.data.maze;';'';
    } catch (error) {';,}console.error('Failed to update maze:', error);';'';
}
}
    }
  }
  /* 宫 *//;/g/;
  *//;,/g/;
const async = deleteMaze(mazeId: string): Promise<void> {}}
    try {}
      const await = apiClient.delete(`${this.config.baseURL;}/api/v1/mazes/${mazeId}`);```/`;`/g`/`;
      // 清除相关缓存/;,/g/;
this.clearMazeCache(mazeId);';'';
    } catch (error) {';,}console.error('Failed to delete maze:', error);';'';
}
}
    }
  }
  /* 表 *//;/g/;
  *//;,/g/;
const async = listMazes(request?: ListMazesRequest): Promise<ListMazesResponse> {try {}}
      const response = await apiClient.get<ListMazesResponse>(;)}
        `${this.config.baseURL}/api/v1/mazes`,{ params: request ;};```/`;`/g`/`;
      );
return response.data;';'';
    } catch (error) {';,}console.error('Failed to list mazes:', error);';'';
}
}
    }
  }
  /* 戏 *//;/g/;
  *//;,/g/;
const async = startMaze(request: StartMazeRequest): Promise<MazeProgress> {}}
    try {}
      const response = await apiClient.post<{ progress: MazeProgress ;}>(;);
        `${this.config.baseURL}/api/v1/mazes/${request.mazeId}/start`,{ user_id: request.userId ;};```/`;`/g`/`;
      );
return response.data.progress;';'';
    } catch (error) {';,}console.error('Failed to start maze:', error);';'';
}
}
    }
  }
  /* 动 *//;/g/;
  *//;,/g/;
const async = moveInMaze(request: MoveRequest): Promise<MoveResponse> {try {}}
      const response = await apiClient.post<MoveResponse>(;)}
        `${this.config.baseURL}/api/v1/mazes/${request.mazeId}/move`,{user_id: request.userId,direction: request.direction;``}``/`;`/g`/`;
        };
      );
      // 清除进度缓存/;,/g/;
this.clearProgressCache(request.userId, request.mazeId);
return response.data;';'';
    } catch (error) {';,}console.error('Failed to move in maze:', error);';'';
}
}
    }
  }
  /* 度 *//;/g/;
  *//;,/g,/;
  async: getUserProgress(mazeId: string, userId: string): Promise<UserProgressResponse> {}
    const cacheKey = `progress_${userId;}_${mazeId}`;````;```;
    // 检查缓存/;,/g/;
if (this.config.enableCache && this.cache.has(cacheKey)) {const cached = this.cache.get(cacheKey);,}if (Date.now() - cached.timestamp < this.cacheTimeout) {}}
        return cached.data;}
      }
    }
    try {}}
      const response = await apiClient.get<UserProgressResponse>(;)}
        `${this.config.baseURL}/api/v1/mazes/${mazeId}/progress/${userId}`;```/`;`/g`/`;
      );
      // 缓存结果/;,/g/;
if (this.config.enableCache) {this.cache.set(cacheKey, {);,}data: response.data,);
}
          const timestamp = Date.now();}
        });
      }
      return response.data;';'';
    } catch (error) {';,}console.error('Failed to get user progress:', error);';'';
}
}
    }
  }
  /* 表 *//;/g/;
  *//;,/g/;
const async = listMazeTemplates();
mazeType?: MazeTheme;
difficulty?: MazeDifficulty;
page: number = 1,;
pageSize: number = 20;
  ): Promise<ListTemplatesResponse> {}}
    try {}
      const params: any = { page, page_size: pageSize ;};
if (mazeType) params.maze_type = mazeType;
if (difficulty) params.difficulty = difficulty;
const response = await apiClient.get<ListTemplatesResponse>(;);
        `${this.config.baseURL}/api/v1/templates`,{ params };```/`;`/g`/`;
      );
return response.data;';'';
    } catch (error) {';,}console.error('Failed to list maze templates:', error);';'';
}
}
    }
  }
  /* 成 *//;/g/;
  *//;,/g/;
const async = recordMazeCompletion();
userId: string,;
mazeId: string,;
stepsTaken: number,;
completionTime: number,;
const score = number;
  ): Promise<{ rewards: GameReward[]; achievements: string[] ;}> {try {}}
      const response = await apiClient.post(;)}
        `${this.config.baseURL}/api/v1/mazes/${mazeId}/complete`,{user_id: userId,steps_taken: stepsTaken,completion_time: completionTime,score: score;``}``/`;`/g`/`;
        };
      );
      // 清除相关缓存/;,/g/;
this.clearProgressCache(userId, mazeId);
return response.data;';'';
    } catch (error) {';,}console.error('Failed to record maze completion:', error);';'';
}
}
    }
  }
  /* 情 *//;/g/;
  *//;,/g/;
const async = getKnowledgeNode(nodeId: string): Promise<KnowledgeNode> {}
    const cacheKey = `knowledge_${nodeId;}`;````;```;
    // 检查缓存/;,/g/;
if (this.config.enableCache && this.cache.has(cacheKey)) {const cached = this.cache.get(cacheKey);,}if (Date.now() - cached.timestamp < this.cacheTimeout) {}}
        return cached.data;}
      }
    }
    try {}
      const response = await apiClient.get<{ node: KnowledgeNode ;}>(;);
        `${this.config.baseURL}/api/v1/knowledge/${nodeId}`;```/`;`/g`/`;
      );
      // 缓存结果/;,/g/;
if (this.config.enableCache) {this.cache.set(cacheKey, {);,}data: response.data.node,);
}
          const timestamp = Date.now();}
        });
      }
      return response.data.node;';'';
    } catch (error) {';,}console.error('Failed to get knowledge node:', error);';'';
}
}
    }
  }
  /* 情 *//;/g/;
  *//;,/g/;
const async = getChallenge(challengeId: string): Promise<Challenge> {}
    const cacheKey = `challenge_${challengeId;}`;````;```;
    // 检查缓存/;,/g/;
if (this.config.enableCache && this.cache.has(cacheKey)) {const cached = this.cache.get(cacheKey);,}if (Date.now() - cached.timestamp < this.cacheTimeout) {}}
        return cached.data;}
      }
    }
    try {}
      const response = await apiClient.get<{ challenge: Challenge ;}>(;);
        `${this.config.baseURL}/api/v1/challenges/${challengeId}`;```/`;`/g`/`;
      );
      // 缓存结果/;,/g/;
if (this.config.enableCache) {this.cache.set(cacheKey, {);,}data: response.data.challenge,);
}
          const timestamp = Date.now();}
        });
      }
      return response.data.challenge;';'';
    } catch (error) {';,}console.error('Failed to get challenge:', error);';'';
}
}
    }
  }
  /* 案 *//;/g/;
  *//;,/g/;
const async = submitChallengeAnswer();
challengeId: string,;
userId: string,;
const answers = string[];
  ): Promise<{ correct: boolean; score: number; explanation?: string }> {try {}}
      const response = await apiClient.post(;)}
        `${this.config.baseURL}/api/v1/challenges/${challengeId}/submit`,{user_id: userId,answers: answers;``}``/`;`/g`/`;
        };
      );
return response.data;';'';
    } catch (error) {';,}console.error('Failed to submit challenge answer:', error);';'';
}
}
    }
  }
  /* 息 *//;/g/;
  *//;,/g/;
const async = getUserStats(userId: string): Promise<MazeStats> {try {}}
      const response = await apiClient.get<MazeStats>(;)}
        `${this.config.baseURL}/api/v1/users/${userId}/stats`;```/`;`/g`/`;
      );
return response.data;';'';
    } catch (error) {';,}console.error('Failed to get user stats:', error);';'';
}
}
    }
  }
  /* 榜 *//;/g/;
  *//;,/g/;
const async = getLeaderboard();
mazeId?: string;
limit: number = 10;
  ): Promise<LeaderboardEntry[]> {}}
    try {}
      const params: any = { limit ;};
if (mazeId) params.maze_id = mazeId;
const response = await apiClient.get<{ entries: LeaderboardEntry[] ;}>(;);
        `${this.config.baseURL}/api/v1/leaderboard`,{ params };```/`;`/g`/`;
      );
return response.data.entries;';'';
    } catch (error) {';,}console.error('Failed to get leaderboard:', error);';'';
}
}
    }
  }
  /* 互 *//;/g/;
  *//;,/g/;
const async = mazeNpcInteraction();
playerId: string,;
action: string,;
const location = Position;
context?: any;
  ): Promise<MazeInteraction> {try {}}
      const response = await apiClient.post<MazeInteraction>(;)}
        `${this.config.baseURL}/api/v1/maze-interaction`,{player_id: playerId,action,location,context;``}``/`;`/g`/`;
        };
      );
return response.data;';'';
    } catch (error) {';,}console.error('Failed to interact with maze NPC:', error);';'';
      // 返回默认响应而不是抛出错误/;/g/;
}
}
      };
    }
  }
  /* 置 *//;/g/;
  *//;,/g/;
const async = getGameSettings(userId: string): Promise<GameSettings> {try {}}
      const response = await apiClient.get<GameSettings>(;)}
        `${this.config.baseURL}/api/v1/users/${userId}/settings`;```/`;`/g`/`;
      );
return response.data;';'';
    } catch (error) {';,}console.error('Failed to get game settings:', error);';'';
      // 返回默认设置'/;'/g'/;
}
      return {soundEnabled: true,musicEnabled: true,vibrationEnabled: true,autoSave: true,difficulty: MazeDifficulty.NORMAL,showHints: true,animationSpeed: 'normal',colorScheme: 'auto';'}'';'';
      };
    }
  }
  /* 置 *//;/g/;
  *//;,/g,/;
  async: updateGameSettings(userId: string, settings: Partial<GameSettings>): Promise<GameSettings> {try {}}
      const response = await apiClient.put<GameSettings>(;)}
        `${this.config.baseURL}/api/v1/users/${userId}/settings`,settings;```/`;`/g`/`;
      );
return response.data;';'';
    } catch (error) {';,}console.error('Failed to update game settings:', error);';'';
}
}
    }
  }
  /* 存 *//;/g/;
  *//;,/g/;
private clearMazeCache(mazeId: string): void {const keysToDelete: string[] = [];}}
    for (const key of this.cache.keys()) {}
      if (key.includes(`maze_${mazeId}`)) {`;}````;```;
};
keysToDelete.push(key);}
      }
    }
    keysToDelete.forEach(key => this.cache.delete(key));
  }
  /* 存 *//;/g/;
  *//;,/g/;
private clearProgressCache(userId: string, mazeId: string): void {}
    const progressKey = `progress_${userId;}_${mazeId}`;````;,```;
this.cache.delete(progressKey);
  }
  /* 存 *//;/g/;
  *//;,/g/;
clearCache(): void {}}
    this.cache.clear();}
  }
  /* 计 *//;/g/;
  *//;,/g/;
getCacheStats(): { size: number; keys: string[] ;} {}}
    return {size: this.cache.size,keys: Array.from(this.cache.keys());}
    };
  }
}
/* 例 *//;/g/;
*//;,/g/;
export const cornMazeService = new CornMazeService();
/* 例 *//;/g/;
*//;,/g/;
export const createCornMazeService = useCallback((config?: Partial<CornMazeServiceConfig>) => {return new CornMazeService(config);}
};';,'';
export default cornMazeService;