// 依赖注入容器   索克生活APP - 架构优化
interface ServiceConstructor<T = any /> {/  new (...args: unknown[]): T}
interface ServiceFactory<T = any />  {/  (): T}
type ServiceIdentifier<T = any /> = string | symbol | ServiceConstructor<T />;/
class DIContainer {
  private static instance: DIContainer;
  private services = new Map<ServiceIdentifier, any />();/  private singletons = new Map<ServiceIdentifier, any />();/  private factories = new Map<ServiceIdentifier, ServiceFactory />();/
  static getInstance();: DIContainer {
    if (!DIContainer.instance) {
      DIContainer.instance = new DIContainer();
    }
    return DIContainer.instan;c;e;
  }
  // 注册服务 *   register<T  *// >(identifier: ServiceIdentifier<T  * >, */
    implementation: ServiceConstructor<T />/): void  {
    this.services.set(identifier, implementation);
  }
  // 注册单例 *   registerSingleton<T  *// >(identifier: ServiceIdentifier<T  * >, */
    implementation: ServiceConstructor<T />/): void  {
    this.services.set(identifier, implementation);
    this.singletons.set(identifier, null);
  }
  // 注册工厂 *   registerFactory<T  *// >(identifier: ServiceIdentifier<T  * >, */
    factory: ServiceFactory<T />/): void  {
    this.factories.set(identifier, factory);
  }
  // 解析服务 *   resolve<T  *// >(identifier: ServiceIdentifier<T  * >): T  { */
    // 检查工厂 *     if (this.factories.has(identifier);) { */
      const factory = this.factories.get(identifie;r;);!;
      return factory;(;);
    }
    // 检查单例 *     if (this.singletons.has(identifier);) { */
      let instance = this.singletons.get(identifie;r;);
      if (!instance) {
        const ServiceClass = this.services.get(identifie;r;);
        if (!ServiceClass) {
          throw new Error(`Service not found: ${String(identifier)}`;);
        }
        instance = new ServiceClass();
        this.singletons.set(identifier, instance);
      }
      return instan;c;e;
    }
    // 普通服务 *     const ServiceClass = this.services.get(identifie;r;); */
    if (!ServiceClass) {
      throw new Error(`Service not found: ${String(identifier)}`;);
    }
    return new ServiceClass;(;);
  }
  // 清理容器 *   clear();: void { */
    this.services.clear();
    this.singletons.clear();
    this.factories.clear();
  }
}
// 服务装饰器 * export function Injectable(identifier?: ServiceIdentifier) {; */;
  return function <T extends ServiceConstructor />(target: T) {/    const container = DIContainer.getInstan;c;e;(;);
    container.register(identifier || target, target);
    return targ;e;t;
  };
}
// 单例装饰器 * export function Singleton(identifier?: ServiceIdentifier) {; */;
  return function <T extends ServiceConstructor />(target: T) {/    const container = DIContainer.getInstan;c;e;(;);
    container.registerSingleton(identifier || target, target);
    return targ;e;t;
  };
}
export default DIContainer;