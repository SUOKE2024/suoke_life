/* 能 *//;/g/;
 *//;,/g/;
import { Ionicons, MaterialIcons } from "@expo/vector-icons";""/;,"/g"/;
import { LinearGradient } from "expo-linear-gradient";";
import React, { useCallback, useEffect, useRef, useState } from "react";";
import {Alert}Animated,;
Dimensions,;
PanResponder,;
ScrollView,;
StyleSheet,;
Text,;
TouchableOpacity,;
Vibration,";"";
}
    View,'}'';'';
} from "react-native";"";"";

// 类型定义/;,/g/;
interface PulseData {position: string}rate: number,;
rhythm: string,;
strength: number,;
tension: number,;
width: number,;
depth: number,;
}
}
  const smoothness = number;}
}

interface TouchData {area: string}temperature: number,;
moisture: number,;
elasticity: number,;
tenderness: number,;
hardness: number,;
}
}
  const thickness = number;}
}

interface PalpationResult {analysis_id: string}pulse_analysis: any,;
touch_analysis: any,;
syndrome_differentiation: any,;
recommendations: string[],;
confidence: number,;
processing_time: number,;
}
}
  const timestamp = string;}
}

interface Props {patientId: string}sessionId: string,;
onAnalysisComplete: (result: PalpationResult) => void,;
}
}
  onError: (error: string) => void;}
}';'';
';,'';
const { width, height } = Dimensions.get('window');';,'';
const  PalpationDiagnosisComponent: React.FC<Props> = ({)patientId}sessionId,);
onAnalysisComplete,);
}
  onError,)}
}) => {';}  // 状态管理'/;,'/g'/;
const [currentStep, setCurrentStep] = useState<'pulse' | 'touch' | 'analysis'>('pulse');';,'';
const [pulseData, setPulseData] = useState<PulseData[]>([]);
const [touchData, setTouchData] = useState<TouchData[]>([]);';,'';
const [isAnalyzing, setIsAnalyzing] = useState(false);';,'';
const [currentPulsePosition, setCurrentPulsePosition] = useState<'寸' | '关' | '尺'>('寸');';,'';
const [currentTouchArea, setCurrentTouchArea] = useState<'腹诊' | '四肢' | '穴位' | '皮肤' | '肌肉'>('腹诊');';,'';
const [symptoms, setSymptoms] = useState<string[]>([]);

  // 脉象检测状态/;,/g/;
const [pulseRate, setPulseRate] = useState(72);
const [pulseStrength, setPulseStrength] = useState(0.5);
const [pulseTension, setPulseTension] = useState(0.5);
const [pulseDepth, setPulseDepth] = useState(0.5);
const [pulseSmoothness, setPulseSmoothness] = useState(0.5);
const [pulseWidth, setPulseWidth] = useState(0.5);
const [isRecordingPulse, setIsRecordingPulse] = useState(false);

  // 触诊状态/;,/g/;
const [touchTemperature, setTouchTemperature] = useState(0.5);
const [touchMoisture, setTouchMoisture] = useState(0.5);
const [touchElasticity, setTouchElasticity] = useState(0.5);
const [touchTenderness, setTouchTenderness] = useState(0.1);
const [touchHardness, setTouchHardness] = useState(0.5);
const [touchThickness, setTouchThickness] = useState(0.5);

  // 动画/;,/g/;
const pulseAnimation = useRef(new Animated.Value(0)).current;
const progressAnimation = useRef(new Animated.Value(0)).current;

  // 脉象动画/;,/g/;
useEffect(() => {if (isRecordingPulse) {}      const pulseInterval = 60000 / pulseRate; // 根据脉率计算间隔/;,/g/;
const  animatePulse = () => {Animated.sequence([;,)Animated.timing(pulseAnimation, {)            toValue: 1,);,]duration: 200,);}}
            useNativeDriver: true,)}
          }),;
Animated.timing(pulseAnimation, {)toValue: 0,);,}duration: pulseInterval - 200,);
}
            useNativeDriver: true,)}
          }),;
];
        ]).start(() => {if (isRecordingPulse) {}}
            animatePulse();}
          }
        });
      };
animatePulse();
    }
  }, [isRecordingPulse, pulseRate]);

  // 触诊手势识别/;,/g/;
const  touchPanResponder = PanResponder.create({));,}onStartShouldSetPanResponder: () => true,;
onMoveShouldSetPanResponder: () => true,;
onPanResponderGrant: (evt) => {}}
      // 开始触诊}/;,/g/;
const { locationX, locationY } = evt.nativeEvent;
handleTouchStart(locationX, locationY);
    }
onPanResponderMove: (evt, gestureState) => {}}
      // 触诊移动}/;,/g/;
const { dx, dy } = gestureState;
handleTouchMove(dx, dy);
    }
onPanResponderRelease: () => {// 结束触诊/;}}/g/;
      handleTouchEnd();}
    }
  });

  // 脉象检测函数/;,/g/;
const  startPulseRecording = useCallback(() => {setIsRecordingPulse(true);,}Vibration.vibrate(100); // 触觉反馈/;/g/;

    // 模拟脉象检测过程/;,/g/;
setTimeout(() => {setIsRecordingPulse(false);}}
      savePulseData();}
    }, 10000); // 10秒检测/;/g/;
  }, [currentPulsePosition, pulseRate, pulseStrength, pulseTension, pulseDepth, pulseSmoothness, pulseWidth]);
const  savePulseData = useCallback(() => {const: newPulseData: PulseData = {position: currentPulsePosition,';,'';
rate: pulseRate,';,'';
rhythm: '规整', // 简化处理'/;,'/g,'/;
  strength: pulseStrength,;
tension: pulseTension,;
width: pulseWidth,;
depth: pulseDepth,;
}
      smoothness: pulseSmoothness,}
    };
setPulseData(prev => {));,}const filtered = prev.filter(p => p.position !== currentPulsePosition);
}
      return [...filtered, newPulseData];}
    });';'';
';,'';
Alert.alert('脉象记录完成', `${currentPulsePosition}脉数据已保存`);````;```;
  }, [currentPulsePosition, pulseRate, pulseStrength, pulseTension, pulseDepth, pulseSmoothness, pulseWidth]);

  // 触诊处理函数/;,/g,/;
  const: handleTouchStart = (x: number, y: number) => {// 根据触摸位置调整参数/;,}const normalizedX = x / width;/;,/g/;
const normalizedY = y / height;/;,/g/;
setTouchTemperature(normalizedX);
}
    setTouchElasticity(1 - normalizedY);}
  };
const: handleTouchMove = (dx: number, dy: number) => {// 根据移动调整触诊参数/;,}const pressure = Math.sqrt(dx * dx + dy * dy) / 100;/;/g/;
}
    setTouchTenderness(Math.min(1, pressure));}
  };
const  handleTouchEnd = () => {Vibration.vibrate(50);}}
    saveTouchData();}
  };
const  saveTouchData = useCallback(() => {const: newTouchData: TouchData = {area: currentTouchArea,;
temperature: touchTemperature,;
moisture: touchMoisture,;
elasticity: touchElasticity,;
tenderness: touchTenderness,;
hardness: touchHardness,;
}
      thickness: touchThickness,}
    };
setTouchData(prev => {));,}const filtered = prev.filter(t => t.area !== currentTouchArea);
}
      return [...filtered, newTouchData];}
    });';'';
';,'';
Alert.alert('触诊记录完成', `${currentTouchArea}数据已保存`);````;```;
  }, [currentTouchArea, touchTemperature, touchMoisture, touchElasticity, touchTenderness, touchHardness, touchThickness]);

  // 执行分析/;,/g/;
const  performAnalysis = async () => {';,}if (pulseData.length === 0 || touchData.length === 0) {';,}Alert.alert('数据不完整', '请先完成脉象和触诊检测');';'';
}
      return;}
    }
';,'';
setIsAnalyzing(true);';,'';
setCurrentStep('analysis');';,'';
try {';}      // 模拟API调用'/;,'/g,'/;
  const: response = await fetch('/api/palpation/analyze', {'/;,)method: 'POST',';,}const headers = {';}}'/g'/;
          'Content-Type': 'application/json','}''/;'/g'/;
        }
body: JSON.stringify({)}patient_id: patientId,;
session_id: sessionId,;
pulse_data: pulseData,);
touch_data: touchData,);
}
          symptoms: symptoms,)}
        }),;
      });
';,'';
if (!response.ok) {';}}'';
        const throw = new Error('分析请求失败');'}'';'';
      }

      const result: PalpationResult = await response.json();
onAnalysisComplete(result);';'';
    } catch (error) {';}}'';
      onError(error instanceof Error ? error.message : '分析失败');'}'';'';
    } finally {}}
      setIsAnalyzing(false);}
    }
  };

  // 参数滑块组件/;,/g,/;
  const: ParameterSlider: React.FC<{label: string,;
value: number,;
onValueChange: (value: number) => void,;
}
    const icon = string;}
  }> = ({ label, value, onValueChange, icon }) => (<View style={styles.sliderContainer}>';)      <View style={styles.sliderHeader}>')'';'';
        <Ionicons name={icon as any} size={20} color="#666"  />")""/;"/g"/;
        <Text style={styles.sliderLabel}>{label}</Text>)/;/g/;
        <Text style={styles.sliderValue}>{(value * 100).toFixed(0)}%</Text>/;/g/;
      </View>/;/g/;
      <View style={styles.sliderTrack}>;
        <View style={[styles.sliderFill, { width: `${value * 100}%` }]}  />```/`;`/g`/`;
        <TouchableOpacity,  />/;,/g/;
style={[styles.sliderThumb, { left: `${value * 100}%` }]}````;,```;
onPressIn={() => {}}
            // 实现滑块拖拽逻辑}/;/g/;
          }}
        />/;/g/;
      </View>/;/g/;
    </View>/;/g/;
  );

  // 触诊参数显示组件/;,/g,/;
  const: TouchParameter: React.FC<{label: string,;
value: number,;
}
    const icon = string;}";"";
  }> = ({ label, value, icon }) => (<View style={styles.touchParameterItem}>")"";"";
      <Ionicons name={icon as any} size={16} color="#666"  />")""/;"/g"/;
      <Text style={styles.touchParameterLabel}>{label}</Text>)/;/g/;
      <Text style={styles.touchParameterValue}>{(value * 100).toFixed(0)}%</Text>/;/g/;
    </View>/;/g/;
  );

  // 渲染脉象检测界面/;,/g/;
const  renderPulseDetection = () => (<View style={styles.stepContainer}>;)      <Text style={styles.stepTitle}>脉象检测</Text>/;/g/;
      );
      {/* 脉位选择 */})"/;"/g"/;
      <View style={styles.positionSelector}>)";"";
        {}['寸', '关', '尺'].map((position) => (';)}'';
          <TouchableOpacity,}  />/;,/g/;
key={position}
            style={[;,]styles.positionButton,);}}
              currentPulsePosition === position && styles.positionButtonActive)}
];
            ]});
onPress={() => setCurrentPulsePosition(position as any)}
          >;
            <Text style={ />/;}[;,]styles.positionButtonText,;/g/;
}
              currentPulsePosition === position && styles.positionButtonTextActive}
];
            ]}>;
              {position}脉;
            </Text>/;/g/;
          </TouchableOpacity>/;/g/;
        ))}
      </View>/;/g/;

      {/* 脉象可视化 */}/;/g/;
      <View style={styles.pulseVisualization}>;
        <Animated.View,  />/;,/g/;
style={[;,]styles.pulseIndicator,;}            {transform: [{,;,]scale: pulseAnimation.interpolate({,);}];
inputRange: [0, 1],);
}
                  outputRange: [1, 1.5],)}
                });
              }],;
opacity: pulseAnimation.interpolate({),);,}inputRange: [0, 1],);
}
                outputRange: [0.5, 1],)}
              });
            }
          ]}
        />/;/g/;
        <Text style={styles.pulseRateText}>{pulseRate} 次/分</Text>/;/g/;
      </View>/;/g/;

      {/* 脉象参数调节 */}/;/g/;
      <View style={styles.parameterContainer}>';'';
        <ParameterSlider,'  />/;,'/g'/;
label="脉力";
value={pulseStrength}";,"";
onValueChange={setPulseStrength}";,"";
icon="fitness"";"";
        />"/;"/g"/;
        <ParameterSlider,"  />/;,"/g"/;
label="脉张力";
value={pulseTension}";,"";
onValueChange={setPulseTension}";,"";
icon="trending-up"";"";
        />"/;"/g"/;
        <ParameterSlider,"  />/;,"/g"/;
label="脉深度";
value={pulseDepth}";,"";
onValueChange={setPulseDepth}";,"";
icon="layers"";"";
        />"/;"/g"/;
        <ParameterSlider,"  />/;,"/g"/;
label="脉流利度";
value={pulseSmoothness}";,"";
onValueChange={setPulseSmoothness}";,"";
icon="water"";"";
        />/;/g/;
      </View>/;/g/;

      {/* 记录按钮 */}/;/g/;
      <TouchableOpacity,  />/;,/g/;
style={[styles.recordButton, isRecordingPulse && styles.recordButtonActive]}
        onPress={startPulseRecording}
        disabled={isRecordingPulse}
      >";"";
        <LinearGradient,"  />/;,"/g"/;
colors={isRecordingPulse ? ['#ff6b6b', '#ee5a52'] : ['#4ecdc4', '#44a08d']}';,'';
style={styles.recordButtonGradient}
        >';'';
          <Ionicons,'  />/;,'/g'/;
name={isRecordingPulse ? "radio-button-on" : "radio-button-off"}";,"";
size={24}";,"";
color="white"";"";
          />"/;"/g"/;
          <Text style={styles.recordButtonText}>";"";
            {isRecordingPulse ? '正在记录...' : '开始记录脉象'}';'';
          </Text>/;/g/;
        </LinearGradient>/;/g/;
      </TouchableOpacity>/;/g/;

      {/* 已记录的脉象 */}/;/g/;
      {pulseData.length > 0 && (<View style={styles.recordedData}>);
          <Text style={styles.recordedDataTitle}>已记录脉象:</Text>)/;/g/;
          {pulseData.map((pulse, index) => (<Text key={index} style={styles.recordedDataItem}>);
              {pulse.position}脉: 脉率{pulse.rate}, 脉力{(pulse.strength * 100).toFixed(0)}%;
            </Text>/;/g/;
          ))}
        </View>/;/g/;
      )}
    </View>/;/g/;
  );

  // 渲染触诊界面/;,/g/;
const  renderTouchDiagnosis = () => (<View style={styles.stepContainer}>;)      <Text style={styles.stepTitle}>触诊检测</Text>/;/g/;
      );
      {/* 触诊部位选择 */})'/;'/g'/;
      <View style={styles.areaSelector}>)';'';
        {}['腹诊', '四肢', '穴位', '皮肤', '肌肉'].map((area) => (';)}'';
          <TouchableOpacity,}  />/;,/g/;
key={area}
            style={[;,]styles.areaButton,);}}
              currentTouchArea === area && styles.areaButtonActive)}
];
            ]});
onPress={() => setCurrentTouchArea(area as any)}
          >;
            <Text style={ />/;}[;,]styles.areaButtonText,;/g/;
}
              currentTouchArea === area && styles.areaButtonTextActive}
];
            ]}>;
              {area}
            </Text>/;/g/;
          </TouchableOpacity>/;/g/;
        ))}
      </View>/;/g/;

      {/* 触诊区域 */}/;/g/;
      <View,  />/;,/g/;
style={styles.touchArea}
        {...touchPanResponder.panHandlers}
      >;
        <Text style={styles.touchAreaText}>;
          在此区域进行触诊操作;
        </Text>/;/g/;
        <Text style={styles.touchAreaSubtext}>;
          轻触、按压、滑动来采集触诊数据;
        </Text>/;/g/;
      </View>/;/g/;

      {/* 触诊参数显示 */}'/;'/g'/;
      <View style={styles.touchParameters}>';'';
        <TouchParameter label="温度" value={touchTemperature} icon="thermometer"  />"/;"/g"/;
        <TouchParameter label="湿润度" value={touchMoisture} icon="water-drop"  />"/;"/g"/;
        <TouchParameter label="弹性" value={touchElasticity} icon="fitness"  />"/;"/g"/;
        <TouchParameter label="压痛" value={touchTenderness} icon="warning"  />"/;"/g"/;
      </View>/;/g/;

      {/* 已记录的触诊数据 */}/;/g/;
      {touchData.length > 0 && (<View style={styles.recordedData}>);
          <Text style={styles.recordedDataTitle}>已记录触诊:</Text>)/;/g/;
          {touchData.map((touch, index) => (<Text key={index} style={styles.recordedDataItem}>);
              {touch.area}: 温度{(touch.temperature * 100).toFixed(0)}%, 弹性{(touch.elasticity * 100).toFixed(0)}%;
            </Text>/;/g/;
          ))}
        </View>/;/g/;
      )}
    </View>/;/g/;
  );

  // 渲染分析界面/;,/g/;
const  renderAnalysis = () => (<View style={styles.stepContainer}>;)      <Text style={styles.stepTitle}>切诊分析</Text>/;/g/;

      {isAnalyzing ? (})        <View style={styles.analysisContainer}>;
          <Animated.View,  />/;,/g/;
style={[;,]styles.analysisIndicator,;}              {transform: [{,;,]rotate: progressAnimation.interpolate({,)";}];,"";
inputRange: [0, 1],)";"";
}
                    outputRange: ['0deg', '360deg'],')'}'';'';
                  });
                }];
              }
            ]}
          />/;/g/;
          <Text style={styles.analysisText}>正在分析切诊数据...</Text>/;/g/;
          <Text style={styles.analysisSubtext}>;
AI正在综合脉象和触诊信息进行辨证分析;
          </Text>/;/g/;
        </View>'/;'/g'/;
      ) : (<View style={styles.analysisReady}>';)          <MaterialIcons name="analytics" size={64} color="#4ecdc4"  />"/;"/g"/;
          <Text style={styles.analysisReadyText}>;
            数据采集完成，准备进行分析;
          </Text>/;/g/;
          <TouchableOpacity,  />/;,/g/;
style={styles.analyzeButton}
            onPress={performAnalysis}
          >";"";
            <LinearGradient,"  />/;,"/g"/;
colors={['#667eea', '#764ba2']}';,'';
style={styles.analyzeButtonGradient}
            >;
              <Text style={styles.analyzeButtonText}>开始分析</Text>/;/g/;
            </LinearGradient>)/;/g/;
          </TouchableOpacity>)/;/g/;
        </View>)/;/g/;
      )}
    </View>/;/g/;
  );

  // 步骤导航/;,/g/;
const  renderStepNavigation = () => (<View style={styles.stepNavigation}>)';'';
      <TouchableOpacity,)'  />/;,'/g'/;
style={[styles.stepButton, currentStep === 'pulse' && styles.stepButtonActive]}')'';
onPress={() => setCurrentStep('pulse')}';'';
      >';'';
        <Text style={[styles.stepButtonText, currentStep === 'pulse' && styles.stepButtonTextActive]}>';'';
          脉象;
        </Text>/;/g/;
      </TouchableOpacity>'/;'/g'/;
      <TouchableOpacity,'  />/;,'/g'/;
style={[styles.stepButton, currentStep === 'touch' && styles.stepButtonActive]}';,'';
onPress={() => setCurrentStep('touch')}';'';
      >';'';
        <Text style={[styles.stepButtonText, currentStep === 'touch' && styles.stepButtonTextActive]}>';'';
          触诊;
        </Text>/;/g/;
      </TouchableOpacity>'/;'/g'/;
      <TouchableOpacity,'  />/;,'/g'/;
style={[styles.stepButton, currentStep === 'analysis' && styles.stepButtonActive]}';,'';
onPress={() => setCurrentStep('analysis')}';'';
      >';'';
        <Text style={[styles.stepButtonText, currentStep === 'analysis' && styles.stepButtonTextActive]}>';'';
          分析;
        </Text>/;/g/;
      </TouchableOpacity>/;/g/;
    </View>/;/g/;
  );
return (<View style={styles.container}>);
      {renderStepNavigation()}';'';
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>';'';
        {currentStep === 'pulse' && renderPulseDetection()}';'';
        {currentStep === 'touch' && renderTouchDiagnosis()}';'';
        {currentStep === 'analysis' && renderAnalysis()}';'';
      </ScrollView>/;/g/;
    </View>/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,';,}flex: 1,';'';
}
    backgroundColor: '#f8f9fa','}'';'';
  },';,'';
stepNavigation: {,';,}flexDirection: 'row',';,'';
backgroundColor: 'white',';,'';
paddingHorizontal: 20,;
paddingVertical: 15,';,'';
borderBottomWidth: 1,';'';
}
    borderBottomColor: '#e9ecef','}'';'';
  }
stepButton: {flex: 1,';,'';
paddingVertical: 10,';,'';
alignItems: 'center',';,'';
borderRadius: 8,;
}
    marginHorizontal: 5,}
  },';,'';
stepButtonActive: {,';}}'';
    backgroundColor: '#4ecdc4','}'';'';
  }
stepButtonText: {,';,}fontSize: 16,';,'';
color: '#666',';'';
}
    fontWeight: '500','}'';'';
  },';,'';
stepButtonTextActive: {,';}}'';
    color: 'white','}'';'';
  }
content: {,;}}
    flex: 1,}
  }
stepContainer: {,;}}
    padding: 20,}
  }
stepTitle: {,';,}fontSize: 24,';,'';
fontWeight: 'bold',';,'';
color: '#2c3e50',';,'';
marginBottom: 20,';'';
}
    textAlign: 'center','}'';'';
  },';,'';
positionSelector: {,';,}flexDirection: 'row',';,'';
justifyContent: 'space-around',';'';
}
    marginBottom: 30,}
  }
positionButton: {paddingHorizontal: 20,;
paddingVertical: 12,;
borderRadius: 25,';,'';
borderWidth: 2,';,'';
borderColor: '#4ecdc4',';'';
}
    backgroundColor: 'white','}'';'';
  },';,'';
positionButtonActive: {,';}}'';
    backgroundColor: '#4ecdc4','}'';'';
  }
positionButtonText: {,';,}fontSize: 16,';,'';
color: '#4ecdc4',';'';
}
    fontWeight: '600','}'';'';
  },';,'';
positionButtonTextActive: {,';}}'';
    color: 'white','}'';'';
  },';,'';
pulseVisualization: {,';,}alignItems: 'center',';'';
}
    marginBottom: 30,}
  }
pulseIndicator: {width: 100,;
height: 100,';,'';
borderRadius: 50,';,'';
backgroundColor: '#ff6b6b',';'';
}
    marginBottom: 15,}
  }
pulseRateText: {,';,}fontSize: 18,';,'';
fontWeight: 'bold',';'';
}
    color: '#2c3e50','}'';'';
  }
parameterContainer: {,;}}
    marginBottom: 30,}
  }
sliderContainer: {,;}}
    marginBottom: 20,}
  },';,'';
sliderHeader: {,';,}flexDirection: 'row',';,'';
alignItems: 'center',';'';
}
    marginBottom: 10,}
  }
sliderLabel: {flex: 1,';,'';
fontSize: 16,';,'';
color: '#2c3e50',';'';
}
    marginLeft: 10,}
  }
sliderValue: {,';,}fontSize: 16,';,'';
color: '#4ecdc4',';'';
}
    fontWeight: 'bold','}'';'';
  }
sliderTrack: {,';,}height: 6,';,'';
backgroundColor: '#e9ecef',';,'';
borderRadius: 3,';'';
}
    position: 'relative','}'';'';
  },';,'';
sliderFill: {,';,}height: '100%',';,'';
backgroundColor: '#4ecdc4',';'';
}
    borderRadius: 3,}
  },';,'';
sliderThumb: {,';,}position: 'absolute',';,'';
top: -7,;
width: 20,;
height: 20,';,'';
borderRadius: 10,';,'';
backgroundColor: '#4ecdc4',';'';
}
    marginLeft: -10,}
  }
recordButton: {,;}}
    marginBottom: 20,}
  }
const recordButtonActive = {}}
    // 活跃状态样式}/;/g/;
  },';,'';
recordButtonGradient: {,';,}flexDirection: 'row',';,'';
alignItems: 'center',';,'';
justifyContent: 'center',';,'';
paddingVertical: 15,;
}
    borderRadius: 12,}
  },';,'';
recordButtonText: {,';,}color: 'white',';,'';
fontSize: 18,';,'';
fontWeight: 'bold',';'';
}
    marginLeft: 10,}
  },';,'';
areaSelector: {,';,}flexDirection: 'row',';,'';
flexWrap: 'wrap',';,'';
justifyContent: 'space-around',';'';
}
    marginBottom: 30,}
  }
areaButton: {paddingHorizontal: 15,;
paddingVertical: 8,;
borderRadius: 20,';,'';
borderWidth: 1,';,'';
borderColor: '#4ecdc4',';,'';
backgroundColor: 'white',';'';
}
    marginBottom: 10,}
  },';,'';
areaButtonActive: {,';}}'';
    backgroundColor: '#4ecdc4','}'';'';
  }
areaButtonText: {,';,}fontSize: 14,';,'';
color: '#4ecdc4',';'';
}
    fontWeight: '500','}'';'';
  },';,'';
areaButtonTextActive: {,';}}'';
    color: 'white','}'';'';
  }
touchArea: {,';,}height: 200,';,'';
backgroundColor: 'white',';,'';
borderRadius: 12,';,'';
borderWidth: 2,';,'';
borderColor: '#4ecdc4',';,'';
borderStyle: 'dashed',';,'';
justifyContent: 'center',';,'';
alignItems: 'center',';'';
}
    marginBottom: 20,}
  }
touchAreaText: {,';,}fontSize: 18,';,'';
color: '#2c3e50',';,'';
fontWeight: '600',';'';
}
    marginBottom: 5,}
  }
touchAreaSubtext: {,';,}fontSize: 14,';,'';
color: '#666',';'';
}
    textAlign: 'center','}'';'';
  },';,'';
touchParameters: {,';,}flexDirection: 'row',';,'';
flexWrap: 'wrap',';,'';
justifyContent: 'space-between',';'';
}
    marginBottom: 20,}
  },';,'';
touchParameterItem: {,';,}flexDirection: 'row',';,'';
alignItems: 'center',';,'';
width: '48%',';,'';
backgroundColor: 'white',';,'';
padding: 12,;
borderRadius: 8,;
}
    marginBottom: 10,}
  }
touchParameterLabel: {flex: 1,';,'';
fontSize: 14,';,'';
color: '#2c3e50',';'';
}
    marginLeft: 8,}
  }
touchParameterValue: {,';,}fontSize: 14,';,'';
color: '#4ecdc4',';'';
}
    fontWeight: 'bold','}'';'';
  },';,'';
recordedData: {,';,}backgroundColor: 'white',';,'';
padding: 15,;
borderRadius: 12,';,'';
borderLeftWidth: 4,';'';
}
    borderLeftColor: '#4ecdc4','}'';'';
  }
recordedDataTitle: {,';,}fontSize: 16,';,'';
fontWeight: 'bold',';,'';
color: '#2c3e50',';'';
}
    marginBottom: 10,}
  }
recordedDataItem: {,';,}fontSize: 14,';,'';
color: '#666',';'';
}
    marginBottom: 5,}
  },';,'';
analysisContainer: {,';,}alignItems: 'center',';'';
}
    paddingVertical: 50,}
  }
analysisIndicator: {width: 60,;
height: 60,';,'';
borderWidth: 4,';,'';
borderColor: '#4ecdc4',';,'';
borderTopColor: 'transparent',';,'';
borderRadius: 30,;
}
    marginBottom: 20,}
  }
analysisText: {,';,}fontSize: 18,';,'';
color: '#2c3e50',';,'';
fontWeight: '600',';'';
}
    marginBottom: 10,}
  }
analysisSubtext: {,';,}fontSize: 14,';,'';
color: '#666',';'';
}
    textAlign: 'center','}'';'';
  },';,'';
analysisReady: {,';,}alignItems: 'center',';'';
}
    paddingVertical: 50,}
  }
analysisReadyText: {,';,}fontSize: 18,';,'';
color: '#2c3e50',';,'';
fontWeight: '600',';,'';
marginVertical: 20,';'';
}
    textAlign: 'center','}'';'';
  }
analyzeButton: {,;}}
    marginTop: 20,}
  }
analyzeButtonGradient: {paddingHorizontal: 40,;
paddingVertical: 15,;
}
    borderRadius: 12,}
  },';,'';
analyzeButtonText: {,';,}color: 'white',';,'';
fontSize: 18,')'';'';
}
    fontWeight: 'bold',')}'';'';
  },);
});
';,'';
export default PalpationDiagnosisComponent; ''';