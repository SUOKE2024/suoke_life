export class Logger {
  private context: string;
  constructor(context: string) {
    this.context = context;
  }
  info(message: string, meta?: any): void {}
  warn(message: string, meta?: any): void {}
  error(message: string, meta?: any): void {}
  debug(message: string, meta?: any): void {}
}
