# TWS API Python 指南

本文档整理自 [IBKR TWS API 文档](https://www.interactivebrokers.com/campus/ibkr-api-page/twsapi-doc/)，专注于 Python 编程语言。

## 目录
1.  [简介](#简介)
2.  [注意事项与限制](#注意事项与限制)
3.  [下载 TWS 或 IB Gateway](#下载-tws-或-ib-gateway)
4.  [TWS 设置](#tws-设置)
5.  [下载 TWS API](#下载-tws-api)
6.  [TWS API 基础教程](#tws-api-基础教程)
7.  [第三方 API 平台](#第三方-api-平台)
8.  [特殊配置](#特殊配置)
9.  [故障排除与支持](#故障排除与支持)
10. [架构](#架构)
11. [调用频率限制](#调用频率限制)
12. [连接性](#连接性)
13. [账户与投资组合数据](#账户与投资组合数据)
14. [公告](#公告)
15. [合约详情](#合约详情)
16. [订单管理](#订单管理)
17. [市场数据](#市场数据)
18. [市场扫描器](#市场扫描器)
19. [基本面数据](#基本面数据)
20. [新闻](#新闻)

---

## 简介

TWS API 使得用户可以构建自动化的交易应用程序，利用 IBKR 的高速订单路由和广泛的市场深度。

您可以：
*   从 TWS 获取实时市场数据。
*   将交易订单发送到 IBKR 系统。
*   监控您的订单状态和投资组合。

## 注意事项与限制

### 要求
*   一个 IBKR 交易账户。
*   安装了 Trader Workstation (TWS) 或 IB Gateway。
*   TWS API 的 Python 客户端库。

### 限制
*   **模拟账户**: 模拟账户（Paper Trading Account）与真实账户的运作方式几乎相同，但可能会有一些环境上的差异。
*   **数据订阅**: 模拟账户需要单独订阅市场数据。

## 下载 TWS 或 IB Gateway

您需要安装 TWS 或 IB Gateway。
*   **TWS**: 功能齐全的交易平台，包含图形用户界面。
*   **IB Gateway**: 轻量级的版本，没有完整的交易界面，主要用于 API 连接，消耗更少的资源。

建议在开发和生产环境中使用 IB Gateway。

## TWS 设置

为了使 API 能够连接，您需要在 TWS 或 IB Gateway 中进行配置：

1.  打开 **File -> Global Configuration**。
2.  在左侧面板选择 **API -> Settings**。
3.  勾选 **Enable ActiveX and Socket Clients**。
4.  取消勾选 **Read-Only API**，除非您只需要只读权限。
5.  在 **Socket Port** 中记下端口号。默认情况下，TWS 正式账户为 `7496`，模拟账户为 `7497`。IB Gateway 正式账户为 `4001`，模拟账户为 `4002`。
6.  在 **Trusted IP Addresses** 中，添加 `127.0.0.1` 以允许本地连接。

### 最佳实践配置
*   **永不锁定 TWS**: 在 **Lock and Exit** 设置中，取消勾选 "Auto-lock Trader Workstation"。
*   **内存分配**: 根据需要调整 TWS 的内存分配。
*   **每日/每周重新认证**: 了解 TWS 的自动重启和重新认证机制。

## 下载 TWS API

1.  访问 [TWS API 文档页面](https://www.interactivebrokers.com/campus/ibkr-api-page/twsapi-doc/)。
2.  找到下载部分，下载 TWS API 源代码。
3.  解压后，找到 `source/pythonclient` 目录。

### 在 Windows/Mac/Linux 上安装
安装 Python API 客户端的标准方法是使用 `setup.py`。

1.  打开终端或命令行工具。
2.  导航到 `TWS API/source/pythonclient` 目录。
3.  运行安装命令：
    ```bash
    python setup.py install
    ```

这将把 `ibapi` 包安装到您的 Python 环境中。

## TWS API 基础教程

这是一个基本的 Python 应用结构，用于连接 TWS，请求数据并接收数据。

```python
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, reqId, errorCode, errorString, additionalInfo=''):
        print("Error: ", reqId, " ", errorCode, " ", errorString, " ", additionalInfo)

    def nextValidId(self, orderId: int):
        # We can start sending requests once we have a valid ID.
        self.start()

    def start(self):
        # Requesting market data
        contract = Contract()
        contract.symbol = "AAPL"
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        contract.primaryExchange = "NASDAQ"

        self.reqMktData(10, contract, "", False, False, [])

    def stop(self):
        self.done = True
        self.disconnect()
        
    def tickPrice(self, reqId, tickType, price, attrib):
        print("Tick Price. Ticker Id:", reqId, "tickType:", tickType, "Price:", price)


def main():
    app = TestApp()
    app.connect("127.0.0.1", 7497, 0) # connect to TWS or IB Gateway
    app.run() # EClient's loop

if __name__ == "__main__":
    main()
```

## 第三方 API 平台

除了官方的库，还有一些社区开发的 Python 库提供了更高级的抽象和便利性，例如：
*   `ib_insync`: 一个流行的库，使用异步 (`asyncio`) IO 来简化编程模型。
*   `ib_async`

这些库通常更容易上手，但了解官方 API 的基础原理仍然很重要。

## 特殊配置

### 更新 Python 解释器
当新的 TWS API 版本发布时，您可能需要更新您环境中安装的 `ibapi` 包。

1.  下载最新版本的 TWS API。
2.  导航到 `TWS API/source/pythonclient`。
3.  运行 `python setup.py install`。

这会覆盖旧版本。

## 故障排除与支持

### 日志文件
*   **API 日志**: API 客户端库可以生成日志文件。
*   **启用调试日志**: 在 `EClient` 连接时可以设置。
*   **TWS 日志**: TWS 自身也会生成日志，对于解决连接问题非常有用。

## 架构

API 应用程序通过 TCP Socket 连接到 TWS 或 IB Gateway。您的应用程序是客户端，TWS 是服务器。所有的通信都通过这个 Socket 进行。

### EReader 线程
API 库使用一个独立的线程 (`EReader`) 来读取来自 TWS 的消息。这个线程在后台运行，解析消息并调用 `EWrapper` 中相应的回调函数。这就是为什么您的应用程序需要在一个循环中运行（`app.run()`），以保持 EReader 线程活跃并处理消息。

## 调用频率限制

TWS 对 API 消息的发送频率有限制，以防止系统过载。
*   通常限制为每秒 50 条消息。
*   这个限制是针对发送到 TWS 的消息，而不是接收的消息。
*   如果您发送消息过快，TWS 会暂停处理您的请求，并最终可能断开连接。

## 连接性

### 建立连接
使用 `EClient` 的 `connect()` 方法来建立连接。

```python
app.connect("127.0.0.1", 7497, clientId=0)
```
*   `host`: TWS/IB Gateway 运行的 IP 地址。
*   `port`: TWS/IB Gateway 中配置的 Socket 端口。
*   `clientId`: 唯一的客户端 ID。每个连接到 TWS 的 API 客户端必须有不同的 ID。

### 验证连接
`EClient` 的 `isConnected()` 方法可以检查连接状态。此外，成功连接后，TWS 会调用 `EWrapper` 的 `nextValidId()` 方法。这是您的应用程序可以开始发送请求的信号。

### 断开连接
使用 `disconnect()` 方法来关闭连接。

```python
app.disconnect()
```

## 账户与投资组合数据

### 账户摘要
请求账户摘要可以获取如净值、可用资金等信息。

*   **请求**: `reqAccountSummary`
*   **接收**: `accountSummary` 回调
*   **取消**: `cancelAccountSummary`

```python
# In your EClient/EWrapper class
def start(self):
    # Requesting account summary
    self.reqAccountSummary(9001, "All", "AccountType,NetLiquidation,TotalCashValue,SettledCash,AccruedCash,BuyingPower,EquityWithLoanValue,PreviousDayEquityWithLoanValue,GrossPositionValue,RegTEquity,RegTMargin,SMA,InitMarginReq,MaintMarginReq,AvailableFunds,ExcessLiquidity,Cushion,FullInitMarginReq,FullMaintMarginReq,FullAvailableFunds,FullExcessLiquidity,LookAheadNextChange,LookAheadInitMarginReq,LookAheadMaintMarginReq,LookAheadAvailableFunds,LookAheadExcessLiquidity,HighestSeverity,DayTradesRemaining,Leverage")

def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
    print("AccountSummary. ReqId:", reqId, "Account:", account, "Tag: ", tag, "Value:", value, "Currency:", currency)
```

### 账户更新
订阅账户值的持续更新。

*   **请求**: `reqAccountUpdates`
*   **接收**: `updateAccountValue`, `updatePortfolio`
*   **取消**: `reqAccountUpdates(False, ...)`

```python
# In your EClient/EWrapper class
def start(self):
    # Requesting account updates
    self.reqAccountUpdates(True, "YOUR_ACCOUNT_ID")

def updateAccountValue(self, key: str, val: str, currency: str, accountName: str):
    print("UpdateAccountValue. Key:", key, "Value:", val, "Currency:", currency, "Account:", accountName)

def updatePortfolio(self, contract: Contract, position: float, marketPrice: float, marketValue: float, averageCost: float, unrealizedPNL: float, realizedPNL: float, accountName: str):
    print("UpdatePortfolio. ", "Symbol:", contract.symbol, "SecType:", contract.secType, "Exchange:", contract.exchange, "Position:", position, "MarketPrice:", marketPrice, "MarketValue:", marketValue, "AverageCost:", averageCost, "UnrealizedPNL:", unrealizedPNL, "RealizedPNL:", realizedPNL, "AccountName:", accountName)
```

### 持仓
请求当前所有持仓。

*   **请求**: `reqPositions`
*   **接收**: `position`
*   **取消**: `cancelPositions`

```python
# In your EClient/EWrapper class
def start(self):
    self.reqPositions()

def position(self, account: str, contract: Contract, position: float, avgCost: float):
    print("Position. ", "Account:", account, "Symbol:", contract.symbol, "SecType:", contract.secType, "Currency:", contract.currency, "Position:", position, "Avg cost:", avgCost)

def positionEnd(self):
    print("PositionEnd")
```

### 盈亏 (PnL)
请求单个持仓或整个账户的盈亏。

*   **请求 PnL**: `reqPnL` (账户), `reqPnLSingle` (单个持仓)
*   **接收 PnL**: `pnl`, `pnlSingle`
*   **取消**: `cancelPnL`, `cancelPnLSingle`

```python
# In your EClient/EWrapper class
def start(self):
    # For a single position
    self.reqPnLSingle(17001, "DU111111", "", 265598) # Example with conId

def pnlSingle(self, reqId: int, pos: int, dailyPNL: float, unrealizedPNL: float, realizedPNL: float, value: float):
    super().pnlSingle(reqId, pos, dailyPNL, unrealizedPNL, realizedPNL, value)
    print("Daily PnL Single. ReqId:", reqId, "Position:", pos, "DailyPnL:", dailyPNL, "UnrealizedPNL:", unrealizedPNL, "RealizedPNL:", realizedPNL, "Value:", value)
```

## 公告
订阅 IB 的新闻公告。

*   **请求**: `reqNewsBulletins`
*   **接收**: `updateNewsBulletin`

```python
# In your EClient/EWrapper class
def start(self):
    self.reqNewsBulletins(True)

def updateNewsBulletin(self, msgId: int, msgType: int, newsMessage: str, originExch: str):
    print("News Bulletins. MsgId:", msgId, "Type:", msgType, "Message:", newsMessage, "Exchange of Origin:", originExch)
```

## 合约详情
获取特定合约的详细信息。

*   **请求**: `reqContractDetails`
*   **接收**: `contractDetails`, `contractDetailsEnd`

```python
# In your EClient/EWrapper class
def start(self):
    contract = Contract()
    contract.symbol = "AAPL"
    contract.secType = "STK"
    contract.currency = "USD"
    self.reqContractDetails(10, contract)

def contractDetails(self, reqId: int, contractDetails):
    print("ContractDetails. ReqId:", reqId, "Symbol:", contractDetails.contract.symbol)
```

## 订单管理
这是 API 最核心的功能之一。

### 获取有效订单 ID
在下任何订单之前，必须从 `nextValidId` 回调中获取一个有效的订单 ID。

```python
# In your EWrapper
def nextValidId(self, orderId: int):
    super().nextValidId(orderId)
    self.nextorderId = orderId
    print("The next valid order id is: ", self.nextorderId)
```

### 下单
使用 `placeOrder` 方法。需要一个 `Contract` 对象来定义产品，一个 `Order` 对象来定义订单参数。

```python
from ibapi.order import Order

# ...
# In your EClient/EWrapper class, after getting a valid orderId
def place_new_order(self):
    contract = Contract()
    contract.symbol = "AAPL"
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"

    order = Order()
    order.action = "BUY"
    order.totalQuantity = 100
    order.orderType = "LMT"
    order.lmtPrice = 150.00
    order.orderId = self.nextorderId
    
    self.placeOrder(order.orderId, contract, order)
    self.nextorderId += 1
```

### 订单状态
订单状态通过 `orderStatus` 和 `openOrder` 回调来更新。

*   `openOrder`: 提供订单的完整信息。
*   `orderStatus`: 在订单状态改变时（如 `Submitted`, `Filled`）被调用。

```python
def openOrder(self, orderId, contract, order, orderState):
    print("OpenOrder. ID:", orderId, contract.symbol, contract.secType, "@", contract.exchange, ":", order.action, order.orderType, order.totalQuantity, orderState.status)

def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
    print("OrderStatus. Id:", orderId, "Status:", status, "Filled:", filled, "Remaining:", remaining, "AvgFillPrice:", avgFillPrice)
```

### 取消订单
使用 `cancelOrder` 方法。

```python
self.cancelOrder(order_id_to_cancel)
```

## 市场数据

### 实时数据
请求实时跳动数据（tick-by-tick）。

*   **请求**: `reqMktData`
*   **接收**: `tickPrice`, `tickSize`, `tickString`, 等。
*   **取消**: `cancelMktData`

```python
# In your EClient/EWrapper class
def start(self):
    contract = Contract()
    contract.symbol = "EUR"
    contract.secType = "CASH"
    contract.currency = "GBP"
    contract.exchange = "IDEALPRO"
    self.reqMktData(1, contract, "", False, False, [])

def tickPrice(self, reqId, tickType, price, attrib):
    print("Tick Price. Ticker Id:", reqId, "tickType:", tickType, "Price:", price)

def tickSize(self, reqId, tickType, size):
    print("Tick Size. Ticker Id:", reqId, "tickType:", tickType, "Size:", size)
```

### 历史数据
请求历史K线数据。

*   **请求**: `reqHistoricalData`
*   **接收**: `historicalData`
*   **取消**: 无直接取消函数，请求完成后会自动停止。

```python
from datetime import datetime

# In your EClient/EWrapper class
def start(self):
    contract = Contract()
    contract.symbol = "AAPL"
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"
    
    queryTime = (datetime.today() - timedelta(days=180)).strftime("%Y%m%d %H:%M:%S")

    self.reqHistoricalData(4001, contract, queryTime,
                           "1 M", "1 day", "MIDPOINT", 0, 1, False, [])

def historicalData(self, reqId, bar):
    print("HistoricalData. ReqId:", reqId, "Date:", bar.date, "Open:", bar.open, "High:", bar.high, "Low:", bar.low, "Close:", bar.close, "Volume:", bar.volume, "Count:", bar.barCount, "WAP:", bar.wap)
```

## 市场扫描器
从大量合约中筛选出符合特定标准的合约。

*   **请求**: `reqScannerSubscription`
*   **接收**: `scannerData`
*   **取消**: `cancelScannerSubscription`

```python
from ibapi.scanner import ScannerSubscription

# In your EClient/EWrapper class
def start(self):
    sub = ScannerSubscription()
    sub.instrument = "STK"
    sub.locationCode = "STK.US.MAJOR"
    sub.scanCode = "TOP_PERC_GAIN"
    
    self.reqScannerSubscription(7001, sub, [], [])

def scannerData(self, reqId, rank, contractDetails, distance, benchmark, projection, legsStr):
    print("ScannerData. ReqId:", reqId, "Rank:", rank, "Symbol:", contractDetails.contract.symbol)
```

## 基本面数据
请求公司的基本面数据。

*   **请求**: `reqFundamentalData`
*   **接收**: `fundamentalData`
*   **取消**: `cancelFundamentalData`

```python
# In your EClient/EWrapper class
def start(self):
    contract = Contract()
    contract.symbol = "AAPL"
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"
    
    # Report types: ReportsFinSummary, ReportsOwnership, ReportSnapshot, ReportsFinStatements, etc.
    self.reqFundamentalData(8001, contract, "ReportsFinSummary", [])

def fundamentalData(self, reqId, data):
    print("FundamentalData. ReqId:", reqId, "Data:", data)

```

## 新闻
订阅新闻源。

*   **请求**: `reqNewsProviders`, `reqNewsArticle`
*   **接收**: `newsProviders`, `newsArticle`

```python
# In your EClient/EWrapper class
def start(self):
    # First get provider codes
    self.reqNewsProviders()
    
def newsProviders(self, newsProviders):
    print("NewsProviders: ")
    for provider in newsProviders:
        print("Provider:", provider.providerCode, provider.providerName)
    # Then request an article from a provider
    # self.reqNewsArticle(...)
``` 