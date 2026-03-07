import type { PluginConfig, ToolSpec } from "./types.js";
import { createSpotTools } from "./tools/spot.js";
import { createFuturesTools } from "./tools/futures.js";
import { createWalletTools } from "./tools/wallet.js";

function buildTools(config?: PluginConfig): ToolSpec[] {
  return [
    ...createSpotTools(config),
    ...createFuturesTools(config),
    ...createWalletTools(config),
  ];
}

function getConfig(api: any): PluginConfig {
  return api?.config || api?.getConfig?.() || {};
}

async function registerAllTools(api: any) {
  // 安装/诊断阶段有可能没有 registerTool，直接跳过，避免 CLI 崩溃
  if (!api || typeof api.registerTool !== "function") {
    return;
  }

  const config = getConfig(api);
  const tools = buildTools(config);

  for (const tool of tools) {
    api.registerTool({
      name: tool.name,
      description: tool.description,
      parameters: tool.inputSchema,
      async execute(_id: string, params: Record<string, any>) {
        return await tool.execute(params);
      },
    });
  }
}

// 官方 agent tools 文档示例入口
export default function (api: any) {
  void registerAllTools(api);
}

// 兼容某些 loader/旧检查逻辑
export async function register(api: any) {
  await registerAllTools(api);
}

export async function activate(api: any) {
  await registerAllTools(api);
}
