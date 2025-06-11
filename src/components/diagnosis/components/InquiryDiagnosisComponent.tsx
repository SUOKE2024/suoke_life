import React, { useCallback, useState } from "react";
import {ActivityIndicator,
Alert,
ScrollView,
StyleSheet,
Text,
TextInput,"
TouchableOpacity,";
} fromiew'}
} from "react-native;
import { colors, spacing } from "../../../constants/theme"
import {DiagnosisComponentProps,";
} fromnquiryDiagnosisData'}
} from "../../../types/diagnosis"
interface Symptom {id: string}name: string,
category: string,
}
}
  const selected = boolean}
}
export const InquiryDiagnosisComponent: React.FC<DiagnosisComponentProps> = ({))onComplete,);
}
  onCancel)};
;}) => {const [currentSymptoms, setCurrentSymptoms] = useState<Symptom[]>([;));]});
];
  ]);
const [medicalHistory, setMedicalHistory] = useState(');
const [lifestyle, setLifestyle] = useState({',)sleep: ,'diet: ,')'
exercise: ,')'
}
    const stress = ')'}
  ;});
const [painLevel, setPainLevel] = useState(0);
const [symptomDuration, setSymptomDuration] = useState(');'';
const [isAnalyzing, setIsAnalyzing] = useState(false);
const [analysisResult, setAnalysisResult] = useState<any>(null);
const  toggleSymptom = useCallback(symptomId: string) => {setCurrentSymptoms(prev) =>prev.map(symptom) =>;
}
        symptom.id === symptomId}
          ? { ...symptom, selected: !symptom.selected }
          : symptom;
      );
    );
  }, []);
const  analyzeInquiry = useCallback(async () => {const selectedSymptoms = currentSymptoms.filter(s) => s.selected)if (selectedSymptoms.length === 0) {}
      return}
    }
    setIsAnalyzing(true);
try {// 模拟问诊分析过程/await: new Promise(resolve => setTimeout(resolve, 2000)),/g/;
const  mockResult = {symptomAnalysis: {primarySymptoms: selectedSymptoms.map(s) => s.name),
}
          const confidence = 0.87}
        }
syndromePattern: {,}
          const confidence = 0.82}
        }
riskAssessment: {const recommendations = [;]}
];
          ]}
        }
      };
setAnalysisResult(mockResult);
    } catch (error) {}
}
    } finally {}
      setIsAnalyzing(false)}
    }
  }, [currentSymptoms, painLevel, symptomDuration]);
const  handleComplete = useCallback() => {const selectedSymptoms = currentSymptoms.filter(s) => s.selected)const: data: InquiryDiagnosisData = {symptoms: selectedSymptoms.map(s) => s.name),
const medicalHistory = medicalHistory ? [medicalHistory] : [];
lifestyle,
currentSymptoms: selectedSymptoms.map(s) => s.name);
painLevel,
}
      const duration = symptomDuration}
    ;};
onComplete(data);
  }, []currentSymptoms,
medicalHistory,
lifestyle,
painLevel,
symptomDuration,
onComplete;
];
  ]);
const  renderSymptomSection = () => {const categories = [...new Set(currentSymptoms.map(s) => s.category))]}
}
    return (<View style={styles.symptomSection}>;)        <Text style={styles.sectionTitle}>当前症状</Text>)
        <Text style={styles.sectionDescription}>请选择您目前的症状</Text>)
);
        {categories.map(category) => (<View key={category} style={styles.categoryContainer}>;)            <Text style={styles.categoryTitle}>{category}</Text>)
            <View style={styles.symptomGrid}>);
              {currentSymptoms;}                .filter(s) => s.category === category);
}
                .map(symptom) => (<TouchableOpacity;}  />/,)key={symptom.id}/g/;
                    style={[]styles.symptomButton,)}
                      symptom.selected && styles.symptomButtonSelected)}
];
                    ]});
onPress={() => toggleSymptom(symptom.id)}
                  >;
                    <Text;  />
style={[]styles.symptomText,}
                        symptom.selected && styles.symptomTextSelected}
];
                      ]}
                    >;
                      {symptom.name}
                    </Text>
                  </TouchableOpacity>
                ))}
            </View>
          </View>
        ))}
      </View>
    );
  };
const  renderPainLevelSection = () => (<View style={styles.painSection}>;)      <Text style={styles.sectionTitle}>疼痛程度</Text>
      <Text style={styles.sectionDescription}>;
);
      </Text>)
      <View style={styles.painLevelContainer}>);
        {[...Array(11)].map(_, index) => (<TouchableOpacity;}  />/,)key={index}/g/;
            style={[]styles.painLevelButton,)}
              painLevel === index && styles.painLevelButtonSelected)}
];
            ]});
onPress={() => setPainLevel(index)}
          >;
            <Text;  />
style={[]styles.painLevelText,}
                painLevel === index && styles.painLevelTextSelected}
];
              ]}
            >;
              {index}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
      <View style={styles.painLevelLabels}>;
        <Text style={styles.painLevelLabel}>无痛</Text>
        <Text style={styles.painLevelLabel}>剧痛</Text>
      </View>
    </View>
  );
const  renderLifestyleSection = () => (<View style={styles.lifestyleSection}>;)      <Text style={styles.sectionTitle}>生活方式</Text>
      <View style={styles.inputGroup}>;
        <Text style={styles.inputLabel}>睡眠情况</Text>
        <TextInput;  />
style={styles.textInput});
);
value={lifestyle.sleep});
onChangeText={(text) =>}
            setLifestyle(prev) => ({  ...prev, sleep: text ; }));
          }
          multiline;
        />
      </View>
      <View style={styles.inputGroup}>;
        <Text style={styles.inputLabel}>饮食习惯</Text>
        <TextInput;  />
style={styles.textInput}
          value={lifestyle.diet}
          onChangeText={(text) =>}
            setLifestyle(prev) => ({  ...prev, diet: text ; }));
          }
          multiline;
        />
      </View>
      <View style={styles.inputGroup}>;
        <Text style={styles.inputLabel}>运动情况</Text>
        <TextInput;  />
style={styles.textInput}
          value={lifestyle.exercise}
          onChangeText={(text) =>}
            setLifestyle(prev) => ({  ...prev, exercise: text ; }));
          }
          multiline;
        />
      </View>
      <View style={styles.inputGroup}>;
        <Text style={styles.inputLabel}>压力状况</Text>
        <TextInput;  />
style={styles.textInput}
          value={lifestyle.stress}
          onChangeText={(text) =>}
            setLifestyle(prev) => ({  ...prev, stress: text ; }));
          }
          multiline;
        />
      </View>
    </View>
  );
const  renderAnalysisResult = () => {if (!analysisResult) return null}
}
    return (<View style={styles.resultContainer}>;)        <Text style={styles.resultTitle}>分析结果</Text>
        <View style={styles.analysisSection}>;
          <Text style={styles.analysisTitle}>症状分析</Text>)
          <Text style={styles.analysisText}>)
)'
            {analysisResult.symptomAnalysis.primarySymptoms.join('、')}
          </Text>
          <Text style={styles.analysisText}>;
          </Text>
          <Text style={styles.analysisText}>;
          </Text>
          <Text style={styles.confidenceText}>;
            {(analysisResult.symptomAnalysis.confidence * 100).toFixed(1)}%;
          </Text>
        </View>
        <View style={styles.analysisSection}>;
          <Text style={styles.analysisTitle}>证候分析</Text>
          <Text style={styles.analysisText}>;
          </Text>
          <Text style={styles.analysisText}>;
          </Text>
          <Text style={styles.confidenceText}>;
            {(analysisResult.syndromePattern.confidence * 100).toFixed(1)}%;
          </Text>
        </View>
        <View style={styles.recommendationSection}>;
          <Text style={styles.analysisTitle}>建议</Text>
          {analysisResult.riskAssessment.recommendations.map(rec: string, index: number) => (<Text key={index;} style={styles.recommendationText}>);
                • {rec});
              </Text>)
            );
          )}
        </View>
      </View>
    );
  };
return (<ScrollView style={styles.container} showsVerticalScrollIndicator={false}>;)      <Text style={styles.title}>问诊分析</Text>
      <Text style={styles.subtitle}>;
);
      </Text>)
);
      {renderSymptomSection()}
      {renderPainLevelSection()}
      <View style={styles.inputSection}>;
        <Text style={styles.sectionTitle}>症状持续时间</Text>
        <TextInput;  />
style={styles.textInput}
          value={symptomDuration}
          onChangeText={setSymptomDuration}
        />
      </View>
      <View style={styles.inputSection}>;
        <Text style={styles.sectionTitle}>既往病史</Text>
        <TextInput;  />
style={[styles.textInput, styles.multilineInput]}
          value={medicalHistory}
          onChangeText={setMedicalHistory}
          multiline;
numberOfLines={4}
        />
      </View>
      {renderLifestyleSection()}
      <View style={styles.actionContainer}>;
        <TouchableOpacity;  />
style={[styles.button, styles.analyzeButton]}
          onPress={analyzeInquiry}
          disabled={isAnalyzing}
        >'
          {isAnalyzing ? (<ActivityIndicator size="small" color={colors.white}  />")
          ) : (<Text style={styles.buttonText}>开始分析</Text>)
          )}
        </TouchableOpacity>
      </View>
      {renderAnalysisResult()}
      {analysisResult && (<View style={styles.actionContainer}>;)          <TouchableOpacity;  />
style={[styles.button, styles.completeButton]}
            onPress={handleComplete}
          >;
            <Text style={styles.buttonText}>完成问诊</Text>)
          </TouchableOpacity>)
        </View>)
      )}
    </ScrollView>
  );
};
const  styles = StyleSheet.create({)container: {flex: 1,
}
    const padding = spacing.md}
  }
title: {,"fontSize: 20,","
fontWeight: '600,'';
color: colors.textPrimary,
}
    const marginBottom = spacing.sm}
  }
subtitle: {fontSize: 14,
color: colors.textSecondary,
marginBottom: spacing.lg,
}
    const lineHeight = 20}
  }
symptomSection: {,}
  const marginBottom = spacing.lg}
  }
sectionTitle: {,'fontSize: 16,'
fontWeight: '600,'';
color: colors.textPrimary,
}
    const marginBottom = spacing.xs}
  }
sectionDescription: {fontSize: 14,
color: colors.textSecondary,
}
    const marginBottom = spacing.md}
  }
categoryContainer: {,}
  const marginBottom = spacing.md}
  }
categoryTitle: {,'fontSize: 14,'
fontWeight: '600,'';
color: colors.textPrimary,
}
    const marginBottom = spacing.sm}
  ;},'
symptomGrid: {,'flexDirection: 'row,'
flexWrap: 'wrap,'
}
    const gap = spacing.sm}
  }
symptomButton: {paddingVertical: spacing.sm,
paddingHorizontal: spacing.md,
borderRadius: 20,
backgroundColor: colors.surface,
borderWidth: 1,
}
    const borderColor = colors.border}
  }
symptomButtonSelected: {backgroundColor: colors.primary,
}
    const borderColor = colors.primary}
  }
symptomText: {fontSize: 14,
}
    const color = colors.textSecondary}
  }
symptomTextSelected: {,'color: colors.white,
}
    const fontWeight = '600'}
  }
painSection: {marginBottom: spacing.lg,
backgroundColor: colors.surface,
borderRadius: 8,
}
    const padding = spacing.md}
  ;},'
painLevelContainer: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
}
    const marginBottom = spacing.sm}
  }
painLevelButton: {width: 30,
height: 30,
borderRadius: 15,
backgroundColor: colors.border,'
justifyContent: 'center,'
}
    const alignItems = 'center'}
  }
painLevelButtonSelected: {,}
  const backgroundColor = colors.primary}
  }
painLevelText: {fontSize: 12,
color: colors.textSecondary,
}
    const fontWeight = '600'}
  }
painLevelTextSelected: {,}
  const color = colors.white}
  ;},'
painLevelLabels: {,'flexDirection: 'row,'
}
    const justifyContent = 'space-between'}
  }
painLevelLabel: {fontSize: 12,
}
    const color = colors.textTertiary}
  }
inputSection: {,}
  const marginBottom = spacing.lg}
  }
inputGroup: {,}
  const marginBottom = spacing.md}
  }
inputLabel: {,'fontSize: 14,'
fontWeight: '600,'';
color: colors.textPrimary,
}
    const marginBottom = spacing.sm}
  }
textInput: {borderWidth: 1,
borderColor: colors.border,
borderRadius: 8,
paddingHorizontal: spacing.md,
paddingVertical: spacing.sm,
fontSize: 14,
color: colors.textPrimary,
}
    const backgroundColor = colors.surface}
  }
multilineInput: {,'height: 80,
}
    const textAlignVertical = 'top'}
  }
lifestyleSection: {,}
  const marginBottom = spacing.lg}
  }
actionContainer: {,}
  const marginVertical = spacing.md}
  }
button: {paddingVertical: spacing.md,
paddingHorizontal: spacing.lg,
borderRadius: 8,
}
    const alignItems = 'center'}
  }
analyzeButton: {,}
  const backgroundColor = colors.primary}
  }
completeButton: {,}
  const backgroundColor = colors.success}
  }
buttonText: {,'fontSize: 16,'
fontWeight: '600,'
}
    const color = colors.white}
  }
resultContainer: {backgroundColor: colors.surface,
borderRadius: 8,
padding: spacing.md,
}
    const marginTop = spacing.md}
  }
resultTitle: {,'fontSize: 18,'
fontWeight: '600,'';
color: colors.textPrimary,
}
    const marginBottom = spacing.md}
  }
analysisSection: {marginBottom: spacing.md,
paddingBottom: spacing.md,
borderBottomWidth: 1,
}
    const borderBottomColor = colors.border}
  }
analysisTitle: {,'fontSize: 16,'
fontWeight: '600,'';
color: colors.textPrimary,
}
    const marginBottom = spacing.sm}
  }
analysisText: {fontSize: 14,
color: colors.textSecondary,
}
    const marginBottom = spacing.xs}
  }
confidenceText: {fontSize: 12,
color: colors.primary,
}
    const fontWeight = '500'}
  }
recommendationSection: {,}
  const marginTop = spacing.sm}
  }
recommendationText: {fontSize: 14,
color: colors.textSecondary,
marginBottom: spacing.xs,);
}
    const lineHeight = 20)}
  ;});
});
''