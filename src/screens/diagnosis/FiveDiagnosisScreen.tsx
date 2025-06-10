import React, { useState, useEffect, useCallback, useRef } from "react";";
import { SafeAreaView } from "react-native-safe-area-context";";
import { useNavigation, useFocusEffect } from "@react-navigation/native";""/;,"/g"/;
import { usePerformanceMonitor } from "../../hooks/usePerformanceMonitor";""/;,"/g"/;
import {;,}View,;
Text,;
StyleSheet,;
ScrollView,;
TouchableOpacity,;
Alert,;
ActivityIndicator,;
Dimensions,;
Animated,";"";
}
  Platform;'}'';'';
} from "react-native";";
import {;,}fiveDiagnosisService,;
FiveDiagnosisInput,;
FiveDiagnosisResult,';'';
}
  FiveDiagnosisError;'}'';'';
} from "../../services/fiveDiagnosisService";""/;"/g"/;
// 诊断步骤枚举'/;,'/g'/;
enum DiagnosisStep {';,}PREPARATION = 'preparation',';,'';
LOOKING = 'looking',';,'';
LISTENING = 'listening',';,'';
INQUIRY = 'inquiry',';,'';
PALPATION = 'palpation',';,'';
CALCULATION = 'calculation',';,'';
ANALYSIS = 'analysis',';'';
}
}
  RESULTS = 'results'}'';'';
}
// 诊断状态接口/;,/g/;
interface DiagnosisState {currentStep: DiagnosisStep}completedSteps: Set<DiagnosisStep>,;
isProcessing: boolean,;
const progress = number;
error?: string;
sessionId?: string;
const collectedData = Partial<FiveDiagnosisInput>;
}
}
  result?: FiveDiagnosisResult;}
}
// 步骤配置/;,/g/;
const  STEP_CONFIG = {[DiagnosisStep.PREPARATION]: {}';'';
';,'';
const icon = '🔧';';'';
}
}
  }
  [DiagnosisStep.LOOKING]: {';}';,'';
const icon = '👁️';';'';
}
}
  }
  [DiagnosisStep.LISTENING]: {';}';,'';
const icon = '👂';';'';
}
}
  }
  [DiagnosisStep.INQUIRY]: {';}';,'';
const icon = '💬';';'';
}
}
  }
  [DiagnosisStep.PALPATION]: {';}';,'';
const icon = '🤚';';'';
}
}
  }
  [DiagnosisStep.CALCULATION]: {';}';,'';
const icon = '🧮';';'';
}
}
  }
  [DiagnosisStep.ANALYSIS]: {';}';,'';
const icon = '🧠';';'';
}
}
  }
  [DiagnosisStep.RESULTS]: {';}';,'';
const icon = '📊';';'';
}
}
  }';'';
};';,'';
const { width: screenWidth, height: screenHeight ;} = Dimensions.get('window');';,'';
export default React.memo(function FiveDiagnosisScreen() {;};
const navigation = useNavigation();
const [diagnosisState, setDiagnosisState] = useState<DiagnosisState>({);,}currentStep: DiagnosisStep.PREPARATION,);
completedSteps: new Set(),;
isProcessing: false,;
progress: 0,';,'';
collectedData: {,';}}'';
}
  const userId = 'current_user' // 应该从用户上下文获取'}''/;'/g'/;
    ;}
  });
  // 动画值/;,/g/;
const progressAnimation = useRef(new Animated.Value(0)).current;
const fadeAnimation = useRef(new Animated.Value(1)).current;
const scaleAnimation = useRef(new Animated.Value(1)).current;';'';
  // 性能监控'/;,'/g,'/;
  const: performanceMonitor = usePerformanceMonitor('FiveDiagnosisScreen', {)';,}trackRender: true,);,'';
trackMemory: true,);
}
    const warnThreshold = 100;)}
  });
  // 初始化服务/;,/g/;
useEffect() => {}}
    initializeDiagnosisService();}
  }, [])  // 检查是否需要添加依赖项;/;/g/;
  // 监听焦点变化/;,/g/;
useFocusEffect();
useCallback() => {// 页面获得焦点时的逻辑/;,}return () => {}}/g/;
        // 页面失去焦点时的清理逻辑}/;/g/;
      };
    }, []);
  );
  // 监听进度变化，更新动画/;,/g/;
useEffect() => {Animated.timing(progressAnimation, {)      toValue: diagnosisState.progress,);,}duration: 500,);
}
      const useNativeDriver = false;)}
    }).start();
  }, [diagnosisState.progress]);
  // 初始化诊断服务/;,/g/;
const  initializeDiagnosisService = async () => {}}
    try {}
      setDiagnosisState(prev => ({ ...prev, isProcessing: true ;}));
const await = fiveDiagnosisService.initialize();
setDiagnosisState(prev => ({));}        ...prev,);
isProcessing: false,);
}
        const sessionId = generateSessionId()}
      ;}));
    } catch (error) {setDiagnosisState(prev => ({)        ...prev,);,}const isProcessing = false;);
}
)}
      }));
    }
  };
  // 开始诊断流程/;,/g/;
const  startDiagnosis = useCallback() => {setDiagnosisState(prev => ({)      ...prev,);,}currentStep: DiagnosisStep.LOOKING,);
}
      const progress = 12.5 // 1/8 的进度)}/;/g/;
    ;}));
  }, []);
  // 完成当前步骤/;,/g/;
const  completeCurrentStep = useCallback(async (stepData: any) => {}
    const { currentStep ;} = diagnosisState;
try {}
      setDiagnosisState(prev => ({ ...prev, isProcessing: true ;}));
      // 更新收集的数据/;,/g/;
const updatedData = { ...diagnosisState.collectedData };
switch (currentStep) {const case = DiagnosisStep.LOOKING: ;,}updatedData.lookingData = stepData;
break;
const case = DiagnosisStep.LISTENING: ;
updatedData.listeningData = stepData;
break;
const case = DiagnosisStep.INQUIRY: ;
updatedData.inquiryData = stepData;
break;
const case = DiagnosisStep.PALPATION: ;
updatedData.palpationData = stepData;
break;
const case = DiagnosisStep.CALCULATION: ;
updatedData.calculationData = stepData;
}
          break;}
      }
      // 更新状态/;,/g/;
const completedSteps = new Set(diagnosisState.completedSteps);
completedSteps.add(currentStep);
const nextStep = getNextStep(currentStep);
const progress = calculateProgress(completedSteps);
setDiagnosisState(prev => ({)...prev}const currentStep = nextStep;
completedSteps,;
progress,);
collectedData: updatedData,);
}
        const isProcessing = false;)}
      }));
      // 如果所有数据收集完成，开始分析/;,/g/;
if (nextStep === DiagnosisStep.ANALYSIS) {}}
        const await = performComprehensiveAnalysis(updatedData as FiveDiagnosisInput);}
      }
    } catch (error) {setDiagnosisState(prev => ({)        ...prev,);,}const isProcessing = false;);
}
)}
      }));
    }
  }, [diagnosisState]);
  // 执行综合分析/;,/g/;
const  performComprehensiveAnalysis = async (input: FiveDiagnosisInput) => {try {}      setDiagnosisState(prev => ({)        ...prev}isProcessing: true,);
currentStep: DiagnosisStep.ANALYSIS,);
}
        const progress = 87.5 // 7/8 的进度)}/;/g/;
      ;}));
const result = await fiveDiagnosisService.performComprehensiveDiagnosis(input);
setDiagnosisState(prev => ({)...prev}currentStep: DiagnosisStep.RESULTS,;
const progress = 100;);
result,);
}
        const isProcessing = false;)}
      }));
      // 显示完成提示/;/g/;

        [;]{}}
}
];
onPress: () => {;} }];
      );
    } catch (error) {setDiagnosisState(prev => ({)        ...prev,);,}const isProcessing = false;);
}
)}
      }));
    }
  };
  // 获取下一步骤/;,/g/;
const  getNextStep = (currentStep: DiagnosisStep): DiagnosisStep => {const steps = Object.values(DiagnosisStep);,}const currentIndex = steps.indexOf(currentStep);
}
    return steps[currentIndex + 1] || DiagnosisStep.RESULTS;}
  };
  // 计算进度/;,/g/;
const  calculateProgress = (completedSteps: Set<DiagnosisStep>): number => {const totalSteps = Object.values(DiagnosisStep).length - 1; // 排除准备阶段/;}}/g/;
    return (completedSteps.size / totalSteps) * 100;}/;/g/;
  };
  // 生成会话ID;/;,/g/;
const  generateSessionId = (): string => {}
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;````;```;
  };
  // 渲染步骤指示器/;,/g/;
const  renderStepIndicator = () => {}}
    const steps = Object.values(DiagnosisStep);}
        return (<View style={styles.stepIndicator}>);
        {steps.map(step, index) => {}          const isCompleted = diagnosisState.completedSteps.has(step);
const isCurrent = diagnosisState.currentStep === step;
}
          const config = STEP_CONFIG[step];}
                    return (<View key={step} style={styles.stepItem}>;)              <View style={ />/;}[;,]styles.stepCircle,;,/g/;
isCompleted && styles.stepCompleted,;
}
                isCurrent && styles.stepCurrent;}
];
              ]}}>);
                <Text style={ />/;}[;]);,/g/;
styles.stepIcon,);
}
                  (isCompleted || isCurrent) && styles.stepIconActive;}
];
                ]}}>;
                  {config.icon}
                </Text>/;/g/;
              </View>/;/g/;
              <Text style={ />/;}[;,]styles.stepTitle,;/g/;
}
                (isCompleted || isCurrent) && styles.stepTitleActive;}
];
              ]}}>;
                {config.title}
              </Text>/;/g/;
              {index < steps.length - 1  && <View style={[ />/;,]styles.stepConnector,;}}/g/;
                  isCompleted && styles.stepConnectorCompleted;}
];
                ]}} />/;/g/;
              )}
            </View>/;/g/;
          );
        })}
      </View>/;/g/;
    );
  };
  // 渲染进度条/;,/g/;
const  renderProgressBar = () => (<View style={styles.progressContainer}>;)      <View style={styles.progressBar}>;
        <Animated.View;  />/;,/g/;
style={[;]);,}styles.progressFill,);
            {);,}width: progressAnimation.interpolate({),';}];,'';
inputRange: [0, 100],';,'';
outputRange: ["0%",100%'],'';'';
}
                const extrapolate = 'clamp'}'';'';
              ;}});
            }
          ]}
        />/;/g/;
      </View>/;/g/;
      <Text style={styles.progressText}>;

      </Text>/;/g/;
    </View>/;/g/;
  );
  // 渲染当前步骤内容/;,/g/;
const  renderCurrentStepContent = () => {}
    const { currentStep } = diagnosisState;
const config = STEP_CONFIG[currentStep];
switch (currentStep) {}}
      const case = DiagnosisStep.PREPARATION:}
        return (<View style={styles.stepContent;}>;)            <Text style={styles.stepDescription}>{config.description}</Text>/;/g/;
            <Text style={styles.estimatedTime}>预计用时：{config.estimatedTime}</Text>/;/g/;
            <TouchableOpacity;  />/;,/g/;
style={styles.startButton}
              onPress={startDiagnosis}
              disabled={diagnosisState.isProcessing}
            >;
              <Text style={styles.startButtonText}>开始五诊检测</Text>)/;/g/;
            </TouchableOpacity>)/;/g/;
          </View>)/;/g/;
        );
const case = DiagnosisStep.LOOKING: ;
return (<View style={styles.stepContent;}>;)            <Text style={styles.stepDescription}>{config.description}</Text>/;/g/;
            <Text style={styles.estimatedTime}>预计用时：{config.estimatedTime}</Text>)/;/g/;
            <TouchableOpacity;)  />/;,/g/;
style={styles.actionButton});
onPress={() => completeCurrentStep(generateMockStepData(currentStep))}
              disabled={diagnosisState.isProcessing}
            >;
              <Text style={styles.actionButtonText}>开始拍照</Text>/;/g/;
            </TouchableOpacity>/;/g/;
          </View>/;/g/;
        );
const case = DiagnosisStep.LISTENING: ;
return (<View style={styles.stepContent;}>;)            <Text style={styles.stepDescription}>{config.description}</Text>/;/g/;
            <Text style={styles.estimatedTime}>预计用时：{config.estimatedTime}</Text>)/;/g/;
            <TouchableOpacity;)  />/;,/g/;
style={styles.actionButton});
onPress={() => completeCurrentStep(generateMockStepData(currentStep))}
              disabled={diagnosisState.isProcessing}
            >;
              <Text style={styles.actionButtonText}>开始录音</Text>/;/g/;
            </TouchableOpacity>/;/g/;
          </View>/;/g/;
        );
const case = DiagnosisStep.INQUIRY: ;
return (<View style={styles.stepContent;}>;)            <Text style={styles.stepDescription}>{config.description}</Text>/;/g/;
            <Text style={styles.estimatedTime}>预计用时：{config.estimatedTime}</Text>)/;/g/;
            <TouchableOpacity;)  />/;,/g/;
style={styles.actionButton});
onPress={() => completeCurrentStep(generateMockStepData(currentStep))}
              disabled={diagnosisState.isProcessing}
            >;
              <Text style={styles.actionButtonText}>开始问诊</Text>/;/g/;
            </TouchableOpacity>/;/g/;
          </View>/;/g/;
        );
const case = DiagnosisStep.PALPATION: ;
return (<View style={styles.stepContent;}>;)            <Text style={styles.stepDescription}>{config.description}</Text>/;/g/;
            <Text style={styles.estimatedTime}>预计用时：{config.estimatedTime}</Text>)/;/g/;
            <TouchableOpacity;)  />/;,/g/;
style={styles.actionButton});
onPress={() => completeCurrentStep(generateMockStepData(currentStep))}
              disabled={diagnosisState.isProcessing}
            >;
              <Text style={styles.actionButtonText}>开始切诊</Text>/;/g/;
            </TouchableOpacity>/;/g/;
          </View>/;/g/;
        );
const case = DiagnosisStep.CALCULATION: ;
return (<View style={styles.stepContent;}>;)            <Text style={styles.stepDescription}>{config.description}</Text>/;/g/;
            <Text style={styles.estimatedTime}>预计用时：{config.estimatedTime}</Text>/;/g/;
            <View style={styles.calculationOptions}>;
              <Text style={styles.calculationTitle}>选择算诊分析类型：</Text>/;/g/;
              <TouchableOpacity style={styles.calculationOption}>;
                <Text style={styles.calculationOptionText}>🕐 子午流注分析</Text>/;/g/;
              </TouchableOpacity>/;/g/;
              <TouchableOpacity style={styles.calculationOption}>;
                <Text style={styles.calculationOptionText}>🎭 八字体质分析</Text>/;/g/;
              </TouchableOpacity>/;/g/;
              <TouchableOpacity style={styles.calculationOption}>;
                <Text style={styles.calculationOptionText}>☯️ 八卦配属分析</Text>/;/g/;
              </TouchableOpacity>/;/g/;
              <TouchableOpacity style={styles.calculationOption}>;
                <Text style={styles.calculationOptionText}>🌊 五运六气分析</Text>/;/g/;
              </TouchableOpacity>/;/g/;
            </View>)/;/g/;
            <TouchableOpacity;)  />/;,/g/;
style={styles.actionButton});
onPress={() => completeCurrentStep(generateMockStepData(currentStep))}
              disabled={diagnosisState.isProcessing}
            >;
              <Text style={styles.actionButtonText}>开始算诊</Text>/;/g/;
            </TouchableOpacity>/;/g/;
          </View>/;/g/;
        );
const case = DiagnosisStep.ANALYSIS: ';,'';
return (<View style={styles.stepContent;}>';)            <ActivityIndicator size="large" color="#007AFF"  />"/;"/g"/;
            <Text style={styles.stepDescription}>{config.description}</Text>)/;/g/;
            <Text style={styles.estimatedTime}>预计用时：{config.estimatedTime}</Text>)/;/g/;
          </View>)/;/g/;
        );
const case = DiagnosisStep.RESULTS: ;
return (<View style={styles.stepContent;}>;)            <Text style={styles.stepDescription}>{config.description}</Text>/;/g/;
            {diagnosisState.result  && <View style={styles.resultsContainer}>;
                <Text style={styles.resultsTitle}>五诊分析结果</Text>/;/g/;
                <Text style={styles.resultsText}>;

                </Text>/;/g/;
                <Text style={styles.resultsText}>;

                </Text>/;/g/;
                <Text style={styles.resultsText}>;

                </Text>/;/g/;
                <Text style={styles.resultsText}>;
);
                </Text>)/;/g/;
              </View>)/;/g/;
            )}
            <TouchableOpacity;  />/;,/g/;
style={styles.actionButton}
              onPress={() => navigation.goBack()}
            >;
              <Text style={styles.actionButtonText}>查看详细报告</Text>/;/g/;
            </TouchableOpacity>/;/g/;
          </View>/;/g/;
        );
default: ;
return null;
    }
  };
  // 生成模拟步骤数据/;,/g/;
const  generateMockStepData = (step: DiagnosisStep) => {switch (step) {}      const case = DiagnosisStep.LOOKING: ";,"";
return {,";,}faceImage: 'mock_face_image_data';','';'';
}
          tongueImage: 'mock_tongue_image_data';',}'';
const metadata = { timestamp: Date.now() ;}
        };
const case = DiagnosisStep.LISTENING: ';,'';
return {,';,}voiceRecording: 'mock_voice_data';','';'';
}
          breathingSound: 'mock_breathing_data';',}'';
metadata: { timestamp: Date.now(), duration: 30 ;}
        };
const case = DiagnosisStep.INQUIRY: ;
return {lifestyle: {,;}}
}
          ;}
        };
const case = DiagnosisStep.PALPATION: ;
return {pulseData: {const rate = 72;

}
}
          }
        };
const case = DiagnosisStep.CALCULATION: ;
return {personalInfo: {birthYear: 1990,;
birthMonth: 5,;
birthDay: 15,;
const birthHour = 10;

}
}
          }
analysisTypes: {ziwuLiuzhu: true,;
constitution: true,;
bagua: true,;
wuyunLiuqi: true,;
}
            const comprehensive = true;}
          }
const currentTime = new Date().toISOString();

        };
const default = return {;};
    }
  };
return (<SafeAreaView style={styles.container}>;)      <View style={styles.header}>);
        <TouchableOpacity;)  />/;,/g/;
style={styles.backButton});
onPress={() => navigation.goBack()}
        >;
          <Text style={styles.backButtonText}>←</Text>/;/g/;
        </TouchableOpacity>/;/g/;
        <Text style={styles.headerTitle}>五诊检测</Text>/;/g/;
        <TouchableOpacity;  />/;,/g/;
style={styles.restartButton}
          onPress={() => {}            setDiagnosisState({);,}currentStep: DiagnosisStep.PREPARATION,);
completedSteps: new Set(),;
isProcessing: false,';'';
}
              progress: 0,'}'';
collectedData: { userId: 'current_user' ;},';,'';
const sessionId = generateSessionId();
            ;});
          }}
        >;
          <Text style={styles.restartButtonText}>重新开始</Text>/;/g/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;
      {renderProgressBar()}
      <ScrollView;  />/;,/g/;
style={styles.content}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.contentContainer}
      >;
        {renderStepIndicator()}
        {renderCurrentStepContent()}
      </ScrollView>/;/g/;
    </SafeAreaView>/;/g/;
  );
}
const  styles = StyleSheet.create({)container: {,';,}flex: 1,';'';
}
    const backgroundColor = '#f8f9fa'}'';'';
  ;},';,'';
header: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'space-between';','';
paddingHorizontal: 20,';,'';
paddingVertical: 15,';,'';
backgroundColor: '#ffffff';','';
borderBottomWidth: 1,';'';
}
    const borderBottomColor = '#e9ecef'}'';'';
  ;}
backButton: {,;}}
  const padding = 8;}
  }
backButtonText: {,';,}fontSize: 24,';'';
}
    const color = '#007AFF'}'';'';
  ;}
headerTitle: {,';,}fontSize: 18,';,'';
fontWeight: '600';','';'';
}
    const color = '#1a1a1a'}'';'';
  ;}
restartButton: {,;}}
  const padding = 8;}
  }
restartButtonText: {,';,}fontSize: 14,';'';
}
    const color = '#007AFF'}'';'';
  ;}
progressContainer: {paddingHorizontal: 20,';,'';
paddingVertical: 15,';'';
}
    const backgroundColor = '#ffffff'}'';'';
  ;}
progressBar: {,';,}height: 8,';,'';
backgroundColor: '#e9ecef';','';
borderRadius: 4,';'';
}
    const overflow = 'hidden'}'';'';
  ;},';,'';
progressFill: {,';,}height: '100%';','';
backgroundColor: '#007AFF';','';'';
}
    const borderRadius = 4;}
  }
progressText: {,';,}fontSize: 12,';,'';
color: '#6c757d';','';
textAlign: 'center';','';'';
}
    const marginTop = 8;}
  }
content: {,;}}
  const flex = 1;}
  }
contentContainer: {,;}}
  const padding = 20;}
  },';,'';
stepIndicator: {,';,}flexDirection: 'row';','';
flexWrap: 'wrap';','';
justifyContent: 'space-between';','';'';
}
    const marginBottom = 30;}
  },';,'';
stepItem: {,';,}alignItems: 'center';','';
width: screenWidth / 4 - 20,'/;,'/g,'/;
  marginBottom: 15,';'';
}
    const position = 'relative'}'';'';
  ;}
stepCircle: {width: 50,;
height: 50,';,'';
borderRadius: 25,';,'';
backgroundColor: '#e9ecef';','';
alignItems: 'center';','';
justifyContent: 'center';','';'';
}
    const marginBottom = 8;}
  },';,'';
stepCompleted: {,';}}'';
  const backgroundColor = '#28a745'}'';'';
  ;},';,'';
stepCurrent: {,';}}'';
  const backgroundColor = '#007AFF'}'';'';
  ;}
stepIcon: {,;}}
  const fontSize = 20;}
  },';,'';
stepIconActive: {,';}}'';
  const color = '#ffffff'}'';'';
  ;}
stepTitle: {,';,}fontSize: 12,';,'';
color: '#6c757d';','';'';
}
    const textAlign = 'center'}'';'';
  ;},';,'';
stepTitleActive: {,';,}color: '#1a1a1a';','';'';
}
    const fontWeight = '600'}'';'';
  ;},';,'';
stepConnector: {,';,}position: 'absolute';','';
top: 25,';,'';
left: '100%';','';
width: screenWidth / 4 - 40,'/;,'/g,'/;
  height: 2,';'';
}
    const backgroundColor = '#e9ecef'}'';'';
  ;},';,'';
stepConnectorCompleted: {,';}}'';
  const backgroundColor = '#28a745'}'';'';
  ;},';,'';
stepContent: {,';,}backgroundColor: '#ffffff';','';
borderRadius: 12,';,'';
padding: 30,';,'';
alignItems: 'center';','';
shadowColor: '#000';','';
shadowOffset: {width: 0,;
}
      const height = 2;}
    }
shadowOpacity: 0.1,;
shadowRadius: 8,;
const elevation = 4;
  }
stepDescription: {,';,}fontSize: 16,';,'';
color: '#6c757d';','';
textAlign: 'center';','';
marginBottom: 30,;
}
    const lineHeight = 24;}
  }
estimatedTime: {,';,}fontSize: 14,';,'';
color: '#6c757d';','';
marginTop: 20,';'';
}
    const textAlign = 'center'}'';'';
  ;},';,'';
startButton: {,';,}backgroundColor: '#007AFF';','';
paddingHorizontal: 40,;
paddingVertical: 15,;
borderRadius: 8,;
marginBottom: 15,;
}
    const minWidth = 200;}
  },';,'';
startButtonText: {,';,}color: '#ffffff';','';
fontSize: 16,';,'';
fontWeight: '600';','';'';
}
    const textAlign = 'center'}'';'';
  ;},';,'';
actionButton: {,';,}backgroundColor: '#007AFF';','';
paddingHorizontal: 40,;
paddingVertical: 15,;
borderRadius: 8,;
marginBottom: 15,;
}
    const minWidth = 200;}
  },';,'';
actionButtonText: {,';,}color: '#ffffff';','';
fontSize: 16,';,'';
fontWeight: '600';','';'';
}
    const textAlign = 'center'}'';'';
  ;},';,'';
calculationOptions: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';'';
}
    const marginBottom = 20;}
  }
calculationTitle: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';'';
}
    const color = '#1a1a1a'}'';'';
  ;}
calculationOption: {padding: 10,';,'';
borderWidth: 1,';,'';
borderColor: '#e9ecef';','';'';
}
    const borderRadius = 8;}
  }
calculationOptionText: {,';,}fontSize: 16,';'';
}
    const color = '#1a1a1a'}'';'';
  ;},';,'';
resultsContainer: {,';,}alignItems: 'center';','';'';
}
    const marginBottom = 30;}
  }
resultsTitle: {,';,}fontSize: 24,';,'';
fontWeight: '700';','';
color: '#28a745';','';'';
}
    const marginBottom = 10;}
  }
resultsText: {,';,}fontSize: 18,';,'';
color: '#1a1a1a';',)'';'';
}
    const marginBottom = 5;)}
  })';'';
});