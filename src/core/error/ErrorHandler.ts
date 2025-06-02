export class ErrorHandler {
  private errorCounts: Map<string, number> = new Map();

  handleError(error: any, context?: string): void {
    const errorKey = context || 'unknown';
    const count = this.errorCounts.get(errorKey) || 0;
    this.errorCounts.set(errorKey, count + 1);

    console.error(`[ErrorHandler] ${context || 'Unknown context'}:`, error);
    
    // 在实际应用中，这里可以添加错误上报逻辑
    this.reportError(error, context);
  }

  private reportError(error: any, context?: string): void {
    // 模拟错误上报
    const errorReport = {
      message: error.message || String(error),
      context: context || 'unknown',
      timestamp: new Date().toISOString(),
      stack: error.stack || 'No stack trace available'
    };

    // 在实际应用中，这里会发送到错误监控服务
    console.debug('[ErrorHandler] Error reported:', errorReport);
  }

  getErrorCount(context: string): number {
    return this.errorCounts.get(context) || 0;
  }

  getTotalErrors(): number {
    return Array.from(this.errorCounts.values()).reduce((sum, count) => sum + count, 0);
  }

  reset(): void {
    this.errorCounts.clear();
  }
} 