import { runMainJson } from "../python.js";
import type { PluginConfig, ToolSpec } from "../types.js";

export function createFuturesTools(config?: PluginConfig): ToolSpec[] {
  return [
    {
      name: "zke_get_futures_ticker",
      description: "Get ZKE futures ticker, e.g. E-BTC-USDT",
      inputSchema: {
        type: "object",
        properties: {
          symbol: { type: "string" },
        },
        required: ["symbol"],
        additionalProperties: false,
      },
      execute: async ({ symbol }) => {
        return await runMainJson(["futures-ticker", String(symbol)], config);
      },
    },
    {
      name: "zke_get_futures_index",
      description: "Get ZKE futures mark/index price",
      inputSchema: {
        type: "object",
        properties: {
          symbol: { type: "string" },
        },
        required: ["symbol"],
        additionalProperties: false,
      },
      execute: async ({ symbol }) => {
        return await runMainJson(["futures-index", String(symbol)], config);
      },
    },
    {
      name: "zke_get_futures_balance",
      description: "Get ZKE futures account balance for a margin coin",
      inputSchema: {
        type: "object",
        properties: {
          margin_coin: { type: "string", default: "USDT" },
        },
        additionalProperties: false,
      },
      execute: async ({ margin_coin = "USDT" }) => {
        return await runMainJson(["futures-balance", String(margin_coin)], config);
      },
    },
    {
      name: "zke_get_futures_positions",
      description: "Get current ZKE futures positions",
      inputSchema: {
        type: "object",
        properties: {},
        additionalProperties: false,
      },
      execute: async () => {
        return await runMainJson(["futures-positions"], config);
      },
    },
    {
      name: "zke_get_futures_order",
      description: "Query a ZKE futures order by order id",
      inputSchema: {
        type: "object",
        properties: {
          symbol: { type: "string" },
          order_id: { type: "string" },
        },
        required: ["symbol", "order_id"],
        additionalProperties: false,
      },
      execute: async ({ symbol, order_id }) => {
        return await runMainJson(["futures-order", String(symbol), String(order_id)], config);
      },
    },
    {
      name: "zke_get_futures_open_orders",
      description: "Get current ZKE futures open orders",
      inputSchema: {
        type: "object",
        properties: {
          symbol: { type: "string" },
        },
        required: ["symbol"],
        additionalProperties: false,
      },
      execute: async ({ symbol }) => {
        return await runMainJson(["futures-open-orders", String(symbol)], config);
      },
    },
    {
      name: "zke_get_futures_my_trades",
      description: "Get recent ZKE futures trades",
      inputSchema: {
        type: "object",
        properties: {
          symbol: { type: "string" },
          limit: { type: "integer", default: 10 },
        },
        required: ["symbol"],
        additionalProperties: false,
      },
      execute: async ({ symbol, limit = 10 }) => {
        return await runMainJson(["futures-my-trades", String(symbol), String(limit)], config);
      },
    },
    {
