The bulk of the efforts will be directed towards gathering, cleaning and preparing the data. There are three kinds of analysis that will be performed:
1 Fundamental Analysis
2 Technical Analysis
3 Sentiment Analysis  

FUNDAMENTAL ANALYSIS: Fundamental analysis is a method of evaluating security to measure its intrinsic value, by examining related economic, financial and other qualitative and quantitative factors. The end goal of fundamental analysis is to produce a quantitative value that an investor can compare with a security's current price, thus indicating whether the security is undervalued or overvalued. For example, an investor can perform fundamental analysis on a bond's value by looking at economic factors such as interest rates and the overall state of the economy. They can also look at information about the bond issuer, such as potential changes in credit ratings. For stocks and equity instruments, this method uses revenues, earnings, future growth, return on equity, profit margins and other data to determine a company's underlying value and potential for future growth. In terms of stocks, fundamental analysis focuses on the financial statements of the company being evaluated. It involves studying and comparing various ratios such as:
p/B RATIO
P/E RATIO
CASH FLOW 
DEBT LOAD  
MARGIN PRICE 
MULTIPLE BOOK VALUE  

TECHNICAL ANALYSIS: Technical analysis is a trading tool employed to evaluate securities and attempt to forecast their future movement by analysing statistics gathered from trading activity, such as price movement and volume. Unlike fundamental analysts who attempt to evaluate a security's intrinsic value, technical analysts focus on charts of price movement and various analytical tools to evaluate a security's strength or weakness and forecast future price changes.  Technical Analysis uses the concept of Dow Theory. Two basic assumptions of Dow Theory that underlie all technical analysis are: 
1) market price discounts every factor that may influence a security's price and 
2) market price movements are not purely random but move in identifiable patterns and trends that repeat over time. Technical analysis is used to attempt to forecast the price movement of virtually any tradable instrument that is generally subject to forces of supply and demand, including stocks, bonds, futures and currency pairs. In fact, technical analysis can be viewed as simply the study of supply and demand forces as reflected in the market price movements of a security. It is most commonly applied to price changes, but some analysts may additionally track numbers other than just price, such as trading volume or open interest figures.  

SENTIMENT ANALYSIS: In addition to the "usual" tricks of statistical arbitrage, trend-following and fundamental analysis, many quant shops (and retail quants!) engage in natural language processing (NLP) techniques to build systematic strategies. Such techniques fall under the banner of Sentiment Analysis. The goal of sentiment analysis is, generally, to take large quantities of data in the form of blog posts, newspaper articles, research reports, tweets, etc and use NLP techniques to quantify positive or negative 'sentiments' about certain assets. For equities this often amounts to a statistical machine learning analysis of the language utilised and whether it contains bullish or bearish phrasing. This phrasing can be quantified in terms of strength of sentiment, which translates into numerical values. Often this means positive values reflecting bullish sentiment and negative values representing bearish sentiment.

CONCLUSION
The results of all the individual analysis will be combined in a weighted manner to yield a final outcome which will be demonstrated via a custom developed API designed in Django. The API will generate responses in JSON data format, providing either cleaned data or the analysis results, as requested by the user depending on the URL provided.
