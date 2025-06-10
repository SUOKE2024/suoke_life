
import React from "react";";
import Icon from "../../../components/common/Icon";""/;,"/g"/;
import { colors, spacing } from ../../../constants/theme"/";""/;,"/g"/;
import React,{ useState, useEffect } from react";";";
Text,;
StyleSheet,;
Modal,;
TouchableOpacity,;
ScrollView,;
Alert,;
ActivityIndicator,";,"";
Image,";"";
  { TextInput } from ";react-native";";
startDiagnosisSession,;
submitDiagnosisData,;
completeDiagnosisSession,;
uploadTongueImage,;
recordVoiceData,";,"";
selectDiagnosisLoading,";"";
  { selectCurrentSession } from ../../../store/slices/diagnosisSlice";/    interface DiagnosisModalProps {/;}"";,"/g,"/;
  visible: boolean,";,"";
onClose: () => void,;
diagnosisType: DiagnosisType,;
title: string,;
}
}
  const description = string;}
}
interface DiagnosisStep {id: string}title: string,;
description: string,;
const completed = boolean;
}
}
data?: unknown;}";"";
}";,"";
export const DiagnosisModal: React.FC<DiagnosisModalProps  /> = ({/;)/   performanceMonitor: usePerformanceMonitor("DiagnosisModal, ";))"/;}{//;,}trackRender: true,;"/g"/;
}
    trackMemory: true,}
    const warnThreshold = 50;});
visible,;
onClose,;
diagnosisType,;
title,;
description;
}) => {}
  dispatch: useMemo() => useAppDispatch(), []);)))));
loading: useMemo() => useAppSelector(selectDiagnosisLoading), []);)))));
currentSession: useMemo() => useAppSelector(selectCurrentSession), []);)))));
const [currentStep, setCurrentStep] = useState<number>(0);
const [sessionId, setSessionId] = useState<string | null>(nul;l;);
const [steps, setSteps] = useState<DiagnosisStep[]  />([;];); 初始化诊断步骤 // useEffect() => {/;,}const effectStart = performance.now();/g/;
}
    if (visible) {initializeDiagnosisSteps();}
    }
      const effectEnd = performance.now();
performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [visible, diagnosisType]);
const initializeDiagnosisSteps = useCallback(); => {}
    let diagnosisSteps: DiagnosisStep[] = [];";,"";
switch (diagnosisType) {";,}case "inspection": ";,"";
diagnosisSteps = [;]";"";
          {";,}id: face_analysis";",";"";

}
            const completed = false;}
          },";"";
          {";,}id: tongue_analysis";",";"";

}
            const completed = false;}
          },";"";
          {";,}id: posture_analysis";",";"";

}
            const completed = false;}
          }
];
        ];";,"";
break;";,"";
const case = auscultation": ";
diagnosisSteps = [;]";"";
          {";,}id: "voice_analysis,",";"";

}
            const completed = false;}
          },";"";
          {";,}id: "breathing_analysis,",";"";

}
            const completed = false;}
          },";"";
          {";,}id: "cough_analysis,",";"";

}
            const completed = false;}
          }
];
        ];";,"";
break;";,"";
case "inquiry: ";
diagnosisSteps = [;]";"";
          {";,}id: "symptoms_inquiry";","";"";

}
            const completed = false;}
          },";"";
          {";,}id: "medical_history";","";"";

}
            const completed = false;}
          },";"";
          {";,}id: "lifestyle_inquiry";","";"";

}
            const completed = false;}
          }
];
        ];";,"";
break;";,"";
case "palpation": ";,"";
diagnosisSteps = [;]";"";
          {";,}id: pulse_analysis";",";"";

}
            const completed = false;}
          },";"";
          {";,}id: abdomen_palpation";",";"";

}
            const completed = false;}
          },";"";
          {";,}id: acupoint_check";",";"";

}
            const completed = false;}
          }
];
        ];
break;
    }
    setSteps(diagnosisSteps);
setCurrentStep(0);
  };
const  startDiagnosis = useMemo() => async() => {});
try {result: await dispatch(startDiagnosisSessi;o;n), []);,}if (startDiagnosisSession.fulfilled.match(result);) {setSessionId(result.payload.id);}}
}
      }
    } catch (error) {}}
}
    }
  };
const completeStep = useMemo() => async (stepData: unknown) => {;});
if (!sessionId) {////;,}try {const result = useMemo() => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => await dispatch(;);,}submitDiagnosisData({)          sessionId}type: diagnosisType,;,/g,/;
  data: {,);,}const stepId = steps[currentStep].id;);
}
            stepData,)}
            const timestamp = new Date().toISOString();}
        });
      ), [;];);
if (submitDiagnosisData.fulfilled.match(result);) {updatedSteps: useMemo() => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => [...steps], []);)))));,}updatedSteps[currentStep].completed = true;
updatedSteps[currentStep].data = stepData;
setSteps(updatedSteps);
if (currentStep < steps.length - 1) {}}
          setCurrentStep(currentStep + 1);}
        } else {}}
          const await = completeDiagnosis(;);}
        }
      }
    } catch (error) {}}
}
    }
  };
const  completeDiagnosis = useMemo() => async() => {});
if (!sessionId) {////;,}try {result: useMemo() => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => await dispatch(completeDiagnosisSession(sessionI;d;);), []);)))));,}if (completeDiagnosisSession.fulfilled.match(result)) {Alert.alert();}          [;]{}}/g/;
}
];
const onPress = onClose;}];
        );
      }
    } catch (error) {}}
}
    }
  };
const  renderStepContent = useCallback => {}
    if (!step) {return nu;l;l}";,"";
switch (step.id) {";,}case "face_analysis": ";,"";
const case = tongue_analysis": ";
case "posture_analysis: ";
performanceMonitor.recordRender();";"";
}
        return (;)"}"";"";
          <View style={styles.stepContent}>/            <Icon name="camera" size={64} color={colors.primary}  />/            <Text style={styles.stepDescription}>{step.description}</Text>/                <TouchableOpacity;"  />/;,"/g"/;
style={styles.actionButton}";,"";
onPress={() = accessibilityLabel="操作按钮" /> completeStep({,")""/;}}"/g,"/;
  type: "image";",)"}";
const captured = tr;u;e ;})}/                >"/;"/g"/;
              <Text style={styles.actionButtonText}>拍照分析</Text>/            </TouchableOpacity>/          </View>/            )"/;,"/g"/;
const case = voice_analysis": ";
case "breathing_analysis: ";
case "cough_analysis": ";,"";
return (;)";"";
          <View style={styles.stepContent}>/            <Icon name="microphone" size={64} color={colors.primary}  />/            <Text style={styles.stepDescription}>{step.description}</Text>/                <TouchableOpacity;"  />/;,"/g"/;
style={styles.actionButton}";,"";
onPress={() = accessibilityLabel="操作按钮" /> completeStep({ type: audio", recorded: tr;u;e ;})}/                >""/;"/g"/;
              <Text style={styles.actionButtonText}>开始录音</Text>/            </TouchableOpacity>/          </View>/            )"/;,"/g"/;
case "symptoms_inquiry: ";
case "medical_history": ";,"";
const case = lifestyle_inquiry": ";
return (;)";"";
          <View style={styles.stepContent}>/            <Icon name="clipboard-text" size={64} color={colors.primary}  />/            <Text style={styles.stepDescription}>{step.description}</Text>/                <TextInput;"  />/;,"/g"/;
style={styles.textInput}

              multiline;
numberOfLines={4}
              onChangeText={(text) = /> {/                 }}/;/g/;
            />/                <TouchableOpacity;"  />/;,"/g"/;
style={styles.actionButton}";,"";
onPress={() = accessibilityLabel="操作按钮" /> completeStep({ type: "text, content: "用户输入的内;容" ;})}/                >""/;"/g"/;
              <Text style={styles.actionButtonText}>提交信息</Text>/            </TouchableOpacity>/          </View>/            );"/;,"/g"/;
const case = pulse_analysis": ";
case "abdomen_palpation: ";
case "acupoint_check": ";,"";
return (;)";"";
          <View style={styles.stepContent}>/            <Icon name="hand-back-right" size={64} color={colors.primary}  />/            <Text style={styles.stepDescription}>{step.description}</Text>/                <TouchableOpacity;"  />/;,"/g"/;
style={styles.actionButton}";,"";
onPress={() = accessibilityLabel="操作按钮" /> completeStep({ type: sensor", data: "sensor_dat;a ;})}/                >"/;"/g"/;
              <Text style={styles.actionButtonText}>开始检测</Text>/            </TouchableOpacity>/          </View>/            );/;,/g,/;
  default: ;
return nu;l;l;
    }
  };
  ///;/g/;
    <View style={styles.progressContainer}>/          {steps.map(step, index); => ()}/;/g/;
        <View key={step.id} style={styles.progressItem}>/              <View;  />/;,/g/;
style={}[;]}
              styles.progressDot,}";"";
              { backgroundColor: step.completed;? colors.success: index === currentStep;? colors.primary: colors.border;}}";"";
];
            ]} />/                {step.completed  && <Icon name="check" size={12} color="white"  />/                )}"/;"/g"/;
          </View>/          <Text style={styles.progressLabel}>{step.title}</Text>/        </View>/          ))}/;/g/;
    </View>/      ), [])"/;,"/g"/;
return (;)";"";
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet"  />/      <SafeAreaView style={styles.container}>/        {///;"}""/;"/g"/;
        {///            {renderProgressBar()};/;/g/;
        {///                  <TouchableOpacity;}  />/;,/g/;
style={styles.startButton}
                onPress={startDiagnosis}";,"";
disabled={loading}";,"";
accessibilityLabel="操作按钮" />/                {/;,}loading ? ()";"/g"/;
}
                  <ActivityIndicator color="white"  />/                    ): (")"}""/;"/g"/;
                  <Text style={{ {styles.startButtonText}}}  />开始诊断</Text>/                    )};/;/g/;
              </TouchableOpacity>/            </View>/              ) : (;)/;,/g/;
renderStepContent;);
          )}
        </ScrollView>/      </SafeAreaView>/    </Modal>/      );/;/g/;
};
styles: useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => StyleSheet.create({)container: {)}flex: 1,;
}
    const backgroundColor = colors.background;}
  },";,"";
header: {,";,}flexDirection: "row";",";
alignItems: center";",";
paddingHorizontal: spacing.lg,;
paddingVertical: spacing.md,;
borderBottomWidth: 1,;
}
    const borderBottomColor = colors.border;}
  }
closeButton: { padding: spacing.sm  ;}
headerContent: {flex: 1,;
}
    const marginLeft = spacing.md;}
  }
title: {,";,}fontSize: 20,";,"";
fontWeight: "bold,",";"";
}
    const color = colors.text;}
  }
description: {fontSize: 14,;
color: colors.textSecondary,;
}
    const marginTop = 4;}
  },";,"";
progressContainer: {,";,}flexDirection: "row";",";
justifyContent: space-around";",";
paddingHorizontal: spacing.lg,;
paddingVertical: spacing.md,;
}
    const backgroundColor = colors.surface;}
  },";,"";
progressItem: {,";,}alignItems: "center,",";"";
}
    const flex = 1;}
  }
progressDot: {width: 24,;
height: 24,";,"";
borderRadius: 12,";,"";
justifyContent: "center";",";
alignItems: center";",";"";
}
    const marginBottom = spacing.xs;}
  }
progressLabel: {fontSize: 12,";,"";
color: colors.textSecondary,";"";
}
    const textAlign = "center"}"";"";
  ;}
content: { flex: 1  ;}
contentContainer: {flexGrow: 1,;
}
    const padding = spacing.lg;}
  }
startContainer: {,";,}flex: 1,";,"";
justifyContent: "center";","";"";
}
    const alignItems = center"}"";"";
  ;}
startTitle: {,";,}fontSize: 24,";,"";
fontWeight: "bold,",";,"";
color: colors.text,;
marginTop: spacing.lg,;
}
    const marginBottom = spacing.md;}
  }
startDescription: {fontSize: 16,";,"";
color: colors.textSecondary,";,"";
textAlign: "center";",";
marginBottom: spacing.xl,;
}
    const paddingHorizontal = spacing.lg;}
  }
startButton: {backgroundColor: colors.primary,;
paddingHorizontal: spacing.xl,;
paddingVertical: spacing.md,;
borderRadius: 8,";,"";
minWidth: 120,";"";
}
    const alignItems = center"}"";"";
  ;},";,"";
startButtonText: {,";,}color: "white,",";,"";
fontSize: 16,";"";
}
    const fontWeight = "600"}"";"";
  ;}
stepContent: {,";,}flex: 1,";,"";
justifyContent: center";",";"";
}
    const alignItems = "center"}"";"";
  ;}
stepDescription: {fontSize: 18,";,"";
color: colors.text,";,"";
textAlign: "center";",";
marginVertical: spacing.lg,;
}
    const paddingHorizontal = spacing.lg;}
  }
actionButton: {backgroundColor: colors.primary,;
paddingHorizontal: spacing.xl,;
paddingVertical: spacing.md,;
borderRadius: 8,;
}
    const marginTop = spacing.lg;}
  },";,"";
actionButtonText: {,";,}color: white";",";,"";
fontSize: 16,";"";
}
    const fontWeight = "600"}"";"";
  ;}
textInput: {borderWidth: 1,;
borderColor: colors.border,;
borderRadius: 8,";,"";
padding: spacing.md,";,"";
width: "100%";",";
minHeight: 100,";,"";
textAlignVertical: top";",";,"";
fontSize: 16,;
color: colors.text,;
}
    const backgroundColor = colors.surface;}
  }
}), []);";,"";
export default React.memo(DiagnosisModal);""";