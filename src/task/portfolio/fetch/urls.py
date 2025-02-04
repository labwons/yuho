import pandas as pd


class Urls:

  class _cdn:

    def __init__(self, ticker: str, gb: str):
      self.products = f"http://cdn.fnguide.com/SVO2/json/chart/02/chart_A{ticker}_01_N.json"
      self.multipleBands = f"http://cdn.fnguide.com/SVO2/json/chart/01_06/chart_A{ticker}_D.json"
      self.expenses = f"http://cdn.fnguide.com/SVO2/json/chart/02/chart_A{ticker}_D.json"
      self.profitConsensusAnnual = f"http://cdn.fnguide.com/SVO2/json/chart/07_01/chart_A{ticker}_{gb}_A.json"
      self.profitConsensusQuarter = f"http://cdn.fnguide.com/SVO2/json/chart/07_01/chart_A{ticker}_{gb}_Q.json"
      self.priceConsensus = f"http://cdn.fnguide.com/SVO2/json/chart/01_02/chart_A{ticker}.json"
      self.abstractConsensusRelevant = f"http://cdn.fnguide.com/SVO2/json/chart/07_02/chart_A{ticker}_{gb}_FY1.json"
      self.abstractConsensusForward = f"http://cdn.fnguide.com/SVO2/json/chart/07_02/chart_A{ticker}_{gb}_FY2.json"
      self.foreignRate3Months = f"http://cdn.fnguide.com/SVO2/json/chart/01_01/chart_A{ticker}_3M.json"
      self.foreignRate1Year = f"http://cdn.fnguide.com/SVO2/json/chart/01_01/chart_A{ticker}_1Y.json"
      self.foreignRate3Years = f"http://cdn.fnguide.com/SVO2/json/chart/01_01/chart_A{ticker}_3Y.json"
      self.benchmarkMultiples = f"http://cdn.fnguide.com/SVO2/json/chart/01_04/chart_A{ticker}_{gb}.json"
      self.shares = f"http://cdn.fnguide.com/SVO2/json/chart/08_01/chart_A{ticker}.json"
      self.shortSell = f"http://cdn.fnguide.com/SVO2/json/chart/11_01/chart_A{ticker}_SELL1Y.json"
      self.shortBalance = f"http://cdn.fnguide.com/SVO2/json/chart/11_01/chart_A{ticker}_BALANCE1Y.json"
      return

  def __init__(self, ticker: str):
    self._ticker = ticker
    return

  def __call__(self, assetType: str, page: str, ReportGB: str,
               stkGb: str) -> str:
    return f"http://comp.fnguide.com/SVO2/ASP/{assetType}_{page}.asp?" \
           f"pGB=1&" \
           f"gicode=A{self._ticker}&" \
           f"cID=&" \
           f"MenuYn=Y" \
           f"&ReportGB={ReportGB}" \
           f"&NewMenuID=" \
           f"&stkGb={stkGb}"

  def __repr__(self):
    return f"ticker: {self._ticker}"

  def _get_gb(self) -> str:
    rd = pd.read_html(io=self("SVD", "Main", "", "701"),
                      encoding="utf-8",
                      displayed_only=False)
    try:
      return "B" if rd[11].iloc[1].isnull().sum() > rd[14].iloc[1].isnull(
      ).sum() else "D"
    except IndexError:
      return "D"

  @property
  def gb(self) -> str:
    if not hasattr(self, "__gb__"):
      self.__setattr__("__gb__", self._get_gb())
    return self.__getattribute__("__gb__")

  @property
  def cdn(self):
    if not hasattr(self, "__cdn__"):
      self.__setattr__("__cdn__", self._cdn(self._ticker, self.gb))
    return self.__getattribute__("__cdn__")

  @property
  def snapshot(self) -> str:
    return self("SVD", "Main", "", "701")

  @property
  def corp(self) -> str:
    return self("SVD", "Corp", self.gb, "701")

  @property
  def finance(self) -> str:
    return self("SVD", "Finance", self.gb, "701")

  @property
  def ratio(self) -> str:
    return self("SVD", "FinanceRatio", self.gb, "701")

  @property
  def invest(self) -> str:
    return self("SVD", "Invest", "", "701")

  @property
  def etf(self) -> str:
    return self("etf", "snapshot", "", "770")
