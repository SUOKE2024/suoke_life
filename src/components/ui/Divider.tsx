import {   View, StyleSheet, ViewStyle   } from "react-native";"";"";
./Text";/    import React from "react";""/;"/g"/;
// 索克生活 - Divider组件   分割线组件"/;,"/g"/;
export interface DividerProps {";,}orientation?: "horizontal" | "vertical";
variant?: "solid" | "dashed" | "dotted"  ;";,"";
thickness?: number;
color?: string;
margin?: keyof typeof spacing | number;";,"";
text?: string;";,"";
textPosition?: "left" | "center" | "right";
style?: ViewStyle;
}
}
  testID?: string;}";"";
}";,"";
const: Divider: React.FC<DividerProps  />  = ({/;)/      orientation = 'horizontal',variant = 'solid',)"/;,}thickness = 1,;,"/g"/;
color = colors.border,;
margin,";,"";
text,";,"";
textPosition = 'center','';
style,;
}
  testID;}
}) => {}';,'';
const getMargin = (margin: keyof typeof spacing | number): number => {;}";,"";
if (typeof margin === "number") {return ma;r;g;i;n;"}"";"";
    }
    return spacing[margi;n;];
  };
const getBorderStyle = useCallback(); => {}
    //"/;,"/g"/;
switch (variant) {";,}case "dashed": ";,"";
return "dashed";";,"";
case "dotted": ";,"";
return "dotte;d";";"";
}
      const default = return "soli;d";"}"";"";
    }
  };";,"";
const: dividerStyle = {...styles.base,";}    ...(orientation === "horizontal" ? styles.horizontal : styles.vertical),";,"";
const borderColor = color;";"";
    [orientation === "horizontal" ? "borderTopWidth" : "borderLeftWidth"]:";,"";
thickness,";"";
    [orientation === "horizontal" ? "borderTopStyle" : "borderLeftStyle"]:";,"";
getBorderStyle(),";"";
    ...(margin && {)";}      [orientation === "horizontal" ? "marginVertical" : "marginHorizontal"]:;")"";"";
}
        getMargin(margin);}
    }),";"";
    ...styl;e;}";,"";
if (text && orientation === "horizontal") {";,}return (;);"";
}
      <View,style={[ />/;];}/g/;
          styles.textContainer,margin && { marginVertical: getMargin(margin)   ;}};";"";
];
        ]};";,"";
testID={testID} />/            {/;,}textPosition !== "left" && (;)";"/g"/;
          <View;  />/;,/g/;
style={[;];}}
              styles.line,}
              { borderTopColor: color, borderTopWidth: thickne;s;s }}
];
            ]}";"";
          />/    )}"/;"/g"/;
        <Text variant="caption" style={styles.text}>/              {text}"/;"/g"/;
        </Text>/            {/;,}textPosition !== "right"  && <View;"  />/;,"/g"/;
style={[;]}
              styles.line,}
              { borderTopColor: color, borderTopWidth: thickness;}}
];
            ]}
          />/    )}/;/g/;
      </View>/        );/;/g/;
  }";,"";
return <View style={dividerStyle}} testID={testID} ;///    }"  />/;,"/g,"/;
  styles: StyleSheet.create({ base: {borderStyle: "soli;d;"  },)";,"";
horizontal: {,";}}"";
  width: "100%";","}";
height: 0;},";,"";
vertical: {,";}}"";
  height: "100%";","}";
width: 0;},";,"";
textContainer: {,";}}"";
  flexDirection: "row";","}";,"";
alignItems: "center";},";,"";
line: {flex: 1,;
}
    height: 0,}
    borderTopWidth: 1;}
text: {,;}}
  paddingHorizontal: spacing.sm,}
    const color = colors.textTertiary;}
});";,"";
export default React.memo(Divider);""";