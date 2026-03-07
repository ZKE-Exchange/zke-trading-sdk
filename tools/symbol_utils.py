from decimal import Decimal
from typing import Any, Dict, List, Optional

from tools.common import normalize_symbol, normalize_spot_api_symbol, format_decimal_by_precision


class SymbolNotFoundError(Exception):
    pass


class SymbolValidationError(Exception):
    pass


class SpotSymbolRegistry:
    def __init__(self, symbols_payload: Dict[str, Any]):
        raw_symbols = symbols_payload.get("symbols", [])
        self.raw_symbols: List[Dict[str, Any]] = raw_symbols

        self.by_api_symbol: Dict[str, Dict[str, Any]] = {}
        self.by_display_symbol: Dict[str, Dict[str, Any]] = {}
        self.by_base_quote: Dict[str, Dict[str, Any]] = {}

        for item in raw_symbols:
            api_symbol = str(item.get("symbol", "")).lower()
            display_symbol = str(item.get("SymbolName", "")).upper().replace("/", "")
            base_asset = str(item.get("baseAssetName") or item.get("baseAsset") or "").upper()
            quote_asset = str(item.get("quoteAssetName") or item.get("quoteAsset") or "").upper()
            merged = f"{base_asset}{quote_asset}"

            if api_symbol:
                self.by_api_symbol[api_symbol] = item
            if display_symbol:
                self.by_display_symbol[display_symbol] = item
            if merged:
                self.by_base_quote[merged] = item

    def resolve(self, symbol: str) -> Dict[str, Any]:
        raw = symbol.strip()
        lower = raw.lower()
        upper = normalize_symbol(raw)

        if lower in self.by_api_symbol:
            return self.by_api_symbol[lower]
        if upper in self.by_display_symbol:
            return self.by_display_symbol[upper]
        if upper in self.by_base_quote:
            return self.by_base_quote[upper]

        raise SymbolNotFoundError(f"找不到交易对: {symbol}")

    def get_api_symbol(self, symbol: str) -> str:
        item = self.resolve(symbol)
        return str(item["symbol"]).lower()

    def get_display_symbol(self, symbol: str) -> str:
        item = self.resolve(symbol)
        return str(item.get("SymbolName") or item.get("symbol", "")).upper()

    def get_meta(self, symbol: str) -> Dict[str, Any]:
        return self.resolve(symbol)

    def validate_order(self, symbol: str, volume: str, price: Optional[str], order_type: str) -> Dict[str, Any]:
        meta = self.resolve(symbol)

        quantity_precision = int(meta.get("quantityPrecision", 8))
        price_precision = int(meta.get("pricePrecision", 8))
        limit_volume_min = str(meta.get("limitVolumeMin", "0"))
        limit_price_min = str(meta.get("limitPriceMin", "0"))
        limit_amount_min = str(meta.get("limitAmountMin", "0"))

        volume_dec = Decimal(str(volume))
        if volume_dec <= 0:
            raise SymbolValidationError("下单数量必须大于 0。")

        if volume_dec < Decimal(limit_volume_min):
            raise SymbolValidationError(
                f"下单数量过小。当前交易对最小下单量为 {limit_volume_min}。"
            )

        fixed_volume = format_decimal_by_precision(str(volume), quantity_precision)
        if Decimal(fixed_volume) != volume_dec:
            raise SymbolValidationError(
                f"下单数量精度过高。该交易对数量精度为 {quantity_precision} 位。"
            )

        fixed_price = None
        if order_type == "LIMIT":
            if price is None:
                raise SymbolValidationError("LIMIT 订单必须提供 price。")

            price_dec = Decimal(str(price))
            if price_dec <= 0:
                raise SymbolValidationError("订单价格必须大于 0。")

            if price_dec < Decimal(limit_price_min):
                raise SymbolValidationError(
                    f"订单价格过低。当前交易对最小价格为 {limit_price_min}。"
                )

            fixed_price = format_decimal_by_precision(str(price), price_precision)
            if Decimal(fixed_price) != price_dec:
                raise SymbolValidationError(
                    f"订单价格精度过高。该交易对价格精度为 {price_precision} 位。"
                )

            if Decimal(limit_amount_min) > 0:
                amount = Decimal(fixed_price) * Decimal(fixed_volume)
                if amount < Decimal(limit_amount_min):
                    raise SymbolValidationError(
                        f"下单金额过小。当前交易对最小下单金额为 {limit_amount_min}。"
                    )

        return {
            "api_symbol": str(meta["symbol"]).lower(),
            "display_symbol": str(meta.get("SymbolName") or meta.get("symbol", "")).upper(),
            "quantity_precision": quantity_precision,
            "price_precision": price_precision,
            "fixed_volume": fixed_volume,
            "fixed_price": fixed_price,
            "meta": meta,
        }