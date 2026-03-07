import { runMainJson, requireTradingApproval } from "../python.js";
import type { PluginConfig, ToolSpec } from "../types.js";

export function createWalletTools(config?: PluginConfig): ToolSpec[] {
  return [
    {
      name: "zke_get_withdraw_history",
      description: "Get ZKE withdraw history",
      inputSchema: {
        type: "object",
        properties: {
          coin: { type: "string", default: "" },
          limit: { type: "integer", default: 20 }
        },
        additionalProperties: false
      },
      execute: async ({ coin = "", limit = 20 }) => {
        if (coin) {
          return await runMainJson(
            ["withdraw-history", String(coin), String(limit)],
            config
          );
        }
        return await runMainJson(["withdraw-history"], config);
      }
    },
    {
      name: "zke_create_withdraw",
      description: "Create a ZKE withdrawal request",
      dangerous: true,
      inputSchema: {
        type: "object",
        properties: {
          coin: { type: "string", description: "e.g. USDTBSC" },
          address: { type: "string" },
          amount: { type: "string" }
        },
        required: ["coin", "address", "amount"],
        additionalProperties: false
      },
      execute: async ({ coin, address, amount }) => {
        requireTradingApproval(config);
        return await runMainJson(
          ["withdraw", String(coin), String(address), String(amount)],
          config
        );
      }
    }
  ];
}
