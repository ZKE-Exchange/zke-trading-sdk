import type { PluginConfig, ToolSpec } from "./types.js";
import { createSpotTools } from "./tools/spot.js";
import { createFuturesTools } from "./tools/futures.js";
import { createWalletTools } from "./tools/wallet.js";

function getConfig(api: any): PluginConfig {
  return api?.config || api?.getConfig?.() || {};
}

function buildTools(config?: PluginConfig): ToolSpec[] {
  return [
    ...createSpotTools(config),
    ...createFuturesTools(config),
    ...createWalletTools(config),
  ];
}

function resolveRegisterFn(api: any): ((tool: any) => any) | null {
  if (typeof api?.registerAgentTool === "function") {
    return api.registerAgentTool.bind(api);
  }

  if (typeof api?.registerTool === "function") {
    return api.registerTool.bind(api);
  }

  if (typeof api?.tools?.registerAgentTool === "function") {
    return api.tools.registerAgentTool.bind(api.tools);
  }

  if (typeof api?.tools?.registerTool === "function") {
    return api.tools.registerTool.bind(api.tools);
  }

  return null;
}

async function registerAllTools(api: any): Promise<void> {
  const registerFn = resolveRegisterFn(api);

  // 很关键：
  // 在 openclaw plugins install / doctor / info 某些阶段，
  // runtime 可能会加载插件，但不给真正的 tool registration API。
  // 这里不能抛错，否则安装过程会炸。
  if (!registerFn) {
    return;
  }

  const config = getConfig(api);
  const tools = buildTools(config);

  for (const tool of tools) {
    await Promise.resolve(
      registerFn({
        name: tool.name,
        description: tool.description,
        // OpenClaw agent tools 文档使用 parameters
        parameters: tool.inputSchema,
        dangerous: !!tool.dangerous,
        async execute(_id: string, params: Record<string, any>) {
          return await tool.execute(params);
        },
      })
    );
  }
}

// 兼容官方 agent-tools 风格
export default function (api: any) {
  void registerAllTools(api);
}

// 兼容某些 loader / checker 仍查找命名导出
export async function register(api: any) {
  await registerAllTools(api);
}

export async function activate(api: any) {
  await registerAllTools(api);
}
