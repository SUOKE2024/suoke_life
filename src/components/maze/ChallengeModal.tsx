import React, { useState, useEffect } from "react"
import {import Icon from "react-native-vector-icons/MaterialIcons";} frommport { Challenge, ChallengeQuestion } from "../../types/maze";
/* ; */
*/
View,
Text,
StyleSheet,
Modal,
ScrollView,
TouchableOpacity,
Dimensions,
Alert,"
Animated,
Image;
} from "react-native;
interface ChallengeModalProps {challenge: Challenge}visible: boolean,
onClose: () => void,
}
}
  onComplete: (score: number) => void}
}
const { width: screenWidth ;} = Dimensions.get('window');
const  ChallengeModal: React.FC<ChallengeModalProps> = ({)challenge}visible,);
onClose,);
}
  onComplete;)}
}) => {}
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)}
  const [selectedAnswers, setSelectedAnswers] = useState<{ [key: number]: number ;}>({});
const [showResults, setShowResults] = useState(false);
const [score, setScore] = useState(0);
const [timeLeft, setTimeLeft] = useState(0);
const [isTimerActive, setIsTimerActive] = useState(false);
  // 动画值
const progressAnim = new Animated.Value(0);
const scoreAnim = new Animated.Value(0);
const currentQuestion = challenge.questions[currentQuestionIndex];
const totalQuestions = challenge.questions.length;
  /* 战 */
  */
useEffect() => {if (visible) {}
      setCurrentQuestionIndex(0)}
      setSelectedAnswers({});
setShowResults(false);
setScore(0);
setTimeLeft(challenge.timeLimit || 300); // 默认5分钟
setIsTimerActive(true);
      // 重置动画
progressAnim.setValue(0);
scoreAnim.setValue(0);
    }
  }, [visible, challenge]);
  /* 器 */
  */
useEffect() => {const let = interval: NodeJS.Timeoutif (isTimerActive && timeLeft > 0) {interval = setInterval() => {}        setTimeLeft(prev => {)if (prev <= 1) {setIsTimerActive(false)handleTimeUp();
}
            return 0}
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => {if (interval) {clearInterval(interval)}
      }
    };
  }, [isTimerActive, timeLeft]);
  /* 理 */
  */
      {}
}
      const onPress = handleSubmit ;};
    ]);
  };
  /* 案 */
  *//,/g,/;
  handleAnswerSelect: useCallback((answerIndex: number) => {setSelectedAnswers(prev => ({...prev,[currentQuestionIndex]: answerIndex;))}
    }));
  };
  /* 题 */
  */
const handleNextQuestion = useCallback(() => {if (currentQuestionIndex < totalQuestions - 1) {setCurrentQuestionIndex(prev => prev + 1);}      // 更新进度动画
Animated.timing(progressAnim, {)toValue: (currentQuestionIndex + 1) / totalQuestions,/,/g,/;
  duration: 300,
}
        const useNativeDriver = false}
      }).start();
    } else {}
      handleSubmit()}
    }
  };
  /* 题 */
  */
const handlePreviousQuestion = useCallback(() => {if (currentQuestionIndex > 0) {setCurrentQuestionIndex(prev => prev - 1);}      // 更新进度动画
Animated.timing(progressAnim, {)toValue: (currentQuestionIndex - 1) / totalQuestions,/,/g,/;
  duration: 300,
}
        const useNativeDriver = false}
      }).start();
    }
  };
  /* 战 */
  */
const handleSubmit = useCallback(() => {setIsTimerActive(false);}    // 计算分数
let correctAnswers = 0;
challenge.questions.forEach(question, index) => {const selectedAnswer = selectedAnswers[index]if (selectedAnswer !== undefined && selectedAnswer === parseInt(String(question.correctAnswer))) {}
        correctAnswers++}
      }
    });
const finalScore = Math.round(correctAnswers / totalQuestions) * 100);
setScore(finalScore);
setShowResults(true);
    // 分数动画
Animated.timing(scoreAnim, {)toValue: finalScore,)duration: 1000,);
}
      const useNativeDriver = false;)}
    }).start();
  };
  /* 战 */
  */
const handleComplete = useCallback(() => {onComplete(score)}
    onClose()}
  };
  /* 间 */
  */
const formatTime = (seconds: number): string => {const minutes = Math.floor(seconds / 60);'/;}}'/g'/;
    const remainingSeconds = seconds % 60;'}
return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;````;```;
  };
  /* 项 */
  */
const renderAnswerOptions = useCallback(() => {if (!currentQuestion) return nullreturn currentQuestion.options.map(option, index) => {const isSelected = selectedAnswers[currentQuestionIndex] === index;)const isCorrect = showResults && index === parseInt(String(currentQuestion.correctAnswer));
const isWrong = showResults && isSelected && index !== parseInt(String(currentQuestion.correctAnswer));
}
      return (<TouchableOpacity;}  />/,)key={index}/g/;
          style={[]styles.answerOption}isSelected && styles.selectedOption,
showResults && isCorrect && styles.correctOption,);
}
            showResults && isWrong && styles.wrongOption;)}
];
          ]}});
onPress={() => !showResults && handleAnswerSelect(index)}
          disabled={showResults}
        >;
          <View style={styles.optionContent}>;
            <View style={ />/;}[]styles.optionIndicator,,/g/;
isSelected && styles.selectedIndicator,
showResults && isCorrect && styles.correctIndicator,
}
              showResults && isWrong && styles.wrongIndicator}
];
            ]}}>;
              <Text style={ />/;}[]styles.optionLetter,,/g/;
isSelected && styles.selectedLetter,
showResults && isCorrect && styles.correctLetter,
}
                showResults && isWrong && styles.wrongLetter}
];
              ]}}>;
                {String.fromCharCode(65 + index)}
              </Text>
            </View>
            <Text style={ />/;}[;];/g/;
}
              styles.optionText,isSelected && styles.selectedText,showResults && isCorrect && styles.correctText,showResults && isWrong && styles.wrongText}
];
            ]}}>;
              {option};
            </Text>;'/;'/g'/;
            {showResults && isCorrect && (;)'}
              <Icon name="check-circle" size={24} color="#4CAF50"  />;"/;"/g"/;
            )};
            {showResults && isWrong && (;)"};
              <Icon name="cancel" size={24} color="#F44336"  />;"/;"/g"/;
            )};
          </View>;
        </TouchableOpacity>;
      );
    });
  };
  /* 面 */
  */
const renderResults = useCallback(() => {const correctCount = Object.keys(selectedAnswers).filter(key => {const questionIndex = parseInt(key);)const selectedAnswer = selectedAnswers[questionIndex];
}
      return selectedAnswer === parseInt(String(challenge.questions[questionIndex].correctAnswer))}
    }).length;
const accuracy = Math.round(correctCount / totalQuestions) * 100);
return (;);
      <View style={styles.resultsContainer}>;
        <View style={styles.scoreDisplay}>;
          <Icon name="emoji-events" size={48} color="#FFD54F"  />;"/;"/g"/;
          <Animated.Text style={[styles.scoreText, {opacity: scoreAnim.interpolate({inputRange: [0, 100],outputRange: [0, 1];)}  />
            }});
          }]}>;
          </Animated.Text>
          <Text style={styles.accuracyText}>;
            正确率: {accuracy}% ({correctCount}/{totalQuestions})
          </Text>
        </View>"
        <View style={styles.resultDetails}>
          <View style={styles.resultItem}>
            <Icon name="timer" size={20} color="#81C784"  />"/;"/g"/;
            <Text style={styles.resultLabel}>用时</Text>
            <Text style={styles.resultValue}>;
              {formatTime(challenge.timeLimit || 300) - timeLeft)}
            </Text>"
          </View>"/;"/g"/;
          <View style={styles.resultItem}>
            <Icon name="star" size={20} color="#FFB74D"  />"/;"/g"/;
            <Text style={styles.resultLabel}>评级</Text>
            <Text style={styles.resultValue}>;
            </Text>
          </View>
        </View>
        <View style={styles.resultActions}>;
          <TouchableOpacity;  />
style={styles.reviewButton}
            onPress={() => setShowResults(false)}
          >
            <Icon name="replay" size={20} color="#2196F3"  />"/;"/g"/;
            <Text style={styles.reviewButtonText}>查看答案</Text>
          </TouchableOpacity>
          <TouchableOpacity;  />
style={styles.completeButton}
            onPress={handleComplete}
          >
            <Icon name="check" size={20} color="#FFFFFF"  />"/;"/g"/;
            <Text style={styles.completeButtonText}>完成挑战</Text>
          </TouchableOpacity>
        </View>
      </View>;
    );
  };
if (!visible) return null;
return (<Modal;"  />/,)visible={visible}","/g"/;
animationType="slide
presentationStyle="pageSheet";
onRequestClose={onClose}
    >;
      <View style={styles.container}>;
        {// 头部}
        <View style={styles.header}>
          <View style={styles.headerLeft}>
            <Icon name="quiz" size={24} color="#FF5722"  />"/;"/g"/;
            <Text style={styles.headerTitle}>健康挑战</Text>
          </View>"
          <View style={styles.headerRight}>
            <View style={styles.timerContainer}>
              <Icon name="access-time" size={16} color={timeLeft < 60 ? "#F44336" : "#4CAF50"}  />"/;"/g"/;
              <Text style={ />/;}[;]/g"/;
}
                styles.timerText,")};
                { color: timeLeft < 60 ? "#F44336" : "#4CAF50" ;}}");
];
              ]}>);
                {formatTime(timeLeft)}
              </Text>"
            </View>"/;"/g"/;
            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <Icon name="close" size={24} color="#666"  />"/;"/g"/;
            </TouchableOpacity>;
          </View>;
        </View>;
        {// 进度条};
        {!showResults && (;)}
          <View style={styles.progressContainer}>;
            <View style={styles.progressBar}>;
              <Animated.View;"  />"
style={[;];";}}"";
];
styles.progressFill,{width: progressAnim.interpolate({inputRange: [0, 1],outputRange: ["0%",100%'];)'}
                    }});
                  }
                ]}
              />
            </View>
            <Text style={styles.progressText}>;
              {currentQuestionIndex + 1} / {totalQuestions}
            </Text>
          </View>
        )}
        {// 内容区域}
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>;
          {showResults ? renderResults() : ()}
            <>}
              {// 挑战信息}
              <View style={styles.challengeInfo}>;
                <Text style={styles.challengeTitle}>{challenge.title}</Text>
                <Text style={styles.challengeDescription}>{challenge.description}</Text>
              </View>
              {// 当前问题}
              {currentQuestion  && <View style={styles.questionContainer}>;
                  <Text style={styles.questionText}>{currentQuestion.question}</Text>
                  {// 问题图片 - 暂时注释掉，因为类型定义中没有imageUrl属性}
                  {/* > *//;}                  )} */}
                  {// 答案选项}
                  <View style={styles.answersContainer}>;
                    {renderAnswerOptions()}
                  </View>
                  {// 解释}
                  {showResults && currentQuestion.explanation  && <View style={styles.explanationContainer}>;
                      <Text style={styles.explanationTitle}>解释</Text>
                      <Text style={styles.explanationText}>;
                        {currentQuestion.explanation}
                      </Text>
                    </View>
                  )}
                </View>
              )}
            < />
          )}
        </ScrollView>
        {// 底部操作栏}
        {!showResults  && <View style={styles.footer}>;
            <TouchableOpacity;  />
style={[styles.navButton, currentQuestionIndex === 0 && styles.disabledButton]}
              onPress={handlePreviousQuestion}
              disabled={currentQuestionIndex === 0}
            >
              <Icon name="chevron-left" size={24} color={currentQuestionIndex === 0 ? "#CCC" : "#4CAF50"}  />"/;"/g"/;
              <Text style={[styles.navButtonText, currentQuestionIndex === 0 && styles.disabledText]}>;
              </Text>
            </TouchableOpacity>
            <TouchableOpacity;  />
style={[]styles.navButton}styles.primaryButton,
}
];
selectedAnswers[currentQuestionIndex] === undefined && styles.disabledButton}
              ]}
              onPress={currentQuestionIndex === totalQuestions - 1 ? handleSubmit : handleNextQuestion}
              disabled={selectedAnswers[currentQuestionIndex] === undefined}
            >;
              <Text style={ />/;}[]styles.navButtonText,,/g/;
styles.primaryButtonText,
}
];
selectedAnswers[currentQuestionIndex] === undefined && styles.disabledText}
              ]}}>;
              </Text>"/;"/g"/;
              <Icon;"  />"
name={currentQuestionIndex === totalQuestions - 1 ? "send" : "chevron-right"}","
size={24}","
color={selectedAnswers[currentQuestionIndex] === undefined ? "#CCC" : "#FFFFFF"}";
              />
            </TouchableOpacity>
          </View>
        )}
      </View>
    </Modal>;
  );
};
const  styles = StyleSheet.create({)container: {,"flex: 1,";
}
    const backgroundColor = '#FFFFFF'}
  ;},'
header: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'';
paddingHorizontal: 16,
paddingVertical: 12,
borderBottomWidth: 1,'
borderBottomColor: '#E0E0E0,'
}
    const backgroundColor = '#F8F9FA'}
  ;},'
headerLeft: {,'flexDirection: 'row,'
}
    const alignItems = 'center'}
  }
headerTitle: {,'fontSize: 18,'
fontWeight: 'bold,'
color: '#FF5722,'
}
    const marginLeft = 8}
  },'
headerRight: {,'flexDirection: 'row,'
}
    const alignItems = 'center'}
  ;},'
timerContainer: {,')''flexDirection: 'row,')'
alignItems: 'center)','
backgroundColor: 'rgba(76, 175, 80, 0.1)',
paddingHorizontal: 8,
paddingVertical: 4,
borderRadius: 12,
}
    const marginRight = 12}
  }
timerText: {,'fontSize: 14,'
fontWeight: 'bold,'';
marginLeft: 4,
}
    const fontFamily = 'monospace'}
  }
closeButton: {,}
  const padding = 8}
  }
progressContainer: {paddingHorizontal: 16,
paddingVertical: 12,
}
    const backgroundColor = '#F8F9FA'}
  }
progressBar: {,'height: 6,'
backgroundColor: '#E0E0E0,'';
borderRadius: 3,'
overflow: 'hidden,'
}
    const marginBottom = 8}
  },'
progressFill: {,'height: '100%,'
backgroundColor: '#4CAF50,'
}
    const borderRadius = 3}
  }
progressText: {,'fontSize: 12,'
color: '#666,'
}
    const textAlign = 'center'}
  }
content: {flex: 1,
}
    const paddingHorizontal = 16}
  }
challengeInfo: {paddingVertical: 16,
borderBottomWidth: 1,
}
    const borderBottomColor = '#F0F0F0'}
  }
challengeTitle: {,'fontSize: 20,'
fontWeight: 'bold,'
color: '#FF5722,'
}
    const marginBottom = 8}
  }
challengeDescription: {,'fontSize: 14,'
color: '#666,'
}
    const lineHeight = 20}
  }
questionContainer: {,}
  const paddingVertical = 16}
  }
questionText: {,'fontSize: 18,'
fontWeight: 'bold,'
color: '#333,'';
lineHeight: 26,
}
    const marginBottom = 16}
  },'
questionImageContainer: {,'alignItems: 'center,'
}
    const marginBottom = 16}
  }
questionImage: {width: screenWidth - 32,
height: 200,
}
    const borderRadius = 8}
  }
answersContainer: {,}
  const marginTop = 8}
  }
answerOption: {,'borderWidth: 2,'
borderColor: '#E0E0E0,'';
borderRadius: 12,
marginBottom: 12,
}
    const backgroundColor = '#FFFFFF'}
  ;},'
selectedOption: {,'borderColor: '#2196F3,'
}
    const backgroundColor = '#E3F2FD'}
  ;},'
correctOption: {,'borderColor: '#4CAF50,'
}
    const backgroundColor = '#E8F5E9'}
  ;},'
wrongOption: {,'borderColor: '#F44336,'
}
    const backgroundColor = '#FFEBEE'}
  ;},'
optionContent: {,'flexDirection: 'row,'
alignItems: 'center,'
}
    const padding = 16}
  }
optionIndicator: {width: 32,
height: 32,
borderRadius: 16,'
backgroundColor: '#F5F5F5,'
justifyContent: 'center,'
alignItems: 'center,'
}
    const marginRight = 12}
  },'
selectedIndicator: {,';}}
  const backgroundColor = '#2196F3'}
  ;},'
correctIndicator: {,';}}
  const backgroundColor = '#4CAF50'}
  ;},'
wrongIndicator: {,';}}
  const backgroundColor = '#F44336'}
  }
optionLetter: {,'fontSize: 16,'
fontWeight: 'bold,'
}
    const color = '#666'}
  ;},'
selectedLetter: {,';}}
  const color = '#FFFFFF'}
  ;},'
correctLetter: {,';}}
  const color = '#FFFFFF'}
  ;},'
wrongLetter: {,';}}
  const color = '#FFFFFF'}
  }
optionText: {flex: 1,
fontSize: 16,'
color: '#333,'
}
    const lineHeight = 22}
  },'
selectedText: {,'color: '#1976D2,'
}
    const fontWeight = '500'}
  ;},'
correctText: {,'color: '#2E7D32,'
}
    const fontWeight = '500'}
  ;},'
wrongText: {,'color: '#C62828,'
}
    const fontWeight = '500'}
  }
explanationContainer: {marginTop: 16,
padding: 16,'
backgroundColor: '#F1F8E9,'
}
    const borderRadius = 8}
  }
explanationTitle: {,'fontSize: 16,'
fontWeight: 'bold,'
color: '#2E7D32,'
}
    const marginBottom = 8}
  }
explanationText: {,'fontSize: 14,'
color: '#388E3C,'
}
    const lineHeight = 20}
  },'
footer: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'';
paddingHorizontal: 16,
paddingVertical: 12,
borderTopWidth: 1,'
borderTopColor: '#E0E0E0,'
}
    const backgroundColor = '#F8F9FA'}
  ;},'
navButton: {,'flexDirection: 'row,'
alignItems: 'center,'';
paddingVertical: 12,
paddingHorizontal: 20,
borderRadius: 8,
borderWidth: 1,
}
    const borderColor = '#4CAF50'}
  ;},'
primaryButton: {,';}}
  const backgroundColor = '#4CAF50'}
  ;},'
disabledButton: {,'borderColor: '#E0E0E0,'
}
    const backgroundColor = '#F5F5F5'}
  }
navButtonText: {,'fontSize: 16,'
color: '#4CAF50,'
fontWeight: '500,'
}
    const marginHorizontal = 4}
  },'
primaryButtonText: {,';}}
  const color = '#FFFFFF'}
  ;},'
disabledText: {,';}}
  const color = '#CCC'}
  }
resultsContainer: {,'paddingVertical: 32,
}
    const alignItems = 'center'}
  ;},'
scoreDisplay: {,'alignItems: 'center,'
}
    const marginBottom = 32}
  }
scoreText: {,'fontSize: 48,'
fontWeight: 'bold,'
color: '#4CAF50,'
}
    const marginVertical = 16}
  }
accuracyText: {,'fontSize: 16,
}
    const color = '#666'}
  ;},'
resultDetails: {,'width: '100%,'
}
    const marginBottom = 32}
  },'
resultItem: {,'flexDirection: 'row,'
alignItems: 'center,'';
paddingVertical: 12,
paddingHorizontal: 16,'
backgroundColor: '#F8F9FA,'';
borderRadius: 8,
}
    const marginBottom = 8}
  }
resultLabel: {,'fontSize: 14,'
color: '#666,'';
marginLeft: 8,
}
    const flex = 1}
  }
resultValue: {,'fontSize: 14,'
fontWeight: 'bold,'
}
    const color = '#333'}
  ;},'
resultActions: {,'flexDirection: 'row,'
justifyContent: 'space-around,'
}
    const width = '100%'}
  ;},'
reviewButton: {,'flexDirection: 'row,'
alignItems: 'center,'';
paddingVertical: 12,
paddingHorizontal: 24,
borderRadius: 8,
borderWidth: 1,
}
    const borderColor = '#2196F3'}
  }
reviewButtonText: {,'fontSize: 16,'
color: '#2196F3,'';
marginLeft: 8,
}
    const fontWeight = '500}
  },completeButton: {,'flexDirection: "row,
}
      alignItems: 'center',paddingVertical: 12,paddingHorizontal: 24,borderRadius: 8,backgroundColor: '#4CAF50}
  },completeButtonText: {fontSize: 16,color: '#FFFFFF',marginLeft: 8,fontWeight: '500}
  };
});
export default ChallengeModal;
