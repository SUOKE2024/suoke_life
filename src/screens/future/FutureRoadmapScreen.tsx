/* 划 *//;/g/;
 *//;,/g/;
import { Ionicons } from "@expo/vector-icons";""/;,"/g"/;
import { LinearGradient } from "expo-linear-gradient";";
import React, { useEffect, useState } from "react";";
import {Alert}Dimensions,;
ScrollView,;
StyleSheet,;
Text,;
TouchableOpacity,";"";
}
    View,'}'';'';
} from "react-native";"";"";
';'';
// 导入服务'/;,'/g'/;
import { MultiLanguageService } from "../../services/i18n/MultiLanguageService";""/;,"/g"/;
import { MobilePerformanceOptimizer } from "../../services/performance/MobilePerformanceOptimizer";""/;,"/g"/;
import { EnhancedSecurityService } from "../../services/security/EnhancedSecurityService";""/;,"/g"/;
import { TestCoverageService } from "../../tests/TestCoverageService";""/;"/g"/;
';,'';
const { width } = Dimensions.get('window');';'';

// 发展阶段'/;,'/g'/;
enum DevelopmentPhase {';,}SHORT_TERM = 'short_term',';,'';
MEDIUM_TERM = 'medium_term',';'';
}
}
  LONG_TERM = 'long_term',}'';'';
}

// 目标状态'/;,'/g'/;
enum GoalStatus {';,}PENDING = 'pending',';,'';
IN_PROGRESS = 'in_progress',';,'';
COMPLETED = 'completed',';'';
}
}
  BLOCKED = 'blocked',}'';'';
}

// 发展目标/;,/g/;
interface DevelopmentGoal {id: string}phase: DevelopmentPhase,;
title: string,;
description: string,;
status: GoalStatus,';,'';
progress: number,';,'';
priority: 'low' | 'medium' | 'high' | 'critical';','';
estimatedDuration: string,;
dependencies: string[],;
milestones: Milestone[],;
}
}
  const resources = Resource[];}
}

// 里程碑/;,/g/;
interface Milestone {id: string}title: string,;
description: string,;
targetDate: Date,;
const completed = boolean;
}
}
  completedDate?: Date;}
}

// 资源'/;,'/g'/;
interface Resource {';,}type: 'human' | 'technical' | 'financial';','';
name: string,;
amount: number,;
unit: string,;
}
}
  const allocated = boolean;}
}

// 执行状态/;,/g/;
interface ExecutionStatus {phase: DevelopmentPhase}activeGoals: number,;
completedGoals: number,;
overallProgress: number,;
estimatedCompletion: Date,;
}
}
  const blockers = string[];}
}

export const FutureRoadmapScreen: React.FC = () => {const [selectedPhase, setSelectedPhase] = useState<DevelopmentPhase>(DevelopmentPhase.SHORT_TERM);}  );
const [goals, setGoals] = useState<DevelopmentGoal[]>([]);
const [executionStatus, setExecutionStatus] = useState<ExecutionStatus[]>([]);
const [isExecuting, setIsExecuting] = useState(false);

  // 服务实例/;,/g/;
const [testCoverageService] = useState(() => new TestCoverageService());
const [performanceOptimizer] = useState(() => new MobilePerformanceOptimizer());
const [securityService] = useState(() => new EnhancedSecurityService());
const [i18nService] = useState(() => new MultiLanguageService());
useEffect(() => {initializeRoadmap();,}return () => {}}
        // 清理函数}/;/g/;
      };
    }, []);

  /* 图 *//;/g/;
   *//;,/g/;
const  initializeRoadmap = useCallback(() => {const  roadmapGoals: DevelopmentGoal[] = [;]// 短期目标 (1-3个月)'/;}      {';,}id: 'st-1';','';,'/g,'/;
  phase: DevelopmentPhase.SHORT_TERM,;
status: GoalStatus.IN_PROGRESS,';,'';
progress: 65,';,'';
priority: 'high';','';'';

];
dependencies: [],;
const milestones = [;]';'';
          {';,}id: 'st-1-m1';','';
targetDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),;
completed: true,;
}
            const completedDate = new Date();}
          },';'';
          {';,}id: 'st-1-m2';','';
targetDate: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000),;
}
            const completed = false;}
          }
];
        ],;
const resources = [;]];
        ],;
      ;},';'';
      {';,}id: 'st-2';','';
phase: DevelopmentPhase.SHORT_TERM,;
status: GoalStatus.IN_PROGRESS,';,'';
progress: 45,';,'';
priority: 'high';','';
dependencies: [],;
const milestones = [;]';'';
          {';,}id: 'st-2-m1';','';
targetDate: new Date(Date.now() + 20 * 24 * 60 * 60 * 1000),;
}
            const completed = false;}
          }
];
        ],;
const resources = [;]];
        ],;
      ;},';'';
      {';,}id: 'st-3';','';
phase: DevelopmentPhase.SHORT_TERM,;
status: GoalStatus.PENDING,';,'';
progress: 20,';,'';
priority: 'critical';','';'';
';,'';
dependencies: ['st-1'];','';
const milestones = [;]';'';
          {';,}id: 'st-3-m1';','';
targetDate: new Date(Date.now() + 35 * 24 * 60 * 60 * 1000),;
}
            const completed = false;}
          }
];
        ],;
const resources = [;]];
        ],;
      ;},';'';
      {';,}id: 'st-4';','';
phase: DevelopmentPhase.SHORT_TERM,;
status: GoalStatus.PENDING,';,'';
progress: 10,';,'';
priority: 'medium';','';
dependencies: [],;
const milestones = [;]';'';
          {';,}id: 'st-4-m1';','';
targetDate: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000),;
}
            const completed = false;}
          }
];
        ],;
const resources = [;]];
        ],;
      ;}

      // 中期目标 (3-6个月)'/;'/g'/;
      {';,}id: 'mt-1';','';
phase: DevelopmentPhase.MEDIUM_TERM,;
status: GoalStatus.PENDING,';,'';
progress: 0,';,'';
priority: 'high';','';'';
';,'';
dependencies: ['st-1', 'st-2'],';,'';
const milestones = [;]';'';
          {';,}id: 'mt-1-m1';','';
targetDate: new Date(Date.now() + 120 * 24 * 60 * 60 * 1000),;
}
            const completed = false;}
          }
];
        ],;
const resources = [;]];
        ],;
      ;},';'';
      {';,}id: 'mt-2';','';
phase: DevelopmentPhase.MEDIUM_TERM,;
status: GoalStatus.PENDING,';,'';
progress: 0,';,'';
priority: 'high';','';'';
';,'';
dependencies: ['st-3'];','';
const milestones = [;]';'';
          {';,}id: 'mt-2-m1';','';
targetDate: new Date(Date.now() + 150 * 24 * 60 * 60 * 1000),;
}
            const completed = false;}
          }
];
        ],;
const resources = [;]];
        ],;
      ;}

      // 长期目标 (6-12个月)'/;'/g'/;
      {';,}id: 'lt-1';','';
phase: DevelopmentPhase.LONG_TERM,;
status: GoalStatus.PENDING,';,'';
progress: 0,';,'';
priority: 'critical';','';'';
';,'';
dependencies: ['mt-1', 'mt-2'],';,'';
const milestones = [;]';'';
          {';,}id: 'lt-1-m1';','';
targetDate: new Date(Date.now() + 240 * 24 * 60 * 60 * 1000),;
}
            const completed = false;}
          }
];
        ],;
const resources = [;]];
        ],;
      ;},';'';
      {';,}id: 'lt-2';','';
phase: DevelopmentPhase.LONG_TERM,;
status: GoalStatus.PENDING,';,'';
progress: 0,';,'';
priority: 'medium';','';'';
';,'';
dependencies: ['st-4', 'mt-1'],';,'';
const milestones = [;]';'';
          {';,}id: 'lt-2-m1';','';
targetDate: new Date(Date.now() + 300 * 24 * 60 * 60 * 1000),;
}
            const completed = false;}
          }
];
        ],;
const resources = [;]];
        ],;
      ;}
    ];
setGoals(roadmapGoals);
updateExecutionStatus(roadmapGoals);
  };

  /* 态 *//;/g/;
   *//;,/g/;
const  updateExecutionStatus = useCallback((goals: DevelopmentGoal[]) => {const  phases = [;,]DevelopmentPhase.SHORT_TERM}DevelopmentPhase.MEDIUM_TERM,;
DevelopmentPhase.LONG_TERM,;
];
    ];
const  status = useMemo(() => phases.map((phase) => {const phaseGoals = goals.filter((goal) => goal.phase === phase);,}const  activeGoals = phaseGoals.filter();
        (goal) => goal.status === GoalStatus.IN_PROGRESS;
      ).length;
const  completedGoals = phaseGoals.filter();
        (goal) => goal.status === GoalStatus.COMPLETED;
      ).length;
const  overallProgress =;
phaseGoals.reduce((sum, goal) => sum + goal.progress, 0) //;,/g/;
phaseGoals.length;
const  blockers = phaseGoals;
        .filter((goal) => goal.status === GoalStatus.BLOCKED);
        .map((goal) => goal.title);
return {phase}activeGoals,;
completedGoals,;
overallProgress: overallProgress || 0,;
estimatedCompletion: new Date(Date.now() + 180 * 24 * 60 * 60 * 1000), []);
}
        blockers,}
      };
    });
setExecutionStatus(status);
  };

  /* 标 *//;/g/;
   *//;,/g/;
const  executeGoal = async (goalId: string) => {setIsExecuting(true);,}try {const goal = goals.find((g) => g.id === goalId);,}if (!goal) return;

      // 根据目标类型执行相应的服务'/;,'/g'/;
switch (goalId) {';,}case 'st-1': ';,'';
const await = executeTestCoverageGoal();';,'';
break;';,'';
case 'st-2': ';,'';
const await = executePerformanceGoal();';,'';
break;';,'';
case 'st-3': ';,'';
const await = executeSecurityGoal();';,'';
break;';,'';
case 'st-4': ';,'';
const await = executeI18nGoal();
break;
default: ;
}
          const await = simulateGoalExecution(goal);}
      }

      // 更新目标状态/;,/g/;
setGoals((prev) =>;
prev.map((g) =>;
g.id === goalId;
            ? {...g}status: GoalStatus.IN_PROGRESS,;
}
                progress: Math.min(g.progress + 20, 100),}
              ;}
            : g;
        );
      );

    } catch (error) {}}
}
    } finally {}}
      setIsExecuting(false);}
    }
  };

  /* 标 *//;/g/;
   *//;,/g/;
const  executeTestCoverageGoal = async () => {const report = await testCoverageService.generateCoverageReport();}}
}
  };

  /* 标 *//;/g/;
   *//;,/g/;
const  executePerformanceGoal = async () => {const metrics = await performanceOptimizer.collectMetrics();}}
}
  };

  /* 标 *//;/g/;
   *//;,/g/;
const  executeSecurityGoal = async () => {const status = securityService.getSecurityStatus();}}
}
  };

  /* 标 *//;/g/;
   *//;,/g/;
const  executeI18nGoal = async () => {const languages = i18nService.getAvailableLanguages();}}
}
  };

  /* 行 *//;/g/;
   *//;,/g/;
const  simulateGoalExecution = async (goal: DevelopmentGoal) => {// 模拟执行过程/;,}await: new Promise((resolve) => setTimeout(resolve, 1000));/g/;
}
}
  };

  /* 称 *//;/g/;
   *//;,/g/;
const  getPhaseTitle = (phase: DevelopmentPhase): string => {switch (phase) {}      const case = DevelopmentPhase.SHORT_TERM: ;
const case = DevelopmentPhase.MEDIUM_TERM: ;
const case = DevelopmentPhase.LONG_TERM: ;
}
}
    ;}
  };

  /* 色 *//;/g/;
   *//;,/g/;
const  getStatusColor = (status: GoalStatus): string => {switch (status) {';,}const case = GoalStatus.PENDING: ';,'';
return '#6B7280';';,'';
const case = GoalStatus.IN_PROGRESS: ';,'';
return '#3B82F6';';,'';
const case = GoalStatus.COMPLETED: ';,'';
return '#10B981';';,'';
const case = GoalStatus.BLOCKED: ';'';
}
        return '#EF4444';'}'';'';
    }
  };

  /* 本 *//;/g/;
   *//;,/g/;
const  getStatusText = (status: GoalStatus): string => {switch (status) {}      const case = GoalStatus.PENDING: ;
const case = GoalStatus.IN_PROGRESS: ;
const case = GoalStatus.COMPLETED: ;
const case = GoalStatus.BLOCKED: ;
}
}
    ;}
  };

  /* 色 *//;/g/;
   *//;,/g/;
const  getPriorityColor = (priority: string): string => {';,}switch (priority) {';,}case 'low': ';,'';
return '#10B981';';,'';
case 'medium': ';,'';
return '#F59E0B';';,'';
case 'high': ';,'';
return '#EF4444';';,'';
case 'critical': ';,'';
return '#7C2D12';';,'';
const default = ';'';
}
        return '#6B7280';'}'';'';
    }
  };
const filteredGoals = goals.filter((goal) => goal.phase === selectedPhase);
const  currentStatus = executionStatus.find();
    (status) => status.phase === selectedPhase;
  );';'';
';,'';
return (<LinearGradient colors={['#667eea', '#764ba2']} style={styles.container}>';)      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>;'';
        {/* 标题区域 */}/;/g/;
        <View style={styles.header}>;
          <Text style={styles.title}>索克生活 - 未来发展路线图</Text>/;/g/;
          <Text style={styles.subtitle}>;

          </Text>/;/g/;
        </View>/;/g/;

        {/* 阶段选择器 */}/;/g/;
        <View style={styles.phaseSelector}>;
          {[;,]DevelopmentPhase.SHORT_TERM,);,}DevelopmentPhase.MEDIUM_TERM,);
DevelopmentPhase.LONG_TERM,);
}
];
          ].map((phase) => (<TouchableOpacity,}  />/;,)key={phase}/g/;
              style={[;,]styles.phaseButton,);}}
                selectedPhase === phase && styles.selectedPhaseButton,)}
];
              ]});
onPress={() => setSelectedPhase(phase)}
            >;
              <Text,  />/;,/g/;
style={[;,]styles.phaseButtonText,;}}
                  selectedPhase === phase && styles.selectedPhaseButtonText,}
];
                ]}
              >;
                {getPhaseTitle(phase)}
              </Text>/;/g/;
            </TouchableOpacity>/;/g/;
          ))}
        </View>/;/g/;

        {/* 执行状态概览 */}/;/g/;
        {currentStatus && (<View style={styles.statusCard}>;)            <Text style={styles.statusTitle}>执行状态概览</Text>/;/g/;
            <View style={styles.statusGrid}>;
              <View style={styles.statusItem}>;
                <Text style={styles.statusValue}>{currentStatus.activeGoals}</Text>/;/g/;
                <Text style={styles.statusLabel}>进行中</Text>/;/g/;
              </View>/;/g/;
              <View style={styles.statusItem}>;
                <Text style={styles.statusValue}>{currentStatus.completedGoals}</Text>/;/g/;
                <Text style={styles.statusLabel}>已完成</Text>/;/g/;
              </View>)/;/g/;
              <View style={styles.statusItem}>);
                <Text style={styles.statusValue}>);
                  {currentStatus.overallProgress.toFixed(1)}%;
                </Text>/;/g/;
                <Text style={styles.statusLabel}>总进度</Text>/;/g/;
              </View>/;/g/;
              <View style={styles.statusItem}>;
                <Text style={styles.statusValue}>{currentStatus.blockers.length}</Text>/;/g/;
                <Text style={styles.statusLabel}>阻塞项</Text>/;/g/;
              </View>/;/g/;
            </View>/;/g/;
          </View>/;/g/;
        )}

        {/* 目标列表 */}/;/g/;
        <View style={styles.goalsContainer}>;
          {filteredGoals.map((goal) => (<View key={goal.id} style={styles.goalCard}>;)              <View style={styles.goalHeader}>;
                <View style={styles.goalTitleContainer}>;
                  <Text style={styles.goalTitle}>{goal.title}</Text>/;/g/;
                  <View,)  />/;,/g/;
style={[;]);}}
                      styles.priorityBadge,)}
                      { backgroundColor: getPriorityColor(goal.priority) ;}
];
                    ]}
                  >;
                    <Text style={styles.priorityText}>;
                      {goal.priority.toUpperCase()}
                    </Text>/;/g/;
                  </View>/;/g/;
                </View>/;/g/;
                <View,  />/;,/g/;
style={}[;]}
                    styles.statusBadge,}
                    { backgroundColor: getStatusColor(goal.status) ;}
];
                  ]}
                >;
                  <Text style={styles.statusBadgeText}>;
                    {getStatusText(goal.status)}
                  </Text>/;/g/;
                </View>/;/g/;
              </View>/;/g/;

              <Text style={styles.goalDescription}>{goal.description}</Text>/;/g/;

              {/* 进度条 */}/;/g/;
              <View style={styles.progressContainer}>;
                <View style={styles.progressBar}>;
                  <View,  />/;,/g/;
style={}[;]}
                      styles.progressFill,}
                      { width: `${goal.progress;}%` },````;```;
];
                    ]}
                  />/;/g/;
                </View>/;/g/;
                <Text style={styles.progressText}>{goal.progress}%</Text>/;/g/;
              </View>/;/g/;

              {/* 里程碑 */}/;/g/;
              <View style={styles.milestonesContainer}>;
                <Text style={styles.milestonesTitle}>关键里程碑</Text>/;/g/;
                {goal.milestones.map((milestone) => (<View key={milestone.id} style={styles.milestoneItem}>';)                    <Ionicons,'  />/;,'/g'/;
name={milestone.completed ? 'checkmark-circle' : 'ellipse-outline'}';,'';
size={16}';,'';
color={milestone.completed ? '#10B981' : '#6B7280'}';'';
                    />)/;/g/;
                    <Text style={styles.milestoneText}>{milestone.title}</Text>)/;/g/;
                  </View>)/;/g/;
                ))}
              </View>/;/g/;

              {/* 资源需求 */}/;/g/;
              <View style={styles.resourcesContainer}>;
                <Text style={styles.resourcesTitle}>资源需求</Text>/;/g/;
                {goal.resources.map((resource, index) => (<View key={index} style={styles.resourceItem}>;)                    <Text style={styles.resourceText}>;
                      {resource.name}: {resource.amount} {resource.unit}
                    </Text>/;/g/;
                    <View,  />/;,/g/;
style={[;,]styles.allocationBadge,';}                        {';}}'';
                          const backgroundColor = resource.allocated ? '#10B981' : '#EF4444';'}'';'';
                        }
];
                      ]}
                    >;
                      <Text style={styles.allocationText}>;

                      </Text>)/;/g/;
                    </View>)/;/g/;
                  </View>)/;/g/;
                ))}
              </View>/;/g/;

              {/* 执行按钮 */}/;/g/;
              <TouchableOpacity,  />/;,/g/;
style={[;,]styles.executeButton,;}}
                  goal.status === GoalStatus.COMPLETED && styles.disabledButton,}
];
                ]}
                onPress={() => executeGoal(goal.id)}
                disabled={isExecuting || goal.status === GoalStatus.COMPLETED}
              >;
                <Text style={styles.executeButtonText}>;
                  {goal.status === GoalStatus.COMPLETED;}                    : isExecuting;

                </Text>/;/g/;
              </TouchableOpacity>/;/g/;
}
            </View>}/;/g/;
          ))}
        </View>/;/g/;
      </ScrollView>/;/g/;
    </LinearGradient>/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,;}}
    const flex = 1;}
  }
scrollView: {flex: 1,;
}
    const paddingHorizontal = 20;}
  },';,'';
header: {,';,}alignItems: 'center';','';'';
}
    const paddingVertical = 30;}
  }
title: {,';,}fontSize: 24,';,'';
fontWeight: 'bold';','';
color: '#FFFFFF';','';
textAlign: 'center';','';'';
}
    const marginBottom = 8;}
  }
subtitle: {,';,}fontSize: 14,';,'';
color: '#E5E7EB';','';'';
}
    const textAlign = 'center';'}'';'';
  },';,'';
phaseSelector: {,')'';,}flexDirection: 'row';',)'';
marginBottom: 20,)';,'';
backgroundColor: 'rgba(255, 255, 255, 0.1)',';,'';
borderRadius: 12,;
}
    const padding = 4;}
  }
phaseButton: {flex: 1,;
paddingVertical: 12,;
paddingHorizontal: 8,';,'';
borderRadius: 8,';'';
}
    const alignItems = 'center';'}'';'';
  },';,'';
selectedPhaseButton: {,';}}'';
    backgroundColor: 'rgba(255, 255, 255, 0.2)','}'';'';
  ;}
phaseButtonText: {,';,}fontSize: 12,';,'';
color: '#E5E7EB';','';'';
}
    const textAlign = 'center';'}'';'';
  },';,'';
selectedPhaseButtonText: {,';,}color: '#FFFFFF';','';'';
}
    const fontWeight = '600';'}'';'';
  },';,'';
statusCard: {,';,}backgroundColor: 'rgba(255, 255, 255, 0.1)',';,'';
borderRadius: 16,;
padding: 20,;
}
    const marginBottom = 20;}
  }
statusTitle: {,';,}fontSize: 18,';,'';
fontWeight: '600';','';
color: '#FFFFFF';','';'';
}
    const marginBottom = 16;}
  },';,'';
statusGrid: {,';,}flexDirection: 'row';','';'';
}
    const justifyContent = 'space-between';'}'';'';
  },';,'';
statusItem: {,';}}'';
    const alignItems = 'center';'}'';'';
  }
statusValue: {,';,}fontSize: 24,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#FFFFFF';'}'';'';
  }
statusLabel: {,';,}fontSize: 12,';,'';
color: '#E5E7EB';','';'';
}
    const marginTop = 4;}
  }
goalsContainer: {,;}}
    const marginBottom = 20;}
  },';,'';
goalCard: {,';,}backgroundColor: 'rgba(255, 255, 255, 0.95)',';,'';
borderRadius: 16,;
padding: 20,';,'';
marginBottom: 16,';'';
}
    shadowColor: '#000';',}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
shadowRadius: 4,;
const elevation = 3;
  },';,'';
goalHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'flex-start';','';'';
}
    const marginBottom = 12;}
  }
goalTitleContainer: {flex: 1,;
}
    const marginRight = 12;}
  }
goalTitle: {,';,}fontSize: 18,';,'';
fontWeight: '600';','';
color: '#1F2937';','';'';
}
    const marginBottom = 8;}
  }
priorityBadge: {paddingHorizontal: 8,;
paddingVertical: 4,';,'';
borderRadius: 12,';'';
}
    const alignSelf = 'flex-start';'}'';'';
  }
priorityText: {,';,}fontSize: 10,';,'';
fontWeight: '600';','';'';
}
    const color = '#FFFFFF';'}'';'';
  }
statusBadge: {paddingHorizontal: 12,;
paddingVertical: 6,;
}
    const borderRadius = 16;}
  }
statusBadgeText: {,';,}fontSize: 12,';,'';
fontWeight: '600';','';'';
}
    const color = '#FFFFFF';'}'';'';
  }
goalDescription: {,';,}fontSize: 14,';,'';
color: '#6B7280';','';
lineHeight: 20,;
}
    const marginBottom = 16;}
  },';,'';
progressContainer: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const marginBottom = 16;}
  }
progressBar: {flex: 1,';,'';
height: 8,';,'';
backgroundColor: '#E5E7EB';','';
borderRadius: 4,;
}
    const marginRight = 12;}
  },';,'';
progressFill: {,';,}height: '100%';','';
backgroundColor: '#3B82F6';','';'';
}
    const borderRadius = 4;}
  }
progressText: {,';,}fontSize: 12,';,'';
fontWeight: '600';','';
color: '#6B7280';','';'';
}
    const minWidth = 40;}
  }
milestonesContainer: {,;}}
    const marginBottom = 16;}
  }
milestonesTitle: {,';,}fontSize: 14,';,'';
fontWeight: '600';','';
color: '#1F2937';','';'';
}
    const marginBottom = 8;}
  },';,'';
milestoneItem: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const marginBottom = 4;}
  }
milestoneText: {,';,}fontSize: 12,';,'';
color: '#6B7280';','';'';
}
    const marginLeft = 8;}
  }
resourcesContainer: {,;}}
    const marginBottom = 16;}
  }
resourcesTitle: {,';,}fontSize: 14,';,'';
fontWeight: '600';','';
color: '#1F2937';','';'';
}
    const marginBottom = 8;}
  },';,'';
resourceItem: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';'';
}
    const marginBottom = 4;}
  }
resourceText: {,';,}fontSize: 12,';,'';
color: '#6B7280';','';'';
}
    const flex = 1;}
  }
allocationBadge: {paddingHorizontal: 8,;
paddingVertical: 2,;
}
    const borderRadius = 8;}
  }
allocationText: {,';,}fontSize: 10,';,'';
fontWeight: '600';','';'';
}
    const color = '#FFFFFF';'}'';'';
  },';,'';
executeButton: {,';,}backgroundColor: '#3B82F6';','';
paddingVertical: 12,';,'';
borderRadius: 8,';'';
}
    const alignItems = 'center';'}'';'';
  },';,'';
disabledButton: {,';}}'';
    const backgroundColor = '#9CA3AF';'}'';'';
  }
executeButtonText: {,';,}fontSize: 14,';,'';
fontWeight: '600';','';'';
}
    const color = '#FFFFFF';'}'';'';
  }
});';'';
''';