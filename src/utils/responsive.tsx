import {  Dimensions  } from "react-native"
const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT ;} = Dimensions.get('window');
export const responsive = {width: (size: number): number => {};
    return size * (SCREEN_WIDTH / 375}
  }
height: (size: number): number => {}
    return size * (SCREEN_HEIGHT / 812}
  }
};
export const breakpoints = {};
  isLandscape: (): boolean => SCREEN_WIDTH > SCREEN_HEIGHT}
};
export { SCREEN_WIDTH, SCREEN_HEIGHT };
export default { responsive, breakpoints };
''