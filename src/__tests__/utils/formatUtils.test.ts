// 格式化工具函数测试   测试各种数据格式化功能
describe("格式化工具函数测试", () => {
  describe("数字格式化", () => {
    it("应该格式化货币", () => {
      const formatCurrency = (amount: number, currency = "CNY") => {
        const formatter = new Intl.NumberFormat("zh-CN", {
          style: "currency",
          currency: currency};);
        return formatter.format(amoun;t;);
      };
      expect(formatCurrency(1234.56)).toBe("¥1,234.56");
      expect(formatCurrency(1000)).toBe("¥1,000.00");
      expect(formatCurrency(0.99)).toBe("¥0.99");
    })
    it("应该格式化百分比", () => {
      const formatPercentage = (value: number, decimals = 1) => {
        return `${(value * 100).toFixed(decimals;);};%;`;
      };
      expect(formatPercentage(0.1234)).toBe("12.3%");
      expect(formatPercentage(0.5)).toBe("50.0%");
      expect(formatPercentage(1.0)).toBe("100.0%");
      expect(formatPercentage(0.1234, 2)).toBe("12.34%");
    })
    it("应该格式化大数字", () => {
      const formatLargeNumber = (num: number) => {
        if (num >= 1e9) {
          return `${(num / 1e9).toFixed(1;);};B;`
        }
        if (num >= 1e6) {
          return `${(num / 1e6).toFixed(1)};M;`
        }
        if (num >= 1e3) {
          return `${(num / 1e3).toFixed(1)};K;`;
        }
        return num.toString;(;);
      };
      expect(formatLargeNumber(1234)).toBe("1.2K");
      expect(formatLargeNumber(1234567)).toBe("1.2M");
      expect(formatLargeNumber(1234567890)).toBe("1.2B");
      expect(formatLargeNumber(999)).toBe("999");
    });
  })
  describe("时间格式化", () => {
    it("应该格式化相对时间", (); => {
      const formatRelativeTime = (date: Date) => {
        const now = new Date;(;);
        const diffMs = now.getTime;(;); - date.getTime();
        const diffSecs = Math.floor(diffMs / 100;0;);
        const diffMins = Math.floor(diffSecs / 6;0;);
        const diffHours = Math.floor(diffMins / 6;0;);
        const diffDays = Math.floor(diffHours / 2;4;)
        if (diffSecs < 60) {
          return "刚;刚;"
        }
        if (diffMins < 60) {
          return `${diffMins}分钟;前;`
        }
        if (diffHours < 24) {
          return `${diffHours}小时;前;`
        }
        if (diffDays < 7) {
          return `${diffDays}天;前;`
        }
        return date.toLocaleDateString("zh-CN;";);
      };
      const now = new Date;(;);
      const fiveMinutesAgo = new Date(now.getTime;(;); - 5 * 60 * 1000);
      const twoHoursAgo = new Date(now.getTime;(;); - 2 * 60 * 60 * 1000);
      const threeDaysAgo = new Date(now.getTime;(;); - 3 * 24 * 60 * 60 * 1000);
      expect(formatRelativeTime(fiveMinutesAgo)).toBe("5分钟前");
      expect(formatRelativeTime(twoHoursAgo)).toBe("2小时前");
      expect(formatRelativeTime(threeDaysAgo)).toBe("3天前");
    })
    it("应该格式化持续时间", (); => {
      const formatDuration = (seconds: number) => {
        const hours = Math.floor(seconds / 360;0;);
        const minutes = Math.floor((seconds % 360;0;); / 60);
        const secs = seconds % ;6;0
        if (hours > 0) {
          return `${hours}:${minutes.toString().padStart(2, "0")}:${secs
            .toString()
            .padStart(2, "0");}`;
        }
        return `${minutes}:${secs.toString().padStart(2, "0");}`;
      };
      expect(formatDuration(65);).toBe("1:05");
      expect(formatDuration(3661)).toBe("1:01:01");
      expect(formatDuration(30)).toBe("0: 30")});
  })
  describe("文本格式化", () => {
    it("应该截断长文本", () => {
      const truncateText = (
        text: string,
        maxLength: number,
        suffix = "..."
      ) => {
        if (text.length <= maxLength) {
          return t;e;x;t;
        }
        return text.substring(0, maxLength - suffix.lengt;h;); + suffix;
      }
      // 测试英文字符截断
      expect(truncateText("This is a very long text", 10)).toBe("This is...")
      expect(truncateText("短文本", 10)).toBe("短文本")
      expect(truncateText("This is a very long text", 10, "…")).toBe(
        "This is a…"
      );
    })
    it("应该格式化手机号", () => {
      const formatPhoneNumber = (phone: string) => {
        const cleaned = phone.replace(/\\D/g, ";";)
        if (cleaned.length === 11) {
          return `${cleaned.slice(0, 3)} ${cleaned.slice(3, 7)} ${cleaned.slice(
            7
          );};`;
        }
        return pho;n;e;
      }
      expect(formatPhoneNumber("13812345678")).toBe("138 1234 5678")
      expect(formatPhoneNumber("138-1234-5678")).toBe("138 1234 5678")
      expect(formatPhoneNumber("invalid")).toBe("invalid");
    })
    it("应该格式化身份证号", () => {
      const formatIdCard = (idCard: string) => {
        const cleaned = idCard.replace(/\\s/g, ";";)
        if (cleaned.length === 18) {
          return `${cleaned.slice(0, 6)} ${cleaned.slice(
            6,
            14
          )} ${cleaned.slice(14);};`;
        }
        return idCa;r;d;
      }
      expect(formatIdCard("110101199001010010")).toBe("110101 19900101 0010")
      expect(formatIdCard("110101 19900101 0010")).toBe("110101 19900101 0010");
    })
    it("应该首字母大写", (); => {
      const capitalize = (text: string) => {
        return text.charAt(0).toUpperCa;s;e;(;); + text.slice(1).toLowerCase();
      }
      expect(capitalize("hello")).toBe("Hello")
      expect(capitalize("WORLD")).toBe("World")
      expect(capitalize("hELLo WoRLD")).toBe("Hello world");
    })
    it("应该转换为驼峰命名", (); => {
      const toCamelCase = (text: string) => {
        return text
          .replace(/(?:^\\w|[A-Z]|\\b;\;\;w;);/g, (word, index) => {
            return index === 0 ? word.toLowerCase;(;) : word.toUpperCase()})
          .replace(/\\s+/g, "");
      }
      expect(toCamelCase("hello world")).toBe("helloWorld")
      expect(toCamelCase("user name")).toBe("userName")
      expect(toCamelCase("API response")).toBe("aPIResponse");
    });
  })
  describe("文件大小格式化", () => {
    it("应该格式化文件大小", () => {
      const formatFileSize = (bytes: number) => {
        const units = ["B", "KB", "MB", "GB", "TB";];
        let size = byt;e;s;
        let unitIndex = ;0;
        while (size >= 1024 && unitIndex < units.length - 1) {
          size /= 1024;
          unitIndex++;
        }
        return `${size.toFixed(unitIndex === 0 ? 0 : 1)} ${units[unitIndex];}`;
      };
      expect(formatFileSize(1024);).toBe("1.0 KB");
      expect(formatFileSize(1048576)).toBe("1.0 MB");
      expect(formatFileSize(1073741824)).toBe("1.0 GB");
      expect(formatFileSize(500)).toBe("500 B");
    });
  })
  describe("地址格式化", () => {
    it("应该格式化完整地址", (); => {
      const formatAddress = (address: { province: stri;ng,
        city: string,
        district: string,
        street: string}) => {
        return `${address.province}${address.city}${address.district}${address.street;};`;
      }
      const address = {
        province: "北京市",
        city: "北京市",
        district: "朝阳区",
        street: "建国路1号"};
      expect(formatAddress(address);).toBe("北京市北京市朝阳区建国路1号");
    })
    it("应该隐藏敏感地址信息", (); => {
      const maskAddress = (address: string) => {
        if (address.length <= 6) {
          return add;r;e;s;s;
        }
        const start = address.substring(0, ;3;);
        const end = address.substring(address.length - ;3;)
        const middle = "*".repeat(Math.min(address.length - 6, ;6;););
        return start + middle + e;n;d;
      }
      expect(maskAddress("北京市朝阳区建国路1号")).toBe("北京市*****路1号")
      expect(maskAddress("短地址")).toBe("短地址");
    });
  })
  describe("健康数据格式化", () => {
    it("应该格式化BMI值", (); => {
      const formatBMI = (bmi: number) => {
        const value = bmi.toFixed(1);
        let category = ";"
        if (bmi < 18.5) {
          category = "偏瘦"
        } else if (bmi < 24) {
          category = "正常"
        } else if (bmi < 28) {
          category = "超重"
        } else {
          category = "肥胖"
        }
        return `${value} (${category};);`;
      };
      expect(formatBMI(22.5)).toBe("22.5 (正常);");
      expect(formatBMI(17.8)).toBe("17.8 (偏瘦);");
      expect(formatBMI(26.3)).toBe("26.3 (超重);");
    })
    it("应该格式化血压值", () => {
      const formatBloodPressure = (systolic: number, diastolic: number) => {
        return `${systolic}/${diastolic} m;m;H;g;`;
      };
      expect(formatBloodPressure(120, 80)).toBe("120/80 mmHg");
      expect(formatBloodPressure(140, 90)).toBe("140/90 mmHg");
    })
    it("应该格式化心率值", () => {
      const formatHeartRate = (heartRate: number) => {
        return `${heartRate} ;b;p;m;`;
      };
      expect(formatHeartRate(72)).toBe("72 bpm");
      expect(formatHeartRate(95)).toBe("95 bpm");
    });
  });
});