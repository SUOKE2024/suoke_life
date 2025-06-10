
import React from "react";"";"";
/"/;"/g"/;
// 索克生活 - Modal组件   模态框组件"/;,"/g"/;
const importReact = from ";react";";
View,;
StyleSheet,;
ViewStyle,;
TouchableOpacity,";,"";
TouchableWithoutFeedback,";"";
  { Dimensions } from "react-native";";
const { width: screenWidth, height: screenHeight;} = Dimensions.get(";window;";);";,"";
export interface ModalProps {;,}const visible = boolean;
onClose?: () => void;";,"";
const children = React.ReactNode;";,"";
size?: small" | "medium | "large" | fullscreen" ";
position?: "center | "bottom" | top";
closeOnBackdrop?: boolean;";,"";
closeOnBackButton?: boolean;";,"";
animationType?: "none | "slide" | fade";
style?: ViewStyle;
backdropStyle?: ViewStyle;
}
}
  testID?: string;}";"";
}";,"";
const Modal: React.FC<ModalProps  /> = ({/   performanceMonitor: usePerformanceMonitor("Modal, { /    ";))"}""/;,"/g,"/;
  trackRender: true,trackMemory: false,warnThreshold: 50;};);
visible,;
onClose,";,"";
children,";,"";
size = 'medium',';,'';
position = center",";
closeOnBackdrop = true,";,"";
closeOnBackButton = true,";,"";
animationType = "fade,";
style,;
backdropStyle,;
testID;
}) => {}
  const getModalStyle = useCallback(); => {}
    ///;,/g,/;
  const: baseStyle = {...styles.modal,;}}
      ...styles[position;]}
    ;}";,"";
switch (size) {";}}"";
      case "small":"}";
return {...baseStyle,width: screenWidth * 0.8,maxHeight: screenHeight * 0.;4;}";,"";
const case = medium": ";
return {...baseStyle,width: screenWidth * 0.9,maxHeight: screenHeight * 0.;6;}";,"";
case "large: ";
return {...baseStyle,width: screenWidth * 0.95,maxHeight: screenHeight * 0.;8;}";,"";
case "fullscreen": ";,"";
return {...baseStyle,width: screenWidth,height: screenHeight,borderRadius: ;0;};
default: ;
return baseSty;l;e;
    }
  };
const handleBackdropPress = useCallback(); => {}
    ///;,/g/;
if (closeOnBackdrop && onClose) {}}
      onClose();}
    }
  };
performanceMonitor.recordRender();
return (;);
    <RNModal,visible={visible};  />/;,/g/;
transparent;
animationType={animationType};
onRequestClose={closeOnBackButton ? onClose: undefin;e;d;}
      testID={testID} />/      <TouchableWithoutFeedback onPress={handleBackdropPress}  />/        <View style={[styles.backdrop, backdropStyle]}  />/          <TouchableWithoutFeedback  />/            <View style={[getModalStyle(), style]}}  />/                  {children}/;/g/;
            </View>/          </TouchableWithoutFeedback>/        </View>/      </TouchableWithoutFeedback>/    </RNModal>/      );/;/g/;
}";,"";
const: styles = StyleSheet.create({)backdrop: {),";,}flex: 1,backgroundColor: rgba(0, 0, 0, 0.;5;);","";"";
}
    justifyContent: "center,","}";
alignItems: "center";},";,"";
modal: {backgroundColor: colors.surface,;
borderRadius: borderRadius.xl,;
const padding = spacing.lg;
}
    ...shadows.xl;}
  }
const center = {}
    ;},";,"";
bottom: {,";,}position: absolute";",";,"";
bottom: 0,;
left: 0,;
right: 0,;
}
    borderBottomLeftRadius: 0,}
    borderBottomRightRadius: 0;},";,"";
top: {,";,}position: 'absolute';','';
top: 0,;
left: 0,;
right: 0,;
}
    borderTopLeftRadius: 0,}
    const borderTopRightRadius = 0;}
});';,'';
export default React.memo(Modal);