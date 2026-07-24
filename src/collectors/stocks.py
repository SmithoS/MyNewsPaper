from __future__ import annotations


def collect(config: dict) -> dict:
    import yfinance as yf

    symbols = config.get("symbols", [])
    if not symbols:
        return {"ok": False, "message": "stocks.json に symbols がありません。", "items": []}

    items = []
    for item in symbols:
        symbol = item["symbol"] if isinstance(item, dict) else item
        label = item.get("label", symbol) if isinstance(item, dict) else symbol
        try:
            hist = yf.Ticker(symbol).history(period="5d", interval="1d", auto_adjust=False)
            hist = hist.dropna(subset=["Close"])
            close = float(hist["Close"].iloc[-1])
            prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else close
            items.append({"ok": True, "symbol": symbol, "label": label, "close": close, "change": close - prev, "change_pct": (close / prev - 1) * 100 if prev else 0})
        except Exception as exc:
            items.append({"ok": False, "symbol": symbol, "label": label, "error": str(exc)})
    return {"ok": True, "items": items}
