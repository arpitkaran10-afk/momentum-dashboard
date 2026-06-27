"""
momentum_pipeline.py  —  Weekly Top-50 Momentum Scanner
S&P 500 + Nasdaq-100  |  12 indicators  |  Groq AI summaries (optional)
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json, logging, os
from datetime import datetime, date, timezone

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

SP500 = [
    "MMM","AOS","ABT","ABBV","ACN","ADBE","AMD","AES","AFL","A","APD","ABNB",
    "AKAM","ALB","ARE","ALGN","ALLE","LNT","ALL","GOOGL","GOOG","MO","AMZN",
    "AMCR","AEE","AAL","AEP","AXP","AIG","AMT","AWK","AMP","AME","AMGN",
    "APH","ADI","AON","APA","AAPL","AMAT","APTV","ACGL","ADM","ANET",
    "AJG","AIZ","T","ATO","ADSK","AZO","AVB","AVY","AXON","BKR","BALL","BAC",
    "BK","BBWI","BAX","BDX","BRK-B","BBY","BIO","TECH","BIIB","BLK","BX",
    "BA","BKNG","BWA","BSX","BMY","AVGO","BR","BRO","BF-B","BLDR","BG",
    "CDNS","CZR","CPT","CPB","COF","CAH","KMX","CCL","CARR","CAT",
    "CBOE","CBRE","CDW","CE","COR","CNC","CNX","CF","CRL","SCHW",
    "CHTR","CVX","CMG","CB","CHD","CI","CINF","CTAS","CSCO","C","CFG",
    "CLX","CME","CMS","KO","CTSH","CL","CMCSA","CAG","COP","ED",
    "STZ","CEG","COO","CPRT","GLW","CPAY","CTVA","CSGP","COST","CTRA","CCI",
    "CSX","CMI","CVS","DHR","DRI","DVA","DE","DAL","XRAY","DVN",
    "DXCM","FANG","DLR","DG","DLTR","D","DPZ","DOV","DHI","DUK",
    "DD","EMN","ETN","EBAY","ECL","EIX","EW","EA","ELV","LLY","EMR","ENPH",
    "ETR","EOG","EPAM","EQT","EFX","EQIX","EQR","ESS","EL","ETSY","EG",
    "EVRG","ES","EXC","EXPE","EXPD","EXR","XOM","FFIV","FDS","FICO","FAST",
    "FRT","FDX","FIS","FITB","FSLR","FE","FMC","F","FTNT","FTV","FOXA",
    "FOX","BEN","FCX","GRMN","IT","GE","GEHC","GEN","GNRC","GD","GIS","GM",
    "GPC","GILD","GS","HAL","HIG","HAS","HCA","DOC","HSIC","HSY","HPE",
    "HLT","HOLX","HD","HON","HRL","HST","HWM","HPQ","HUBB","HUM","HBAN",
    "HII","IBM","IEX","IDXX","ITW","INCY","IR","PODD","INTC","ICE","IFF",
    "IP","INTU","ISRG","IVZ","INVH","IQV","IRM","JBHT","JBL","JKHY",
    "J","JNJ","JCI","JPM","KVUE","KDP","KEY","KEYS","KMB","KIM",
    "KMI","KLAC","KHC","KR","LHX","LH","LRCX","LW","LVS","LDOS","LEN","LNC",
    "LIN","LYV","LKQ","LMT","L","LOW","LULU","LYB","MTB","MPC","MKTX",
    "MAR","MLM","MAS","MA","MTCH","MKC","MCD","MCK","MDT","MRK","META",
    "MET","MTD","MGM","MCHP","MU","MSFT","MAA","MRNA","MHK","MOH","TAP",
    "MDLZ","MPWR","MNST","MCO","MS","MOS","MSI","MSCI","NDAQ","NTAP","NFLX",
    "NEM","NBIX","NKE","NI","NDSN","NSC","NTRS","NOC","NCLH","NRG","NUE",
    "NVDA","NVR","NXPI","ORLY","OXY","ODFL","OMC","ON","OKE","ORCL","OTIS",
    "PCAR","PKG","PANW","PH","PAYX","PAYC","PYPL","PNR","PEP","PFE","PCG",
    "PM","PSX","PNW","PNC","POOL","PPG","PPL","PFG","PG","PGR","PLD",
    "PRU","PEG","PTC","PSA","PHM","QRVO","PWR","QCOM","DGX","RL","RJF","RTX",
    "O","REG","REGN","RF","RSG","RMD","RVTY","ROK","ROL","ROP","ROST","RCL",
    "SPGI","CRM","SBAC","SLB","STX","SRE","NOW","SHW","SPG","SWKS","SJM",
    "SNA","SOLV","SO","LUV","SWK","SBUX","STT","STLD","STE","SYK","SMCI",
    "SYF","SNPS","SYY","TMUS","TROW","TTWO","TPR","TRGP","TGT","TEL","TDY",
    "TFX","TER","TSLA","TXN","TXT","TMO","TJX","TSCO","TT","TDG","TRV",
    "TRMB","TFC","TYL","TSN","USB","UBER","UDR","ULTA","UNP","UAL","UPS",
    "URI","UNH","UHS","VLO","VTR","VLTO","VRSN","VRSK","VZ","VRTX","VTRS",
    "VICI","V","VST","VFC","WRB","GWW","WAB","WMT","DIS","WBD",
    "WM","WAT","WEC","WFC","WELL","WST","WDC","WY","WHR","WMB","WTW",
    "WYNN","XEL","XYL","YUM","ZBRA","ZBH","ZTS",
]

NDX = [
    "AAPL","MSFT","NVDA","AMZN","GOOGL","GOOG","META","TSLA","AVGO","COST",
    "NFLX","AMD","ADBE","QCOM","TXN","AMGN","INTU","INTC","AMAT","MU",
    "ISRG","LRCX","REGN","ADI","MRVL","KLAC","PANW","CRWD","SNPS","CDNS",
    "ASML","MELI","GILD","ABNB","MDLZ","CTAS","ORLY","MNST","PYPL",
    "PCAR","FAST","DXCM","FTNT","ROST","IDXX","PAYX","KHC","CEG","GEHC",
    "ADP","CSCO","BKNG","HON","SBUX","VRTX","CHTR","NXPI","MCHP","LULU",
    "KDP","FANG","DLTR","EXC","XEL","CSGP","VRSK","ODFL",
    "WBD","TTWO","BIIB","ILMN","MTCH","SWKS","DDOG","ZM","OKTA","TEAM",
    "WDAY","TTD","ALGN","CPRT","APP","ARM","ON",
]

ETF = [
    # Broad Market
    "SPY","QQQ","IWM","DIA","VTI","VOO","RSP",
    # Sector SPDRs
    "XLK","XLF","XLE","XLV","XLI","XLY","XLP","XLU","XLB","XLRE","XLC",
    # Style / Factor
    "VUG","VTV","SCHD","MTUM","QUAL","IWF","IWD","IWN",
    # Thematic / Industry
    "ARKK","ARKG","ARKW","ARKF","SOXX","SMH","HACK","CIBR","IGV","BOTZ","TAN","XBI","IBB","KRE","XRT","XHB","IHI",
    # Commodities
    "GLD","IAU","SLV","USO","UNG","DBA",
    # Fixed Income
    "TLT","IEF","SHY","TIP","HYG","LQD","BND","EMB",
    # Real Estate
    "VNQ","IYR",
    # International
    "EEM","EFA","FXI","EWJ","VEA","KWEB",
    # Leveraged
    "TQQQ","SOXL","UPRO","TECL",
]

ETF_SECTOR_MAP = {
    "SPY":"Broad Market","QQQ":"Broad Market","IWM":"Broad Market",
    "DIA":"Broad Market","VTI":"Broad Market","VOO":"Broad Market","RSP":"Broad Market",
    "XLK":"Sector ETF","XLF":"Sector ETF","XLE":"Sector ETF","XLV":"Sector ETF",
    "XLI":"Sector ETF","XLY":"Sector ETF","XLP":"Sector ETF","XLU":"Sector ETF",
    "XLB":"Sector ETF","XLRE":"Sector ETF","XLC":"Sector ETF",
    "VUG":"Style/Factor","VTV":"Style/Factor","SCHD":"Style/Factor","MTUM":"Style/Factor",
    "QUAL":"Style/Factor","IWF":"Style/Factor","IWD":"Style/Factor","IWN":"Style/Factor",
    "ARKK":"Thematic","ARKG":"Thematic","ARKW":"Thematic","ARKF":"Thematic",
    "SOXX":"Thematic","SMH":"Thematic","HACK":"Thematic","CIBR":"Thematic",
    "IGV":"Thematic","BOTZ":"Thematic","TAN":"Thematic","XBI":"Thematic","IBB":"Thematic",
    "KRE":"Thematic","XRT":"Thematic","XHB":"Thematic","IHI":"Thematic",
    "GLD":"Commodities","IAU":"Commodities","SLV":"Commodities","USO":"Commodities",
    "UNG":"Commodities","DBA":"Commodities",
    "TLT":"Fixed Income","IEF":"Fixed Income","SHY":"Fixed Income","TIP":"Fixed Income",
    "HYG":"Fixed Income","LQD":"Fixed Income","BND":"Fixed Income","EMB":"Fixed Income",
    "VNQ":"Real Estate","IYR":"Real Estate",
    "EEM":"International","EFA":"International","FXI":"International",
    "EWJ":"International","VEA":"International","KWEB":"International",
    "TQQQ":"Leveraged","SOXL":"Leveraged","UPRO":"Leveraged","TECL":"Leveraged",
}

ETF_SET = set(ETF)

SECTOR_MAP = {
    "AAPL":"Technology","MSFT":"Technology","NVDA":"Technology","AMD":"Technology",
    "INTC":"Technology","ADBE":"Technology","CRM":"Technology","ORCL":"Technology",
    "CSCO":"Technology","AMAT":"Technology","LRCX":"Technology","KLAC":"Technology",
    "SNPS":"Technology","CDNS":"Technology","MCHP":"Technology","NXPI":"Technology",
    "TXN":"Technology","QCOM":"Technology","ADI":"Technology","MU":"Technology",
    "AVGO":"Technology","IBM":"Technology","HPE":"Technology","HPQ":"Technology",
    "STX":"Technology","WDC":"Technology","SMCI":"Technology","FTNT":"Technology",
    "PANW":"Technology","CRWD":"Technology","ZBRA":"Technology","FFIV":"Technology",
    "MRVL":"Technology","ARM":"Technology","APP":"Technology","DDOG":"Technology",
    "WDAY":"Technology","TEAM":"Technology","TTD":"Technology","OKTA":"Technology",
    "ZM":"Technology","ILMN":"Technology","ON":"Technology","JBL":"Technology",
    "MPWR":"Technology","ANET":"Technology","KEYS":"Technology","CDW":"Technology",
    "AMZN":"Consumer Discretionary","TSLA":"Consumer Discretionary","HD":"Consumer Discretionary",
    "MCD":"Consumer Discretionary","NKE":"Consumer Discretionary","SBUX":"Consumer Discretionary",
    "LOW":"Consumer Discretionary","TJX":"Consumer Discretionary","ROST":"Consumer Discretionary",
    "BKNG":"Consumer Discretionary","ABNB":"Consumer Discretionary","MAR":"Consumer Discretionary",
    "HLT":"Consumer Discretionary","LVS":"Consumer Discretionary","WYNN":"Consumer Discretionary",
    "LULU":"Consumer Discretionary","EBAY":"Consumer Discretionary","ETSY":"Consumer Discretionary",
    "ALGN":"Consumer Discretionary","BBY":"Consumer Discretionary","KMX":"Consumer Discretionary",
    "GOOGL":"Communication Services","GOOG":"Communication Services","META":"Communication Services",
    "NFLX":"Communication Services","DIS":"Communication Services","CMCSA":"Communication Services",
    "T":"Communication Services","VZ":"Communication Services","CHTR":"Communication Services",
    "WBD":"Communication Services","TTWO":"Communication Services","EA":"Communication Services",
    "MTCH":"Communication Services",
    "LLY":"Health Care","UNH":"Health Care","JNJ":"Health Care","ABBV":"Health Care",
    "MRK":"Health Care","ABT":"Health Care","TMO":"Health Care","DHR":"Health Care",
    "BMY":"Health Care","AMGN":"Health Care","GILD":"Health Care","ISRG":"Health Care",
    "REGN":"Health Care","VRTX":"Health Care","DXCM":"Health Care","IDXX":"Health Care",
    "BIIB":"Health Care","MRNA":"Health Care","BSX":"Health Care",
    "SYK":"Health Care","BDX":"Health Care","EW":"Health Care","MDT":"Health Care",
    "CVS":"Health Care","HUM":"Health Care","CI":"Health Care","MOH":"Health Care",
    "HOLX":"Health Care","INCY":"Health Care","NBIX":"Health Care","PODD":"Health Care",
    "IQV":"Health Care","RVTY":"Health Care","A":"Health Care","BIO":"Health Care",
    "TECH":"Health Care","GEHC":"Health Care","ZBH":"Health Care","ZTS":"Health Care",
    "JPM":"Financials","BAC":"Financials","WFC":"Financials","GS":"Financials",
    "MS":"Financials","BLK":"Financials","SCHW":"Financials","AXP":"Financials",
    "V":"Financials","MA":"Financials","PYPL":"Financials","COF":"Financials",
    "BK":"Financials","C":"Financials","USB":"Financials","PNC":"Financials",
    "TFC":"Financials","MTB":"Financials","RF":"Financials","KEY":"Financials",
    "HBAN":"Financials","CFG":"Financials","ICE":"Financials","CME":"Financials",
    "CBOE":"Financials","NDAQ":"Financials","SPGI":"Financials","MCO":"Financials",
    "MSCI":"Financials","FDS":"Financials","MKTX":"Financials","BX":"Financials",
    "AMP":"Financials","LNC":"Financials","PRU":"Financials","MET":"Financials",
    "AFL":"Financials","ALL":"Financials","AIG":"Financials","CB":"Financials",
    "PGR":"Financials","TRV":"Financials","HIG":"Financials","AJG":"Financials",
    "MMC":"Financials","AON":"Financials","WTW":"Financials","AIZ":"Financials",
    "BR":"Financials","IVZ":"Financials","BEN":"Financials","TROW":"Financials",
    "RJF":"Financials","ACGL":"Financials","EG":"Financials","WRB":"Financials",
    "XOM":"Energy","CVX":"Energy","COP":"Energy","EOG":"Energy","SLB":"Energy",
    "OXY":"Energy","MPC":"Energy","PSX":"Energy","VLO":"Energy","FANG":"Energy",
    "HAL":"Energy","BKR":"Energy","APA":"Energy",
    "NEE":"Utilities","DUK":"Utilities","SO":"Utilities","D":"Utilities",
    "AEP":"Utilities","EXC":"Utilities","XEL":"Utilities","CEG":"Utilities",
    "EVRG":"Utilities","ES":"Utilities","PEG":"Utilities","ETR":"Utilities",
    "AEE":"Utilities","LNT":"Utilities","NI":"Utilities","AES":"Utilities",
    "PCG":"Utilities","EIX":"Utilities","ED":"Utilities","WEC":"Utilities",
    "AWK":"Utilities","NRG":"Utilities","VST":"Utilities",
    "COST":"Consumer Staples","WMT":"Consumer Staples","PG":"Consumer Staples",
    "KO":"Consumer Staples","PEP":"Consumer Staples","PM":"Consumer Staples",
    "MO":"Consumer Staples","MDLZ":"Consumer Staples","KHC":"Consumer Staples",
    "GIS":"Consumer Staples","KMB":"Consumer Staples","SYY":"Consumer Staples",
    "CL":"Consumer Staples","MNST":"Consumer Staples","KDP":"Consumer Staples",
    "STZ":"Consumer Staples","TAP":"Consumer Staples","CPB":"Consumer Staples",
    "CAG":"Consumer Staples","SJM":"Consumer Staples","MKC":"Consumer Staples",
    "HSY":"Consumer Staples","KVUE":"Consumer Staples",
    "CHD":"Consumer Staples","CLX":"Consumer Staples","HRL":"Consumer Staples",
    "CAT":"Industrials","HON":"Industrials","GE":"Industrials","UPS":"Industrials",
    "RTX":"Industrials","LMT":"Industrials","BA":"Industrials","GD":"Industrials",
    "NOC":"Industrials","DE":"Industrials","MMM":"Industrials","EMR":"Industrials",
    "ETN":"Industrials","ITW":"Industrials","CMI":"Industrials","PCAR":"Industrials",
    "FAST":"Industrials","CTAS":"Industrials","NSC":"Industrials","CSX":"Industrials",
    "UNP":"Industrials","FDX":"Industrials","ODFL":"Industrials","EXPD":"Industrials",
    "JBHT":"Industrials","PWR":"Industrials","URI":"Industrials","LHX":"Industrials",
    "TDG":"Industrials","TT":"Industrials","CARR":"Industrials","OTIS":"Industrials",
    "ROK":"Industrials","DOV":"Industrials","PH":"Industrials",
    "AME":"Industrials","GNRC":"Industrials","HUBB":"Industrials","NDSN":"Industrials",
    "SNA":"Industrials","SWK":"Industrials","TXT":"Industrials","HII":"Industrials",
    "LDOS":"Industrials","J":"Industrials","TRMB":"Industrials",
    "GWW":"Industrials","WAB":"Industrials","FTV":"Industrials","AXON":"Industrials",
    "RSG":"Industrials","WM":"Industrials","ROL":"Industrials","ROP":"Industrials",
    "CPRT":"Industrials",
    "LIN":"Materials","APD":"Materials","SHW":"Materials","FCX":"Materials",
    "NEM":"Materials","ALB":"Materials","DD":"Materials","EMN":"Materials",
    "NUE":"Materials","STLD":"Materials","MLM":"Materials","PKG":"Materials",
    "IP":"Materials","CE":"Materials","MOS":"Materials","CF":"Materials",
    "FMC":"Materials","BG":"Materials","LYB":"Materials","AMCR":"Materials",
    "AMT":"Real Estate","PLD":"Real Estate","EQIX":"Real Estate","CCI":"Real Estate",
    "SBAC":"Real Estate","DLR":"Real Estate","PSA":"Real Estate","O":"Real Estate",
    "AVB":"Real Estate","EQR":"Real Estate","ARE":"Real Estate","MAA":"Real Estate",
    "CPT":"Real Estate","INVH":"Real Estate","IRM":"Real Estate","VICI":"Real Estate",
    "REG":"Real Estate","FRT":"Real Estate","UDR":"Real Estate","HST":"Real Estate",
    "DOC":"Real Estate","WELL":"Real Estate","VTR":"Real Estate",
}


SECTOR_MAP.update(ETF_SECTOR_MAP)


# ── Enrichment data (drives data.json — no hardcoding in the UI) ─────────────

FULL_NAME_MAP = {
    "AAPL":"Apple Inc.","MSFT":"Microsoft Corporation","NVDA":"NVIDIA Corporation",
    "AMD":"Advanced Micro Devices, Inc.","INTC":"Intel Corporation","ADBE":"Adobe Inc.",
    "CRM":"Salesforce, Inc.","ORCL":"Oracle Corporation","CSCO":"Cisco Systems, Inc.",
    "AMAT":"Applied Materials, Inc.","LRCX":"Lam Research Corporation","KLAC":"KLA Corporation",
    "SNPS":"Synopsys, Inc.","CDNS":"Cadence Design Systems, Inc.",
    "MCHP":"Microchip Technology Incorporated","NXPI":"NXP Semiconductors N.V.",
    "TXN":"Texas Instruments Incorporated","QCOM":"QUALCOMM Incorporated",
    "ADI":"Analog Devices, Inc.","MU":"Micron Technology, Inc.","AVGO":"Broadcom Inc.",
    "IBM":"International Business Machines Corporation",
    "HPE":"Hewlett Packard Enterprise Company","HPQ":"HP Inc.",
    "STX":"Seagate Technology Holdings plc","WDC":"Western Digital Corporation",
    "SMCI":"Super Micro Computer, Inc.","FTNT":"Fortinet, Inc.",
    "PANW":"Palo Alto Networks, Inc.","CRWD":"CrowdStrike Holdings, Inc.",
    "ZBRA":"Zebra Technologies Corporation","FFIV":"F5, Inc.",
    "MRVL":"Marvell Technology, Inc.","ARM":"Arm Holdings plc",
    "APP":"AppLovin Corporation","DDOG":"Datadog, Inc.","WDAY":"Workday, Inc.",
    "TEAM":"Atlassian Corporation","TTD":"The Trade Desk, Inc.","OKTA":"Okta, Inc.",
    "ZM":"Zoom Video Communications, Inc.","ILMN":"Illumina, Inc.",
    "ON":"ON Semiconductor Corporation","JBL":"Jabil Inc.",
    "MPWR":"Monolithic Power Systems, Inc.","ANET":"Arista Networks, Inc.",
    "KEYS":"Keysight Technologies, Inc.","CDW":"CDW Corporation","INTU":"Intuit Inc.",
    "ISRG":"Intuitive Surgical, Inc.",
    "AMZN":"Amazon.com, Inc.","TSLA":"Tesla, Inc.","HD":"The Home Depot, Inc.",
    "MCD":"McDonald's Corporation","NKE":"NIKE, Inc.","SBUX":"Starbucks Corporation",
    "LOW":"Lowe's Companies, Inc.","TJX":"The TJX Companies, Inc.",
    "ROST":"Ross Stores, Inc.","BKNG":"Booking Holdings Inc.","ABNB":"Airbnb, Inc.",
    "MAR":"Marriott International, Inc.","HLT":"Hilton Worldwide Holdings Inc.",
    "LVS":"Las Vegas Sands Corp.","WYNN":"Wynn Resorts, Limited",
    "LULU":"Lululemon Athletica Inc.","EBAY":"eBay Inc.","ETSY":"Etsy, Inc.",
    "ALGN":"Align Technology, Inc.","BBY":"Best Buy Co., Inc.","KMX":"CarMax, Inc.",
    "GOOGL":"Alphabet Inc. (Class A)","GOOG":"Alphabet Inc. (Class C)",
    "META":"Meta Platforms, Inc.","NFLX":"Netflix, Inc.",
    "DIS":"The Walt Disney Company","CMCSA":"Comcast Corporation",
    "T":"AT&T Inc.","VZ":"Verizon Communications Inc.",
    "CHTR":"Charter Communications, Inc.","WBD":"Warner Bros. Discovery, Inc.",
    "TTWO":"Take-Two Interactive Software, Inc.","EA":"Electronic Arts Inc.",
    "MTCH":"Match Group, Inc.",
    "LLY":"Eli Lilly and Company","UNH":"UnitedHealth Group Incorporated",
    "JNJ":"Johnson & Johnson","ABBV":"AbbVie Inc.","MRK":"Merck & Co., Inc.",
    "ABT":"Abbott Laboratories","TMO":"Thermo Fisher Scientific Inc.",
    "DHR":"Danaher Corporation","BMY":"Bristol-Myers Squibb Company",
    "AMGN":"Amgen Inc.","GILD":"Gilead Sciences, Inc.",
    "REGN":"Regeneron Pharmaceuticals, Inc.",
    "VRTX":"Vertex Pharmaceuticals Incorporated","DXCM":"DexCom, Inc.",
    "IDXX":"IDEXX Laboratories, Inc.","BIIB":"Biogen Inc.","MRNA":"Moderna, Inc.",
    "BSX":"Boston Scientific Corporation","SYK":"Stryker Corporation",
    "BDX":"Becton, Dickinson and Company","EW":"Edwards Lifesciences Corporation",
    "MDT":"Medtronic plc","CVS":"CVS Health Corporation","HUM":"Humana Inc.",
    "CI":"The Cigna Group","MOH":"Molina Healthcare, Inc.","HOLX":"Hologic, Inc.",
    "INCY":"Incyte Corporation","NBIX":"Neurocrine Biosciences, Inc.",
    "PODD":"Insulet Corporation","IQV":"IQVIA Holdings Inc.","RVTY":"Revvity, Inc.",
    "A":"Agilent Technologies, Inc.","BIO":"Bio-Rad Laboratories, Inc.",
    "TECH":"Bio-Techne Corporation","GEHC":"GE HealthCare Technologies Inc.",
    "ZBH":"Zimmer Biomet Holdings, Inc.","ZTS":"Zoetis Inc.",
    "JPM":"JPMorgan Chase & Co.","BAC":"Bank of America Corporation",
    "WFC":"Wells Fargo & Company","GS":"The Goldman Sachs Group, Inc.",
    "MS":"Morgan Stanley","BLK":"BlackRock, Inc.",
    "SCHW":"The Charles Schwab Corporation","AXP":"American Express Company",
    "V":"Visa Inc.","MA":"Mastercard Incorporated","PYPL":"PayPal Holdings, Inc.",
    "COF":"Capital One Financial Corporation",
    "BK":"The Bank of New York Mellon Corporation","C":"Citigroup Inc.",
    "USB":"U.S. Bancorp","PNC":"The PNC Financial Services Group, Inc.",
    "TFC":"Truist Financial Corporation","ICE":"Intercontinental Exchange, Inc.",
    "CME":"CME Group Inc.","CBOE":"Cboe Global Markets, Inc.","NDAQ":"Nasdaq, Inc.",
    "SPGI":"S&P Global Inc.","MCO":"Moody's Corporation","MSCI":"MSCI Inc.",
    "BX":"Blackstone Inc.","AMP":"Ameriprise Financial, Inc.",
    "PRU":"Prudential Financial, Inc.","MET":"MetLife, Inc.",
    "AFL":"Aflac Incorporated","ALL":"The Allstate Corporation",
    "AIG":"American International Group, Inc.","CB":"Chubb Limited",
    "PGR":"The Progressive Corporation","TRV":"The Travelers Companies, Inc.",
    "MMC":"Marsh & McLennan Companies, Inc.","AON":"Aon plc",
    "AIZ":"Assurant, Inc.","STT":"State Street Corporation",
    "XOM":"Exxon Mobil Corporation","CVX":"Chevron Corporation",
    "COP":"ConocoPhillips","EOG":"EOG Resources, Inc.","SLB":"SLB",
    "OXY":"Occidental Petroleum Corporation",
    "MPC":"Marathon Petroleum Corporation","PSX":"Phillips 66",
    "VLO":"Valero Energy Corporation","FANG":"Diamondback Energy, Inc.",
    "HAL":"Halliburton Company","BKR":"Baker Hughes Company",
    "NEE":"NextEra Energy, Inc.","DUK":"Duke Energy Corporation",
    "SO":"The Southern Company","CEG":"Constellation Energy Corporation",
    "VST":"Vistra Corp.",
    "COST":"Costco Wholesale Corporation","WMT":"Walmart Inc.",
    "PG":"The Procter & Gamble Company","KO":"The Coca-Cola Company",
    "PEP":"PepsiCo, Inc.","PM":"Philip Morris International Inc.",
    "MO":"Altria Group, Inc.","MDLZ":"Mondelez International, Inc.",
    "KHC":"The Kraft Heinz Company","KDP":"Keurig Dr Pepper Inc.",
    "MNST":"Monster Beverage Corporation",
    "CAT":"Caterpillar Inc.","HON":"Honeywell International Inc.",
    "GE":"GE Aerospace","UPS":"United Parcel Service, Inc.",
    "RTX":"RTX Corporation","LMT":"Lockheed Martin Corporation",
    "BA":"The Boeing Company","GD":"General Dynamics Corporation",
    "NOC":"Northrop Grumman Corporation","DE":"Deere & Company",
    "ETN":"Eaton Corporation plc","CTAS":"Cintas Corporation",
    "NSC":"Norfolk Southern Corporation","CSX":"CSX Corporation",
    "UNP":"Union Pacific Corporation","FDX":"FedEx Corporation",
    "PWR":"Quanta Services, Inc.","URI":"United Rentals, Inc.",
    "LHX":"L3Harris Technologies, Inc.","TDG":"TransDigm Group Incorporated",
    "TT":"Trane Technologies plc","CARR":"Carrier Global Corporation",
    "OTIS":"Otis Worldwide Corporation","AXON":"Axon Enterprise, Inc.",
    "RSG":"Republic Services, Inc.","WM":"Waste Management, Inc.",
    "ROP":"Roper Technologies, Inc.","CPRT":"Copart, Inc.",
    "HWM":"Howmet Aerospace Inc.","ODFL":"Old Dominion Freight Line, Inc.",
    "JBHT":"J.B. Hunt Transport Services, Inc.","GWW":"W.W. Grainger, Inc.",
    "LIN":"Linde plc","SHW":"The Sherwin-Williams Company",
    "FCX":"Freeport-McMoRan Inc.","NEM":"Newmont Corporation",
    "ALB":"Albemarle Corporation","NUE":"Nucor Corporation",
    "STLD":"Steel Dynamics, Inc.","BWA":"BorgWarner Inc.",
    "AMT":"American Tower Corporation","PLD":"Prologis, Inc.",
    "EQIX":"Equinix, Inc.","CCI":"Crown Castle Inc.",
    "DLR":"Digital Realty Trust, Inc.","PSA":"Public Storage",
    "WELL":"Welltower Inc.","HST":"Host Hotels & Resorts, Inc.",
    "ESS":"Essex Property Trust","FRT":"Federal Realty Investment Trust",
    "INVH":"Invitation Homes Inc.",
    "ELV":"Elevance Health, Inc.","GLW":"Corning Incorporated",
    "MGM":"MGM Resorts International","CZR":"Caesars Entertainment, Inc.",
    "NTAP":"NetApp, Inc.","FSLR":"First Solar, Inc.",
    "FDS":"FactSet Research Systems Inc.",
    "ASML":"ASML Holding N.V.","KIM":"Kimco Realty Corporation","SJM":"The J.M. Smucker Company",
    "PFG":"Principal Financial Group, Inc.","MTB":"M&T Bank Corporation","SPG":"Simon Property Group, Inc.",
    "BAX":"Baxter International Inc.","FITB":"Fifth Third Bancorp","AAL":"American Airlines Group Inc.",
    "DAL":"Delta Air Lines, Inc.","CAH":"Cardinal Health, Inc.","CPT":"Camden Property Trust",
    "CFG":"Citizens Financial Group, Inc.","EXPD":"Expeditors International of Washington, Inc.",
    "RL":"Ralph Lauren Corporation","HBAN":"Huntington Bancshares Incorporated","CNC":"Centene Corporation",
}

DESCRIPTION_MAP = {
    "AAPL":"Apple designs and sells consumer electronics, software and services, including the iPhone, Mac, iPad and Apple Watch.",
    "MSFT":"Microsoft develops cloud computing, productivity software, and enterprise platforms including Azure, Windows, and Office 365.",
    "NVDA":"NVIDIA designs GPUs and AI computing platforms powering data centers, gaming, autonomous vehicles, and robotics.",
    "AMD":"Advanced Micro Devices designs high-performance CPUs, GPUs, and AI accelerators for cloud, gaming, and enterprise markets.",
    "INTC":"Intel designs and manufactures semiconductors, including PC processors, data center chips, and network infrastructure solutions.",
    "ADBE":"Adobe provides creative cloud software, digital marketing platforms, and document management tools for professionals and enterprises.",
    "CRM":"Salesforce delivers cloud-based CRM, sales automation, and enterprise AI software to businesses worldwide.",
    "ORCL":"Oracle provides enterprise database software, cloud infrastructure, and business applications to organizations globally.",
    "CSCO":"Cisco Systems designs networking hardware, software, cybersecurity, and collaboration solutions for enterprise and cloud customers.",
    "AMAT":"Applied Materials supplies semiconductor manufacturing equipment, services, and software used in chip fabrication worldwide.",
    "LRCX":"Lam Research develops wafer fabrication equipment used in the production of memory and logic semiconductors.",
    "KLAC":"KLA Corporation provides process control and inspection equipment critical to semiconductor manufacturing yield improvement.",
    "SNPS":"Synopsys offers electronic design automation software and IP products used by chip designers globally.",
    "CDNS":"Cadence Design Systems delivers EDA software, IP, and hardware for semiconductor and electronics design.",
    "MCHP":"Microchip Technology develops microcontrollers, analog semiconductors, and microprocessors for embedded control applications.",
    "NXPI":"NXP Semiconductors provides chips for automotive, industrial, mobile, and IoT applications.",
    "TXN":"Texas Instruments designs and manufactures analog semiconductors and embedded processors used across diverse industries.",
    "QCOM":"Qualcomm develops wireless technology, modem chips, and mobile platforms powering smartphones and connected devices.",
    "ADI":"Analog Devices designs high-performance analog, mixed-signal, and DSP semiconductors for industrial and communications applications.",
    "MU":"Micron Technology manufactures DRAM and NAND flash memory chips for data centers, PCs, and mobile devices.",
    "AVGO":"Broadcom designs semiconductors and infrastructure software for data centers, networking, broadband, and wireless applications.",
    "IBM":"IBM provides hybrid cloud, AI, and consulting services, with platforms including watsonx and Red Hat OpenShift.",
    "HPE":"Hewlett Packard Enterprise delivers enterprise networking, servers, storage, and hybrid cloud solutions to businesses worldwide.",
    "HPQ":"HP Inc. designs and sells personal computers, printers, and related supplies for consumers and businesses.",
    "STX":"Seagate Technology manufactures hard disk drives and storage solutions for cloud, enterprise, and consumer markets.",
    "WDC":"Western Digital produces hard drives, flash storage devices, and enterprise data storage infrastructure.",
    "SMCI":"Super Micro Computer builds high-performance server and storage systems optimized for AI, cloud, and enterprise workloads.",
    "FTNT":"Fortinet provides network security appliances and cloud-based cybersecurity solutions for enterprises and service providers.",
    "PANW":"Palo Alto Networks delivers next-generation cybersecurity platforms including firewalls, cloud security, and AI-driven threat detection.",
    "CRWD":"CrowdStrike provides cloud-native endpoint protection, threat intelligence, and identity security for enterprises.",
    "MRVL":"Marvell Technology designs data infrastructure semiconductors for cloud, 5G, automotive, and enterprise networking applications.",
    "ARM":"Arm Holdings licenses processor architectures and IP used in billions of chips powering smartphones, servers, and IoT devices.",
    "APP":"AppLovin operates an AI-powered advertising platform and mobile gaming portfolio serving app developers and marketers.",
    "DDOG":"Datadog provides cloud monitoring, observability, and security platforms for DevOps and engineering teams.",
    "WDAY":"Workday delivers cloud-based human capital management and financial management software for enterprises.",
    "TEAM":"Atlassian provides collaboration and project management tools including Jira, Confluence, and Trello.",
    "TTD":"The Trade Desk operates a programmatic advertising platform enabling data-driven digital media buying.",
    "OKTA":"Okta provides identity and access management solutions securing authentication for enterprises and developers.",
    "ZM":"Zoom Video Communications offers video conferencing, phone, and collaboration software for businesses and individuals.",
    "ANET":"Arista Networks designs cloud networking switches and software for hyperscale data centers and enterprise cloud.",
    "INTU":"Intuit provides financial software including TurboTax, QuickBooks, and Credit Karma for consumers and small businesses.",
    "ISRG":"Intuitive Surgical develops the da Vinci robotic surgical system enabling minimally invasive surgery worldwide.",
    "AMZN":"Amazon operates e-commerce, cloud computing (AWS), advertising, streaming, and logistics businesses globally.",
    "TSLA":"Tesla designs and manufactures electric vehicles, energy storage systems, and solar products with full self-driving capabilities.",
    "HD":"The Home Depot is the largest home improvement retailer, serving DIY customers and professional contractors.",
    "MCD":"McDonald's is the world's largest fast-food restaurant chain operating and franchising globally.",
    "NKE":"Nike designs, manufactures, and sells athletic footwear, apparel, and equipment worldwide.",
    "SBUX":"Starbucks operates a global coffeehouse chain with retail stores, licensed operations, and consumer packaged goods.",
    "BKNG":"Booking Holdings operates online travel platforms including Booking.com, Priceline, and Kayak.",
    "ABNB":"Airbnb operates an online marketplace for short-term rentals and travel experiences worldwide.",
    "GOOGL":"Alphabet operates Google Search, YouTube, Google Cloud, Android, and a portfolio of AI and moonshot ventures.",
    "META":"Meta Platforms operates Facebook, Instagram, WhatsApp, and develops augmented and virtual reality technologies.",
    "NFLX":"Netflix is a global streaming service offering on-demand TV shows, movies, and original content.",
    "DIS":"Walt Disney operates theme parks, studios, streaming (Disney+), and media networks including ESPN.",
    "LLY":"Eli Lilly develops pharmaceuticals in diabetes, obesity, oncology, and immunology including tirzepatide.",
    "UNH":"UnitedHealth Group provides health insurance, pharmacy benefits, and healthcare services through UnitedHealthcare and Optum.",
    "JNJ":"Johnson & Johnson develops pharmaceuticals, MedTech devices, and over-the-counter consumer health products.",
    "ABBV":"AbbVie is a biopharmaceutical company with leading drugs in immunology, oncology, and neuroscience.",
    "MRK":"Merck develops vaccines, oncology therapies, and animal health products, including Keytruda and Gardasil.",
    "AMGN":"Amgen develops biologics and biosimilars focused on oncology, cardiovascular, and inflammation conditions.",
    "GILD":"Gilead Sciences is a biopharmaceutical company with leading HIV antivirals, hepatitis treatments, and oncology drugs.",
    "REGN":"Regeneron develops monoclonal antibodies in oncology, eye disease, and allergic conditions including Dupixent.",
    "VRTX":"Vertex Pharmaceuticals develops transformative medicines for cystic fibrosis and other serious diseases.",
    "BSX":"Boston Scientific designs minimally invasive medical devices for cardiology, endoscopy, urology, and neuromodulation.",
    "SYK":"Stryker develops orthopedic implants, surgical equipment, neurovascular devices, and hospital medical products.",
    "JPM":"JPMorgan Chase is the largest U.S. bank providing investment banking, commercial banking, and asset management.",
    "BAC":"Bank of America offers consumer banking, corporate and investment banking, and wealth management services.",
    "GS":"Goldman Sachs is a leading global investment bank providing M&A advisory, trading, and asset management.",
    "MS":"Morgan Stanley provides investment banking, equity trading, wealth management, and investment management globally.",
    "BLK":"BlackRock is the world's largest asset manager with over $10 trillion in AUM across index and active strategies.",
    "V":"Visa operates a global digital payment network processing transactions across 200+ countries.",
    "MA":"Mastercard runs a global payments network enabling secure digital transactions between consumers and merchants.",
    "PYPL":"PayPal operates a digital payments platform including PayPal, Venmo, and Braintree for consumers and merchants.",
    "XOM":"ExxonMobil is a major integrated oil and gas company with upstream exploration, refining, and chemicals operations.",
    "CVX":"Chevron is a global energy company engaged in oil and gas exploration, production, refining, and petrochemicals.",
    "COP":"ConocoPhillips is an independent oil and gas exploration and production company operating globally.",
    "NEE":"NextEra Energy is the world's largest generator of renewable energy from wind and solar, plus regulated utilities.",
    "CEG":"Constellation Energy is the largest nuclear power operator in the U.S., supplying clean baseload electricity.",
    "VST":"Vistra is a leading competitive power company with nuclear, natural gas, solar, and battery storage assets.",
    "COST":"Costco Wholesale operates a global chain of membership-based warehouse clubs selling bulk goods at low prices.",
    "WMT":"Walmart operates the world's largest retail chain, including Sam's Club, with growing e-commerce and advertising businesses.",
    "PG":"Procter & Gamble makes consumer goods including Tide, Pampers, Gillette, and Oral-B sold in 180+ countries.",
    "KO":"The Coca-Cola Company produces and distributes beverages including Coke, Sprite, Fanta, and Dasani globally.",
    "PEP":"PepsiCo manufactures and distributes beverages and snack foods including Pepsi, Lay's, Gatorade, and Quaker.",
    "CAT":"Caterpillar manufactures heavy construction equipment, mining machinery, diesel engines, and financial products.",
    "HON":"Honeywell provides industrial automation, aerospace components, performance materials, and building technologies.",
    "GE":"GE Aerospace manufactures commercial and military jet engines, propulsion systems, and aviation services.",
    "RTX":"RTX Corporation makes Pratt & Whitney jet engines, Raytheon defense missiles, and Collins aerospace systems.",
    "LMT":"Lockheed Martin is the world's largest defense contractor, producing the F-35, missiles, and space systems.",
    "BA":"Boeing designs and manufactures commercial jetliners, military aircraft, satellites, and space launch vehicles.",
    "GD":"General Dynamics produces Gulfstream business jets, submarines, combat systems, and IT services for defense.",
    "AXON":"Axon Enterprise develops Taser devices, body cameras, cloud software, and digital evidence management for law enforcement.",
    "LIN":"Linde is the world's largest industrial gases company, supplying oxygen, nitrogen, hydrogen, and specialty gases.",
    "SHW":"Sherwin-Williams manufactures and sells paints, coatings, and related products through a global retail network.",
    "FCX":"Freeport-McMoRan is a leading copper and gold mining company operating large-scale mines in the Americas and Indonesia.",
    "NEM":"Newmont Corporation is the world's leading gold and silver mining company with operations across six continents.",
    "ALB":"Albemarle is the global leader in lithium production for electric vehicle batteries and specialty chemicals.",
    "AMT":"American Tower owns and operates wireless communication towers and data centers globally.",
    "PLD":"Prologis owns and develops industrial logistics real estate including warehouses and distribution centers globally.",
    "EQIX":"Equinix operates a global network of data centers and digital infrastructure connecting enterprises and cloud providers.",
    "WELL":"Welltower invests in senior housing, post-acute care communities, and outpatient medical properties.",
    "ELV":"Elevance Health provides health insurance through Anthem-branded plans plus Carelon health services.",
    "GLW":"Corning Incorporated develops optical fiber, specialty glass, ceramics, and advanced materials for technology applications.",
    "HST":"Host Hotels & Resorts is the largest lodging REIT, owning luxury and upper-upscale hotels across major markets.",
    "MGM":"MGM Resorts International operates casino resorts, hotels, and entertainment venues in Las Vegas and globally.",
    "HUM":"Humana is a leading Medicare Advantage insurer offering health plans, pharmacy benefits, and wellness services.",
    "URI":"United Rentals is the world's largest equipment rental company serving construction, industrial, and infrastructure customers.",
    "NTAP":"NetApp provides hybrid cloud data management, storage systems, and cloud data services for enterprises.",
    "ODFL":"Old Dominion Freight Line is a leading less-than-truckload carrier providing regional and national freight services.",
    "BWA":"BorgWarner designs and manufactures propulsion systems and components for combustion, hybrid, and electric vehicles.",
    "NUE":"Nucor Corporation is the largest U.S. steel producer, manufacturing steel and steel products using electric arc furnaces.",
    "CNC":"Centene Corporation is a managed care organization providing government-sponsored health insurance programs including Medicaid and Medicare.",
    "STLD":"Steel Dynamics is one of the largest U.S. steel producers making flat-rolled, long steel, and steel fabrication products.",
    "JBHT":"J.B. Hunt Transport Services provides intermodal, dedicated contract, truckload, and final-mile logistics across North America.",
    "KMX":"CarMax is the largest used-vehicle retailer in the U.S., operating hundreds of stores with an omnichannel buying experience.",
    "GWW":"W.W. Grainger is a broad-line industrial distribution company supplying maintenance, repair, and operating products to businesses.",
    "MNST":"Monster Beverage Corporation develops, markets, and distributes energy drinks and alternative beverages globally.",
    "FSLR":"First Solar manufactures thin-film photovoltaic solar panels and develops utility-scale solar energy projects in the U.S. and globally.",
    "ILMN":"Illumina develops DNA sequencing and array-based technologies enabling genomic research, clinical diagnostics, and life sciences.",
    "ESS":"Essex Property Trust owns and operates apartment communities in the West Coast markets of California and the Pacific Northwest.",
    "MAR":"Marriott International is the world's largest hotel company, operating and franchising properties across 30+ brands globally.",
    "NBIX":"Neurocrine Biosciences develops treatments for neurological and endocrine diseases including tardive dyskinesia and congenital adrenal hyperplasia.",
    "FFIV":"F5, Inc. provides multi-cloud application security and delivery solutions that protect and optimize applications across any infrastructure.",
    "AIZ":"Assurant provides specialty insurance and risk management products for mobile devices, housing, automotive, and credit markets.",
    "STT":"State Street Corporation provides investment management, custody banking, and financial data services to institutional investors globally.",
    "KDP":"Keurig Dr Pepper is a beverage company owning brands including Dr Pepper, Keurig, Snapple, and 7UP.",
    "ON":"ON Semiconductor designs power management, analog, and sensing semiconductors for automotive, industrial, and IoT applications.",
    "FRT":"Federal Realty Investment Trust owns and redevelops mixed-use retail real estate in high-density coastal markets.",
    "BK":"The Bank of New York Mellon provides custody banking, clearing, investment management, and financial data services globally.",
    "CVS":"CVS Health operates pharmacy retail chains, pharmacy benefit management (Caremark), and Aetna health insurance.",
    "HLT":"Hilton Worldwide Holdings franchises and manages hotels across 18 brands including Hilton, Hampton, and DoubleTree.",
    "CZR":"Caesars Entertainment operates and owns casino resorts across the U.S. including Caesars Palace, Harrah's, and Horseshoe.",
    "FDS":"FactSet Research Systems provides financial data, analytics, and portfolio analysis software to investment professionals.",
    "FDX":"FedEx Corporation provides express delivery, freight transportation, logistics, and supply chain management services worldwide.",
    "ASML":"ASML Holding is the sole manufacturer of extreme ultraviolet lithography machines essential to producing advanced semiconductors.",
    "KIM":"Kimco Realty owns and operates open-air, grocery-anchored shopping centers and mixed-use properties across the U.S.",
    "SJM":"The J.M. Smucker Company makes and sells food and beverage products including Folgers coffee, Jif peanut butter, and Smucker's jams.",
    "PFG":"Principal Financial Group provides retirement, asset management, and insurance solutions to businesses and individuals.",
    "MTB":"M&T Bank Corporation is a regional commercial bank serving retail, business, and institutional customers across the mid-Atlantic and Northeast.",
    "SPG":"Simon Property Group is the largest U.S. retail REIT, owning premium malls, outlets, and mixed-use properties globally.",
    "BAX":"Baxter International provides essential hospital products including IV therapies, renal care devices, and surgical tools.",
    "PNC":"PNC Financial Services is a large U.S. regional bank offering retail banking, corporate banking, and asset management.",
    "FITB":"Fifth Third Bancorp is a regional bank headquartered in Cincinnati providing commercial, retail, and mortgage banking services.",
    "AAL":"American Airlines Group operates one of the world's largest airline networks serving domestic and international routes.",
    "DAL":"Delta Air Lines is a major U.S. carrier operating a global network of passenger and cargo flights.",
    "CAH":"Cardinal Health is a healthcare distribution company supplying pharmaceuticals, medical products, and specialty solutions.",
    "CPT":"Camden Property Trust owns and manages multifamily apartment communities across high-growth U.S. markets.",
    "CFG":"Citizens Financial Group is a regional bank providing consumer, commercial, and wealth management banking services.",
    "EXPD":"Expeditors International of Washington provides global logistics, freight forwarding, and supply chain management services.",
    "INCY":"Incyte Corporation is a biopharmaceutical company focused on oncology and hematology including the JAK inhibitor ruxolitinib.",
    "RL":"Ralph Lauren Corporation designs, markets, and distributes premium lifestyle apparel, accessories, and home products globally.",
    "USB":"U.S. Bancorp is one of the largest U.S. regional banks offering consumer banking, payment services, and wealth management.",
    "HBAN":"Huntington Bancshares is a regional bank serving the Midwest with consumer, commercial, and wealth management banking.",
    "EVRG":"Evergy is a regulated electric utility serving customers in Kansas and Missouri with a growing renewable energy portfolio.",
    "ETSY":"Etsy operates a global online marketplace connecting buyers and sellers of handmade, vintage, and unique goods.",
    "C":"Citigroup is a global bank providing consumer banking, corporate and investment banking, and treasury services in 160+ countries.",
    "MET":"MetLife is a global insurance company offering life, dental, vision, and annuity products to individuals and enterprises.",
}

SUB_SECTOR_MAP = {
    "NVDA":"Semiconductors","AMD":"Semiconductors","INTC":"Semiconductors","AVGO":"Semiconductors",
    "QCOM":"Semiconductors","TXN":"Semiconductors","ADI":"Semiconductors","MU":"Semiconductors",
    "AMAT":"Semiconductor Equipment","LRCX":"Semiconductor Equipment","KLAC":"Semiconductor Equipment",
    "SNPS":"EDA Software","CDNS":"EDA Software","MCHP":"Microcontrollers","NXPI":"Automotive Chips",
    "MRVL":"Data Infrastructure Chips","ARM":"Chip IP & Architecture","ON":"Power Semiconductors",
    "STX":"Data Storage","WDC":"Data Storage","SMCI":"AI Servers","IBM":"Hybrid Cloud & AI",
    "HPE":"Enterprise Networking","HPQ":"PCs & Printers",
    "FTNT":"Network Security","PANW":"Cybersecurity Platform","CRWD":"Endpoint Security","OKTA":"Identity Security",
    "MSFT":"Cloud & Enterprise Software","AAPL":"Consumer Electronics","CRM":"CRM & Cloud Apps",
    "ORCL":"Enterprise Database","CSCO":"Networking","ADBE":"Creative & Marketing Software",
    "INTU":"Financial Software","WDAY":"HR & Finance Cloud","TEAM":"Dev & Collab Tools",
    "APP":"Ad Tech","TTD":"Programmatic Ad Tech","DDOG":"Cloud Observability","ZM":"Video Conferencing",
    "ANET":"Cloud Networking","KEYS":"Electronic Test & Measurement","CDW":"IT Distribution",
    "ZBRA":"Enterprise Mobility","FFIV":"App Delivery & Security","ILMN":"Genomic Sequencing",
    "MPWR":"Power Management ICs","JBL":"Electronics Manufacturing","NTAP":"Enterprise Storage",
    "AMZN":"E-commerce & Cloud","TSLA":"Electric Vehicles","HD":"Home Improvement Retail",
    "MCD":"Quick Service Restaurants","NKE":"Athletic Apparel","SBUX":"Coffee & QSR",
    "LOW":"Home Improvement Retail","TJX":"Off-Price Retail","ROST":"Off-Price Retail",
    "BKNG":"Online Travel","ABNB":"Short-Term Rental Platform","MAR":"Hotels & Lodging",
    "HLT":"Hotels & Lodging","LVS":"Casinos & Gaming","WYNN":"Casinos & Gaming",
    "LULU":"Athletic Apparel","EBAY":"E-commerce Marketplace","ETSY":"Artisan E-commerce",
    "ALGN":"Medical Devices","BBY":"Consumer Electronics Retail","KMX":"Used Auto Retail",
    "MGM":"Casinos & Gaming","CZR":"Casinos & Gaming",
    "GOOGL":"Internet Search & Cloud","GOOG":"Internet Search & Cloud","META":"Social Media",
    "NFLX":"Streaming Media","DIS":"Diversified Media & Parks","CMCSA":"Cable & Streaming",
    "T":"Telecom","VZ":"Telecom","CHTR":"Cable & Broadband","WBD":"Streaming & Studios",
    "TTWO":"Video Games","EA":"Video Games","MTCH":"Social & Dating Apps",
    "LLY":"Large-Cap Pharma","UNH":"Managed Care","JNJ":"Diversified Pharma & MedTech",
    "ABBV":"Immunology & Oncology","MRK":"Large-Cap Pharma","ABT":"Diagnostics & Medical Devices",
    "TMO":"Life Science Tools","DHR":"Life Science Tools","BMY":"Oncology & Immunology",
    "AMGN":"Biologics","GILD":"Antiviral & Oncology","REGN":"Biologics & Ophthalmology",
    "VRTX":"Rare Disease Therapeutics","DXCM":"Continuous Glucose Monitoring",
    "IDXX":"Veterinary Diagnostics","BIIB":"Neurology Therapeutics","MRNA":"mRNA Therapeutics",
    "BSX":"Cardiology Devices","SYK":"Orthopedics & Surgical Robots",
    "BDX":"Diagnostics & Medical Supplies","EW":"Heart Valves","MDT":"Medical Devices",
    "CVS":"Pharmacy & Health Services","HUM":"Medicare Managed Care","CI":"Health Insurance & PBM",
    "ISRG":"Robotic Surgery","IQV":"Clinical Research & Data Analytics","GEHC":"Medical Imaging",
    "ZTS":"Animal Health","A":"Analytical Instruments","PODD":"Insulin Delivery",
    "NBIX":"Neurology Therapeutics","HOLX":"Women's Health Diagnostics","MOH":"Medicaid Managed Care",
    "JPM":"Investment Banking & Retail","BAC":"Retail & Commercial Banking","WFC":"Retail Banking",
    "GS":"Investment Banking","MS":"Wealth & Investment Banking","BLK":"Asset Management",
    "SCHW":"Discount Brokerage","AXP":"Payment Networks & Credit",
    "V":"Payment Networks","MA":"Payment Networks","PYPL":"Digital Payments","COF":"Consumer Credit",
    "BK":"Custody Banking","C":"Global Banking","STT":"Custody Banking",
    "ICE":"Exchange Operator","CME":"Exchange Operator","CBOE":"Options Exchange",
    "NDAQ":"Exchange & Data","SPGI":"Credit Ratings & Data","MCO":"Credit Ratings","MSCI":"Index & Analytics",
    "BX":"Alternative Asset Management","AMP":"Wealth Management",
    "PRU":"Life Insurance","MET":"Life Insurance","AFL":"Supplemental Insurance",
    "ALL":"P&C Insurance","AIG":"P&C Insurance","CB":"P&C Insurance","PGR":"Auto Insurance",
    "TRV":"P&C Insurance","MMC":"Insurance Brokerage","AON":"Insurance Brokerage",
    "AIZ":"Specialty Insurance","FDS":"Financial Data & Analytics",
    "XOM":"Integrated Oil & Gas","CVX":"Integrated Oil & Gas","COP":"E&P Oil & Gas",
    "EOG":"E&P Oil & Gas","SLB":"Oil Field Services","OXY":"E&P Oil & Gas",
    "MPC":"Oil Refining","PSX":"Oil Refining","VLO":"Oil Refining","FANG":"E&P Oil & Gas",
    "HAL":"Oil Field Services","BKR":"Oil Field Services",
    "NEE":"Renewable Energy","DUK":"Regulated Utilities","SO":"Regulated Utilities",
    "CEG":"Nuclear Power","VST":"Competitive Power","EXC":"Regulated Utilities",
    "COST":"Warehouse Club Retail","WMT":"Mass Merchandise Retail","PG":"Household Products",
    "KO":"Non-Alcoholic Beverages","PEP":"Beverages & Snacks","PM":"Tobacco","MO":"Tobacco",
    "KDP":"Beverages & Coffee Systems","MNST":"Energy Beverages",
    "CAT":"Construction & Mining Equipment","HON":"Industrial Conglomerate","GE":"Aerospace Engines",
    "UPS":"Package Delivery","RTX":"Aerospace & Defense","LMT":"Defense Systems",
    "BA":"Commercial & Defense Aircraft","GD":"Defense & Aerospace","NOC":"Defense Systems",
    "DE":"Agricultural Equipment","ETN":"Electrical Components","CTAS":"Uniform Services",
    "NSC":"Rail Freight","CSX":"Rail Freight","UNP":"Rail Freight","FDX":"Express Delivery & Logistics",
    "PWR":"Electrical Contracting","URI":"Equipment Rental","LHX":"Defense Electronics",
    "TDG":"Aerospace Components","TT":"HVAC & Climate","CARR":"HVAC & Refrigeration",
    "OTIS":"Elevators & Escalators","AXON":"Public Safety Technology",
    "RSG":"Waste Management","WM":"Waste Management","ROP":"Industrial Software",
    "CPRT":"Online Auto Auction","HWM":"Aerospace Components",
    "ODFL":"LTL Freight","JBHT":"Intermodal Logistics","GWW":"Industrial Distribution",
    "BWA":"Auto Components","NUE":"Steel Production","STLD":"Steel Production",
    "LIN":"Industrial Gases","SHW":"Paints & Coatings","FCX":"Copper Mining",
    "NEM":"Gold Mining","ALB":"Lithium Production",
    "AMT":"Cell Tower REIT","PLD":"Industrial REIT","EQIX":"Data Center REIT",
    "CCI":"Cell Tower REIT","DLR":"Data Center REIT","PSA":"Self-Storage REIT",
    "WELL":"Senior Housing REIT","INVH":"Single-Family Rental REIT",
    "HST":"Hotel REIT","ESS":"Apartment REIT","FRT":"Retail REIT",
    "FSLR":"Solar Energy",
    "ELV":"Managed Care","GLW":"Specialty Glass & Fiber",
    "CNC":"Medicaid Managed Care",
    "ASML":"Semiconductor Lithography","KIM":"Retail REIT","SJM":"Packaged Foods",
    "PFG":"Insurance & Retirement","MTB":"Regional Banking","SPG":"Mall REIT",
    "BAX":"Hospital Products","PNC":"Regional Banking","FITB":"Regional Banking",
    "AAL":"Airlines","DAL":"Airlines","CAH":"Healthcare Distribution",
    "CPT":"Apartment REIT","CFG":"Regional Banking","EXPD":"Freight Forwarding",
    "INCY":"Oncology Therapeutics","RL":"Luxury Apparel","USB":"Regional Banking",
    "HBAN":"Regional Banking","EVRG":"Regulated Utilities",
}


def get_universe():
    tickers = list(set(SP500 + NDX + ETF))
    sp_set = set(SP500); ndx_set = set(NDX)
    tags = {}
    for t in tickers:
        if t in ETF_SET:                   tags[t] = "ETF"
        elif t in sp_set and t in ndx_set: tags[t] = "S&P500+NDX"
        elif t in sp_set:                  tags[t] = "S&P500"
        else:                              tags[t] = "Nasdaq-100"
    log.info(f"Universe: {len(tickers)} unique tickers ({len(ETF)} ETFs included)")
    return tickers, tags


def download_prices(tickers, period="1y"):
    log.info(f"Downloading {period} OHLCV for {len(tickers)} tickers...")
    # Download in batches of 100 to avoid timeouts
    all_close, all_volume, all_high, all_low = {}, {}, {}, {}
    batch_size = 100
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        log.info(f"  Batch {i//batch_size+1}/{(len(tickers)-1)//batch_size+1} ({len(batch)} tickers)...")
        try:
            raw = yf.download(batch, period=period, interval="1d",
                              auto_adjust=True, progress=False,
                              group_by="ticker", threads=True)
            if len(batch) == 1:
                t = batch[0]
                if "Close" in raw.columns:
                    all_close[t] = raw["Close"]
                    all_volume[t] = raw["Volume"]
                    all_high[t] = raw["High"]
                    all_low[t] = raw["Low"]
            else:
                for t in batch:
                    try:
                        all_close[t]  = raw[t]["Close"]
                        all_volume[t] = raw[t]["Volume"]
                        all_high[t]   = raw[t]["High"]
                        all_low[t]    = raw[t]["Low"]
                    except: pass
        except Exception as e:
            log.warning(f"Batch failed: {e}")
    close  = pd.DataFrame(all_close)
    volume = pd.DataFrame(all_volume)
    high   = pd.DataFrame(all_high)
    low    = pd.DataFrame(all_low)
    log.info(f"Downloaded {len(close.columns)} tickers successfully")
    return close, volume, high, low

    


def rsi(s, p=14):
    d = s.diff()
    g = d.clip(lower=0).ewm(alpha=1/p, adjust=False).mean()
    l = (-d.clip(upper=0)).ewm(alpha=1/p, adjust=False).mean()
    return float((100 - 100/(1 + g/l.replace(0, np.nan))).iloc[-1])


def stochastic(hi, lo, cl, k=14, d=3):
    lowest  = lo.rolling(k).min()
    highest = hi.rolling(k).max()
    pct_k = 100 * (cl - lowest) / (highest - lowest + 1e-9)
    pct_d = pct_k.rolling(d).mean()
    return round(float(pct_k.iloc[-1]), 1), round(float(pct_d.iloc[-1]), 1)


def adx(hi, lo, cl, p=14):
    tr  = pd.concat([hi-lo,(hi-cl.shift()).abs(),(lo-cl.shift()).abs()],axis=1).max(axis=1)
    dmp = hi.diff().clip(lower=0)
    dmm = (-lo.diff().clip(upper=0))
    atr_s = tr.ewm(alpha=1/p, adjust=False).mean()
    dip   = 100 * dmp.ewm(alpha=1/p, adjust=False).mean() / atr_s
    din   = 100 * dmm.ewm(alpha=1/p, adjust=False).mean() / atr_s
    dx    = 100 * (dip-din).abs() / (dip+din+1e-9)
    return round(float(dx.ewm(alpha=1/p, adjust=False).mean().iloc[-1]), 1)


def bollinger_pct(s, p=20):
    ma  = s.rolling(p).mean()
    std = s.rolling(p).std()
    val = (s.iloc[-1]-(ma-2*std).iloc[-1]) / ((4*std).iloc[-1]+1e-9) * 100
    return round(float(val), 1)


def vwap_breakout(hi, lo, cl, vol, lookback=20):
    """
    VWAP + Breakout Quality.
    Returns:
        vwap_pct   : % price is above/below VWAP (+ = above)
        breakout_q : 0–100 score. Combines distance above VWAP,
                     volume surge, and price near recent high.
    """
    tp   = (hi + lo + cl) / 3           # typical price
    vwap = (tp * vol).rolling(lookback).sum() / vol.rolling(lookback).sum()
    vwap_val   = float(vwap.iloc[-1])
    price      = float(cl.iloc[-1])
    vwap_pct   = round((price - vwap_val) / (vwap_val + 1e-9) * 100, 2)

    # breakout quality components (each 0–1)
    above_vwap   = 1.0 if vwap_pct > 0 else 0.0
    vol_surge    = min(float(vol.rolling(5).mean().iloc[-1] /
                             (vol.rolling(20).mean().iloc[-1] + 1e-9)), 3.0) / 3.0
    high_range   = float(hi.rolling(lookback).max().iloc[-1])
    near_high    = max(0.0, 1.0 - (high_range - price) / (high_range + 1e-9) * 10)
    near_high    = min(near_high, 1.0)

    breakout_q = round((above_vwap * 0.4 + vol_surge * 0.35 + near_high * 0.25) * 100, 1)
    return vwap_pct, breakout_q


def momentum_divergence(cl, lookback=14):
    """
    RSI Divergence detector.
    Compares price slope vs RSI slope over recent `lookback` bars.
    Returns:
        div_score : -1 = bearish divergence, 0 = no divergence, +1 = bullish divergence
        div_label : human-readable string
    """
    if len(cl) < lookback + 14:
        return 0, "N/A"

    # RSI series (last 2*lookback bars for stability)
    window = cl.iloc[-(lookback * 2):]
    d   = window.diff()
    g   = d.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
    l   = (-d.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
    rsi_s = 100 - 100 / (1 + g / l.replace(0, np.nan))

    price_recent = cl.iloc[-lookback:]
    rsi_recent   = rsi_s.iloc[-lookback:]

    price_slope = float(np.polyfit(range(lookback), price_recent.values, 1)[0])
    rsi_slope   = float(np.polyfit(range(lookback), rsi_recent.fillna(50).values, 1)[0])

    if price_slope > 0 and rsi_slope < -0.1:
        return -1, "Bearish Div"      # price up, RSI weakening → caution
    elif price_slope < 0 and rsi_slope > 0.1:
        return  1, "Bullish Div"      # price down, RSI strengthening → opportunity
    else:
        return  0, "No Div"


def obv_slope(cl, vol, lookback=20):
    """
    On-Balance Volume slope.
    Returns:
        obv_trend : 'Rising', 'Falling', 'Flat'
        obv_score : percentile-like 0–100 (higher = stronger rising OBV)
    """
    direction = np.sign(cl.diff().fillna(0))
    obv       = (direction * vol).cumsum()
    obv_recent = obv.iloc[-lookback:]
    slope      = float(np.polyfit(range(lookback), obv_recent.values, 1)[0])

    # Normalise slope relative to mean OBV magnitude
    mean_obv   = float(obv_recent.abs().mean()) + 1e-9
    norm_slope = slope / mean_obv   # roughly -1 to +1

    obv_score  = round(min(max((norm_slope + 1) / 2 * 100, 0), 100), 1)
    if norm_slope > 0.02:   trend = "Rising"
    elif norm_slope < -0.02: trend = "Falling"
    else:                    trend = "Flat"
    return trend, obv_score


def compute_indicators(close, volume, high, low):
    results = []
    for ticker in close.columns:
        try:
            c = close[ticker].dropna()
            print(
                f"{ticker} | Latest Candle: {c.index[-1]} | Close: {round(float(c.iloc[-1]),2)}"
            )
            v = volume[ticker].dropna()
            h = high[ticker].dropna()
            l = low[ticker].dropna()
            if len(c) < 200: continue

            price = round(float(c.iloc[-1]), 2)
            r1w   = round((c.iloc[-1]/c.iloc[-6]   -1)*100, 2) if len(c) >= 6 else 0.0
            r1m   = round((c.iloc[-1]/c.iloc[-22]  -1)*100, 2)
            r3m   = round((c.iloc[-1]/c.iloc[-66]  -1)*100, 2)
            r6m   = round((c.iloc[-1]/c.iloc[-126] -1)*100, 2)

            # MTD: from first trading day of current month
            try:
                month_start = c[(c.index.year == c.index[-1].year) & (c.index.month == c.index[-1].month)].iloc[0]
                r_mtd = round((c.iloc[-1]/month_start -1)*100, 2)
            except: r_mtd = 0.0

            # YTD: from first trading day of current year
            try:
                year_start = c[c.index.year == c.index[-1].year].iloc[0]
                r_ytd = round((c.iloc[-1]/year_start -1)*100, 2)
            except: r_ytd = 0.0

            # 1Y: 252 trading days back
            try:
                r_1y = round((c.iloc[-1]/c.iloc[-252] -1)*100, 2) if len(c) >= 252 else round((c.iloc[-1]/c.iloc[0] -1)*100, 2)
            except: r_1y = 0.0
            rsi_v = round(rsi(c), 1)

            ema12 = c.ewm(span=12, adjust=False).mean()
            ema26 = c.ewm(span=26, adjust=False).mean()
            macd_hist   = float((ema12-ema26-(ema12-ema26).ewm(span=9,adjust=False).mean()).iloc[-1])
            macd_signal = "BUY" if macd_hist > 0 else "SELL"

            stoch_k, stoch_d = stochastic(h, l, c)
            adx_v   = adx(h, l, c)
            bb_pct  = bollinger_pct(c)

            tr      = pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
            atr_pct = round(float(tr.ewm(span=14,adjust=False).mean().iloc[-1])/price*100, 2)
            roc10   = round((c.iloc[-1]/c.iloc[-11]-1)*100, 2)
            vol_ratio = round(float(v.rolling(5).mean().iloc[-1]/v.rolling(20).mean().iloc[-1]),2)

            ma50  = float(c.rolling(50).mean().iloc[-1])
            ma200 = float(c.rolling(200).mean().iloc[-1])
            high52w = float(c.rolling(252).max().iloc[-1])
            pct_from_high = round((price-high52w)/high52w*100, 1)

            spark_raw = c.iloc[-30:].values.tolist()
            mn, mx = min(spark_raw), max(spark_raw)
            spark = [round((spv-mn)/(mx-mn+1e-9)*100,1) for spv in spark_raw]

            # ── NEW INDICATORS ────────────────────────────────────────────
            vwap_pct_v, breakout_q_v = vwap_breakout(h, l, c, v)
            div_score_v, div_label_v = momentum_divergence(c)
            obv_trend_v, obv_score_v = obv_slope(c, v)
            # ─────────────────────────────────────────────────────────────

            results.append({
                "ticker":ticker,"sector":SECTOR_MAP.get(ticker,"Other"),"price":price,
                "ret_1w":r1w,"ret_1m":r1m,"ret_3m":r3m,"ret_6m":r6m,"ret_mtd":r_mtd,"ret_ytd":r_ytd,"ret_1y":r_1y,
                "rsi":rsi_v,"stoch_k":stoch_k,"stoch_d":stoch_d,
                "adx":adx_v,"bb_pct":bb_pct,"atr_pct":atr_pct,"roc10":roc10,
                "macd_signal":macd_signal,"macd_hist":round(macd_hist,4),
                "vol_ratio":vol_ratio,"pct_from_high":pct_from_high,
                "above_ma50":bool(price>ma50),"above_ma200":bool(price>ma200),
                "ma50":round(ma50,2),"ma200":round(ma200,2),"sparkline":spark,
                # ── new indicators ──
                "vwap_pct":vwap_pct_v, "breakout_quality":breakout_q_v,
                "div_score":div_score_v, "div_label":div_label_v,
                "obv_trend":obv_trend_v, "obv_score":obv_score_v,
                "rel_strength_sector": 0.0,   # filled in post-pass below
                "asset_type": "etf" if ticker in ETF_SET else "stock",
            })
        except Exception as e:
            log.debug(f"Skip {ticker}: {e}")

    log.info(f"{len(results)} tickers with valid indicators")
    df_out = pd.DataFrame(results)

    # ── Relative Strength vs Sector (post-pass) ───────────────────────────
    # rel_strength_sector = stock 3-month return minus median 3-month return
    # of all valid stocks in the same sector. Positive = outperforming sector.
    if not df_out.empty:
        sector_medians = df_out.groupby("sector")["ret_3m"].median()
        df_out["rel_strength_sector"] = df_out.apply(
            lambda row: round(row["ret_3m"] - sector_medians.get(row["sector"], 0.0), 2),
            axis=1
        )
    # ─────────────────────────────────────────────────────────────────────
    return df_out


def score_and_rank(df, top_n=50):
    df = df.copy()
    df["s_1m"]  = df["ret_1m"].rank(pct=True)*100
    df["s_3m"]  = df["ret_3m"].rank(pct=True)*100
    df["s_6m"]  = df["ret_6m"].rank(pct=True)*100
    df["s_rsi"] = df["rsi"].rank(pct=True)*100
    df["s_adx"] = df["adx"].rank(pct=True)*100
    df["s_vol"] = df["vol_ratio"].rank(pct=True)*100
    df["s_roc"] = df["roc10"].rank(pct=True)*100
    df["s_breakout"] = df["breakout_quality"].rank(pct=True)*100
    df["s_obv"]      = df["obv_score"].rank(pct=True)*100
    df["s_rs"]       = df["rel_strength_sector"].rank(pct=True)*100
    # div_score: +1 bullish div → bonus, -1 bearish div → penalty
    df["s_div"]      = df["div_score"].map({1: 75, 0: 50, -1: 25})
    df["momentum_score"] = (
        df["s_1m"]*0.20 + df["s_3m"]*0.15 + df["s_6m"]*0.10 +
        df["s_rsi"]*0.10 + df["s_adx"]*0.08 + df["s_vol"]*0.07 + df["s_roc"]*0.05 +
        df["s_breakout"]*0.10 + df["s_obv"]*0.07 + df["s_rs"]*0.05 + df["s_div"]*0.03
    ).round(1)
    df["grade"] = pd.cut(df["momentum_score"],bins=[0,50,65,80,100],labels=["D","C","B","A"],include_lowest=True)
    stocks_df = df[df["asset_type"] == "stock"] if "asset_type" in df.columns else df
    etf_df    = df[df["asset_type"] == "etf"]   if "asset_type" in df.columns else df.iloc[0:0]

    # Drop any rows where the score couldn't be computed — never let None into the top 50
    stocks_df = stocks_df.dropna(subset=["momentum_score"])
    etf_df    = etf_df.dropna(subset=["momentum_score"])

    top_stocks = stocks_df.nlargest(top_n, "momentum_score").reset_index(drop=True)
    top_stocks.insert(0, "rank", range(1, len(top_stocks)+1))

    top_etfs = etf_df.nlargest(50, "momentum_score").reset_index(drop=True)
    top_etfs.insert(0, "rank", range(1, len(top_etfs)+1))

    # Hard validation — pipeline should never produce None scores in output
    assert top_stocks["momentum_score"].notna().all(), "BUG: None scores in top stocks"
    assert top_etfs.empty or top_etfs["momentum_score"].notna().all(), "BUG: None scores in top ETFs"

    log.info(f"Top {top_n} stocks. Score: {top_stocks.momentum_score.min():.1f}–{top_stocks.momentum_score.max():.1f}")
    if not top_etfs.empty:
        log.info(f"Top 50 ETFs. Score: {top_etfs.momentum_score.min():.1f}–{top_etfs.momentum_score.max():.1f}")
    return top_stocks, top_etfs


def add_groq_summaries(df, api_key):
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        summaries = []
        log.info("Generating Groq AI summaries...")
        for _, r in df.iterrows():
            prompt = (f"You are a concise financial analyst. Write a 2-sentence momentum summary for "
                      f"{r['ticker']} ({r['sector']}). "
                      f"Data: Price ${r['price']}, 1M {r['ret_1m']:+.1f}%, 3M {r['ret_3m']:+.1f}%, "
                      f"RSI {r['rsi']}, ADX {r['adx']}, MACD {r['macd_signal']}, "
                      f"Stoch K={r['stoch_k']}, Vol ratio {r['vol_ratio']}x, "
                      f"{r['pct_from_high']:.1f}% from 52W high. "
                      f"VWAP {r['vwap_pct']:+.1f}%, Breakout Quality {r['breakout_quality']}/100, "
                      f"OBV {r['obv_trend']} ({r['obv_score']:.0f}/100), "
                      f"RSI Divergence: {r['div_label']}, "
                      f"Rel Strength vs Sector: {r['rel_strength_sector']:+.1f}%. "
                      f"Be factual. No buy/sell advice.")
            try:
                resp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role":"user","content":prompt}],
                    max_tokens=120, temperature=0.3)
                summaries.append(resp.choices[0].message.content.strip())
            except:
                summaries.append("")
        df["ai_summary"] = summaries
        log.info("Groq summaries complete.")
    except ImportError:
        log.warning("groq not installed. Run: pip install groq")
        df["ai_summary"] = ""
    except Exception as e:
        log.warning(f"Groq error: {e}")
        df["ai_summary"] = ""
    return df


def enrich_metadata(df):
    """
    Fill full_name, description, sub_sector for any ticker missing them,
    by fetching yfinance .info. Only fetches tickers that need it.
    """
    missing = df[
        df["full_name"].eq("") | df["description"].eq("") | df["sub_sector"].eq("")
    ]["ticker"].tolist()

    if not missing:
        return df

    log.info(f"Fetching metadata from yfinance for {len(missing)} tickers: {missing}")
    for ticker in missing:
        try:
            info = yf.Ticker(ticker).info
            if df.loc[df["ticker"] == ticker, "full_name"].values[0] == "":
                df.loc[df["ticker"] == ticker, "full_name"] = info.get("longName", "")
            if df.loc[df["ticker"] == ticker, "description"].values[0] == "":
                summary = info.get("longBusinessSummary", "")
                # Trim to ~200 chars at a sentence boundary
                if len(summary) > 200:
                    cut = summary[:200].rfind(". ")
                    summary = summary[:cut + 1] if cut > 100 else summary[:200]
                df.loc[df["ticker"] == ticker, "description"] = summary
            if df.loc[df["ticker"] == ticker, "sub_sector"].values[0] == "":
                df.loc[df["ticker"] == ticker, "sub_sector"] = info.get("industry", "")
        except Exception as e:
            log.warning(f"Metadata fetch failed for {ticker}: {e}")

    return df


def push_to_github(local_path, token, repo, branch="main", dest_path=None):
    """
    Push any local file to GitHub Pages using the GitHub REST API.
    Auto-updates your live dashboard after every run.

    Args:
        local_path : local file to push (e.g. "data.json", "index.html")
        token      : GitHub Personal Access Token (repo scope)
        repo       : "username/repo-name"
        branch     : branch name (default: main)
        dest_path  : destination path in repo (defaults to filename)
    """
    import urllib.request, base64

    dest_path = dest_path or os.path.basename(local_path)

    with open(local_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    api_url = f"https://api.github.com/repos/{repo}/contents/{dest_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    }

    req = urllib.request.Request(api_url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            existing = json.loads(resp.read())
        sha = existing["sha"]
        log.info(f"GitHub: existing {dest_path} found, will update.")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            sha = None
            log.info(f"GitHub: {dest_path} not found, will create.")
        else:
            log.warning(f"GitHub GET failed: {e}")
            return

    commit_msg = f"Auto-update: Week {date.today().isocalendar()[1]} {date.today().year} ({date.today()})"
    payload = json.dumps({
        "message": commit_msg,
        "content": encoded,
        "branch": branch,
        **({"sha": sha} if sha else {}),
    }).encode("utf-8")

    put_req = urllib.request.Request(api_url, data=payload, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(put_req) as resp:
            result = json.loads(resp.read())
        log.info(f"✅ {dest_path} pushed! Commit: {result['commit']['sha'][:7]}")
        username, reponame = repo.split("/")
        log.info(f"🌐 Live at: https://{username}.github.io/{reponame}")
    except urllib.error.HTTPError as e:
        log.warning(f"GitHub push failed: {e.code} — {e.read().decode()}")


def export(df, etf_df, tags):
    df = df.copy()
    df["exchange"] = df["ticker"].map(tags).fillna("S&P500")
    if "ai_summary" not in df.columns:
        df["ai_summary"] = ""

    # Enrich every stock record with display metadata so the UI never needs
    # hardcoded fallback lookups — any ticker that enters the top-50 will
    # automatically carry its own label, description, and sub-sector.
    df["full_name"]   = df["ticker"].map(FULL_NAME_MAP).fillna("")
    df["description"] = df["ticker"].map(DESCRIPTION_MAP).fillna("")
    df["sub_sector"]  = df["ticker"].map(SUB_SECTOR_MAP).fillna("")
    df = enrich_metadata(df)

    if not etf_df.empty:
        etf_df = etf_df.copy()
        etf_df["full_name"]   = etf_df["ticker"].map(FULL_NAME_MAP).fillna("")
        etf_df["description"] = etf_df["ticker"].map(DESCRIPTION_MAP).fillna("")
        etf_df["sub_sector"]  = etf_df["ticker"].map(SUB_SECTOR_MAP).fillna("")
        etf_df = enrich_metadata(etf_df)

    sector_counts = df["sector"].value_counts().to_dict()
    grade_counts = df["grade"].value_counts().to_dict()

    df = df.replace([np.nan, np.inf, -np.inf], None)
    if not etf_df.empty:
        etf_df = etf_df.replace([np.nan, np.inf, -np.inf], None)

    def sanitize(obj):
        """Recursively replace float NaN/Inf with None so JSON is always valid."""
        if isinstance(obj, float) and (obj != obj or obj == float("inf") or obj == float("-inf")):
            return None
        if isinstance(obj, dict):
            return {k: sanitize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [sanitize(v) for v in obj]
        return obj

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "week": date.today().isocalendar()[1],
        "year": date.today().year,
        "total_universe": len(tags),
        "sector_breakdown": sector_counts,
        "grade_breakdown": {str(k): v for k, v in grade_counts.items()},
        "avg_score": round(float(df["momentum_score"].mean()), 1),
        "pct_above_ma200": round(float(df["above_ma200"].mean() * 100), 1),
        "stocks": json.loads(df.to_json(orient="records").replace(":NaN,", ":null,").replace(":NaN}", ":null}").replace(":NaN]", ":null]")),
        "etfs":   json.loads(etf_df.to_json(orient="records").replace(":NaN,", ":null,").replace(":NaN}", ":null}").replace(":NaN]", ":null]")),
        "etf_avg_score":          round(float(etf_df["momentum_score"].mean()), 1) if not etf_df.empty else 0,
        "etf_pct_above_ma200":    round(float(etf_df["above_ma200"].mean() * 100), 1) if not etf_df.empty else 0,
        "etf_grade_breakdown":    {str(k): v for k, v in etf_df["grade"].value_counts().to_dict().items()} if not etf_df.empty else {},
        "etf_category_breakdown": etf_df["sector"].value_counts().to_dict() if not etf_df.empty else {},
    }

    payload = sanitize(payload)

    with open("data.json", "w") as f:
        json.dump(payload, f, indent=2)

    log.info("Saved → data.json")



    cols = [
        "rank","ticker","exchange","sector","price","momentum_score","grade",
        "ret_1m","ret_3m","ret_6m","ret_mtd","ret_ytd","ret_1y","rsi","stoch_k","stoch_d","adx","bb_pct",
        "atr_pct","roc10","macd_signal","vol_ratio","pct_from_high",
        "above_ma50","above_ma200",
        "vwap_pct","breakout_quality","div_score","div_label",
        "obv_trend","obv_score","rel_strength_sector",
        "ai_summary"
    ]

    df[cols].to_csv("top50_momentum.csv", index=False)

    etf_cols = [c for c in cols if c in etf_df.columns]
    if not etf_df.empty:
        etf_df[etf_cols].to_csv("top50_etfs.csv", index=False)
        log.info("Saved → top50_etfs.csv")

    log.info("Saved → top50_momentum.csv")


if __name__ == "__main__":
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    tickers, tags              = get_universe()
    close, volume, high, low   = download_prices(tickers, period="1y")
    df_ind                     = compute_indicators(close, volume, high, low)
    if df_ind.empty:
        log.error("No valid records. Check network/yfinance.")
        raise SystemExit(1)
    top50, top50_etfs = score_and_rank(df_ind, top_n=50)
    if GROQ_API_KEY:
        top50 = add_groq_summaries(top50, GROQ_API_KEY)
    export(top50, top50_etfs, tags)
    print("\n"+"="*70)
    print(f"  TOP 10 MOMENTUM STOCKS  |  Week {date.today().isocalendar()[1]}, {date.today().year}")
    print("="*70)
    print(top50[["rank","ticker","sector","momentum_score","grade",
                 "ret_1m","ret_3m","rsi","adx","macd_signal"]].head(10).to_string(index=False))
    print("="*70)
    if GROQ_API_KEY: print("\nGroq AI summaries: included")
    else: print("\nGroq summaries: skipped (set GROQ_API_KEY env var to enable)")
    print("\n✅ Done! Open index.html directly in your browser — no server needed!")

    # ── AUTO-PUSH TO GITHUB PAGES ─────────────────────────────────────────
    # Fill in your details once. After that, every run auto-updates your live link.
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")   # set env var OR paste token here
    GITHUB_REPO  = "arpitkaran10-afk/momentum-dashboard"   # your repo

    if GITHUB_TOKEN:
        log.info("Pushing updated dashboard to GitHub Pages...")
        push_to_github("data.json", GITHUB_TOKEN, GITHUB_REPO)
        push_to_github("index.html", GITHUB_TOKEN, GITHUB_REPO)
    else:
        print("\n💡 To auto-publish: set GITHUB_TOKEN env var or paste your token into GITHUB_TOKEN in this script.")
        print("   Your dashboard will then auto-update at https://arpitkaran10-afk.github.io/momentum-dashboard")
