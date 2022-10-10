# BakePy

**Create good-looking documents programatically and easily**

BakePy was conceived as an way to create good-looking documents in Python without messing with templates or difficult layout systems.

Creating a BakePy Report is simple:

```
import pandas as pd 

from bakepy import Report

r = Report()

r.add_special("Hello!")

#Adding a DataFrame in a new line.

data = {
  "cost": [420, 380, 390],
  "speed": [50, 40, 45]
}
df = pd.DataFrame(data)

r.add(df, caption = "This is a table", new_row = True)

#Adding a plot on the same line.

r.add(df.plot(x="cost", y="speed").figure, caption = "This is a figure")

#Saving the report

r.save_html("example_report.html")
```

## Simple to use, easy to hack

BakePy is designed to automatically transform Python objects such as Matplotlib Figures and Pandas DataFrames into HTML code. By using Bootstrap 5's grid you can easily arrange markup, mathematical formulas, plots and tables without needing boilerplate code.

If you need more customization, you can easily add CSS stylesheets in order to make the Report look exactly how you want it to.
