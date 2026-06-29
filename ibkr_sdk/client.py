from .connection import IBConnection
from .guardrails import Guardrails
from ib_insync import Stock, MarketOrder, LimitOrder

class IBKRClient:
    def __init__(self, host='127.0.0.1', port=7496, config_path="config.json"):
        self.conn = IBConnection(host, port)
        self.guardrails = Guardrails(config_path)

    def connect(self):
        return self.conn.connect()

    def disconnect(self):
        self.conn.disconnect()

    def get_account_summary(self):
        if not self.conn.ib.isConnected():
            return {"error": "Not connected to IBKR"}
        
        summary = self.conn.ib.accountSummary()
        res = {}
        for item in summary:
            if item.tag in ['NetLiquidation', 'TotalCashValue', 'InitMarginReq']:
                res[f"{item.tag}_{item.currency}"] = float(item.value)
        return res

    def get_portfolio(self):
        if not self.conn.ib.isConnected():
            return {"error": "Not connected to IBKR"}
            
        portfolio = self.conn.ib.portfolio()
        positions = []
        for p in portfolio:
            if p.position != 0:
                positions.append({
                    "symbol": p.contract.symbol,
                    "position": p.position,
                    "marketPrice": p.marketPrice,
                    "marketValue": p.marketValue,
                    "averageCost": p.averageCost,
                    "unrealizedPNL": p.unrealizedPNL
                })
        return positions

    def place_order(self, symbol, action, quantity, order_type="MKT", price=0.0):
        if not self.conn.ib.isConnected():
            return {"error": "Not connected to IBKR"}

        if action not in ["BUY", "SELL"]:
            return {"error": "Invalid action. Must be BUY or SELL"}

        # Fetch current price for guardrail validation if not a limit order
        check_price = price
        contract = Stock(symbol, 'SMART', 'USD')
        self.conn.ib.qualifyContracts(contract)

        if order_type == "MKT" or check_price == 0.0:
            tickers = self.conn.ib.reqTickers(contract)
            if tickers and tickers[0].marketPrice() > 0:
                check_price = tickers[0].marketPrice()
            else:
                return {"error": f"Could not fetch current market price for {symbol} to validate order size."}

        # Validate against guardrails
        is_valid, msg = self.guardrails.validate_order(symbol, action, quantity, check_price)
        if not is_valid:
            return {"error": msg}

        # Execute
        if order_type == "MKT":
            order = MarketOrder(action, quantity)
        elif order_type == "LMT":
            order = LimitOrder(action, quantity, price)
        else:
            return {"error": f"Unsupported order type {order_type}"}

        trade = self.conn.ib.placeOrder(contract, order)
        self.conn.ib.sleep(2) # Give it a moment to transmit
        
        return {
            "status": trade.orderStatus.status,
            "orderId": trade.order.orderId,
            "message": "Order placed successfully. Await execution."
        }
