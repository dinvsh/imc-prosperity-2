# IMC Prosperity 2

This repository contains the IMC Prosperity 2 code from my solo team "Noobland" (named humorously as a nod to my next to no prior experience with coding and trading).

Final position: 265th overall, 10th in Singapore.

Huge shoutout to the GOAT [jmerle](https://github.com/jmerle), who developed the open-sourced [visualizer](https://github.com/jmerle/imc-prosperity-2-visualizer) and [backtester](https://github.com/jmerle/imc-prosperity-2-backtester). These tools were invaluable in helping me grasp how the simulated markets moved.

## Results

| Round | Overall Profit | Global Rank | Country Rank |
|-------|----------------|-------------|--------------|
| 1     | 123,656        | 570         | 20           |
| 2     | 521,145        | 246         | 10           |
| 3     | 584,550        | 267         | 11           |
| 4     | 805,831        | 231         | 9            |
| 5     | 893,953        | 265         | 10           |

## Final Strategy

### Amethysts
- assumed a true value of 10,000 seashells, and utilised market-making and market-taking strategies concurrently.

### Starfruit
- used a simple linear regression model to predict the next mid-price of the STARFRUIT product based on the last 10 mid-prices.

### Orchids
- focused on regional arbitrage opportunities while attempting to leverage environmental factors like humidity and financial costs such as transport and tariffs.
- couldn't fully work out the kinks behind feature engineering the environmental factors and just left it in my final submission as a hail mary.

### Gift Baskets
- mainly used the concept of ETF arbitrage by trading around the spread between a gift basket and its underlying components (4 chocolates, 6 strawberries, and 1 rose).

### Chocolate
- could not find a consistently profitable strategy.
  
### Strawberries
- could not find a consistently profitable strategy.
  
### Roses
- tracked trades involving Rhianna and mirrored her trading decisions, as she consistently capitalized on favorable market movements.

### Coconut
- could not find a consistently profitable strategy.

### Coconut Coupons
- used the Black-Scholes model to estimate the theoretical price of coconut coupons and traded based on price discrepancies between the theoretical and market prices.
