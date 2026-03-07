import { runMainJson, requireTradingApproval } from "../python.js";
import type { PluginConfig, ToolSpec } from "../types.js";

export function createSpotTools(config?: PluginConfig): ToolSpec[] {
  return [
    {
      name: "zke_get_spot_ticker",
      description: "Get ZKE spot ticker for a symbol, e.g. BTCUSDT",
      inputSchema: {
        type: "object",
        properties: {
          symbol: { type: "string" }
        },
        required: ["symbol"],
        additionalProperties: false
      },
      execute: async ({ symbol }) => {
        return await runMainJson(["ticker", String(symbol)], config);
      }
    },
    {
      name: "zke_get_spot_depth",
      description: "Get ZKE spot order book depth",
      inputSchema: {
        type: "object",
        properties: {
          symbol: { type: "string" },
          limit: { type: "integer", default: 20 }
        },
        required: ["symbol"],
        additionalProperties: false
      },
      execute: async ({ symbol, limit = 20 }) => {
        return await runMainJson(
          ["depth", String(symbol), String(limit)],
          config
        );
      }
    },
    {
      name: "zke_get_spot_balance",
      description: "Get ZKE spot balance details for one asset, e.g. USDT",
      inputSchema: {
        type: "object",
        properties: {
          asset: { type: "string" }
        },
        required: ["asset"],
        additionalProperties: false
      },
      execute: async ({ asset }) => {
        return await runMainJson(["account-asset", String(asset)], config);
      }
    },
    {
      name: "zke_get_spot_open_orders",
      description: "Get current ZKE spot open orders for a symbol",
      inputSchema: {
        type: "object",
        properties: {
          symbol: { type: "string" },
          limit: { type: "integer", default: 20 }
        },
        required: ["symbol"],
        additionalProperties: false
      },
      execute: async ({ symbol, limit = 20 }) => {
        return await runMainJson(
          ["open-orders", String(symbol), String(limit)],
          config
        );
      }
    },
    {
      name: "zke_get_spot_my_trades",
      description: "Get recent ZKE spot trades for a symbol",
      inputSchema: {
        type: "object",
        properties: {
          symbol: { type: "string" },
          limit: { type: "integer", default: 20 }
        },
        required: ["symbol"],
        additionalProperties: false
      },
      execute: async ({ symbol, limit = 20 }) => {
        return await runMainJson(
          ["my-trades", String(symbol), String(limit)],
          config
        );
      }
    },
    {
      name: "zke_create_spot_order",
      description: "Create a ZKE spot order",
      dangerous: true,
      inputSchema: {
        type: "object",
        properties: {
          symbol: { type: "string" },
          side: { type: "string", enum: ["BUY", "SELL"] },
          order_type: { type: "string", enum: ["LIMIT", "MARKET"] },
          volume: { type: "string" },
          price: { type: "string" }
        },
        required: ["symbol", "side", "order_type", "volume"],
        additionalProperties: false
      },
      execute: async ({ symbol, side, order_type, volume, price = "" }) => {
        requireTradingApproval(config);
        const args = [
          "create-order",
          String(symbol),
          String(side),
          String(order_type),
          String(volume)
        ];
        if (String(order_type).toUpperCase() === "LIMIT") {
          args.push(String(price));
        }
        return await runMainJson(args, config);
      }
    },
    {
      name: "zke_cancel_spot_order",
      description: "Cancel a ZKE spot order by order id",
      dangerous: true,
      inputSchema: {
        type: "object",
        properties: {
          symbol: { type: "string" },
          order_id: { type: "string" }
        },
        required: ["symbol", "order_id"],
        additionalProperties: false
      },
      execute: async ({ symbol, order_id }) => {
        requireTradingApproval(config);
        return await runMainJson(
          ["cancel-order", String(symbol), String(order_id)],
          config
        );
      }
    }
  ];
}
