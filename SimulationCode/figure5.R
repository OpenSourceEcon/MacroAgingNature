library(tidyverse)

df = data.frame(intervention = rep(c("Brain Aging",
                                     "Ovarian Aging",
                                     "41 Is the\nNew 40",
                                     "66 Is the\nNew 65"), each=3),
                Scenario = rep(c("Base",
                                 "Pessimistic",
                                 "Optimistic"), 4),
                avg_gdp_change = c(201, -385, 246,
                                   9.1, 3.5, 14.6,
                                   408, 321, 496,
                                   326, 256, 397))

df$intervention = factor(df$intervention,
                         levels=c("Brain Aging",
                                  "Ovarian Aging",
                                  "41 Is the\nNew 40",
                                  "66 Is the\nNew 65"))

ggplot(df, aes(x=avg_gdp_change, y=intervention, shape = Scenario)) +
  geom_point(size=3) +
  xlab("Projected Average Annual\nChange in GDP, 2045-2064") +
  ylab("") +
  scale_y_discrete(limits=rev) +
  scale_x_continuous(limits=c(0,500)) +
  theme_bw() +
  theme(legend.position="bottom")
ggsave('sl_scenario_plot.png', height = 5, width = 5, units="in")
