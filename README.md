# BakePy

**Create good-looking documents programatically and easily**

BakePy was conceived as an way to create good-looking documents in Python without messing with templates or difficult layout systems.

Creating a BakePy Report is simple:

```
import pandas as pd 
from datetime import datetime as dt
from bakepy import Report

r = Report()

r.add_special("markdown",
f"""
<h1 class="display-1"> An example BakePy report </h1>
### {dt.now().strftime("%Y-%m-%d")}
""")

r.set_col_cls("text-center")

r.add_special("separator", new_row = True)

a = 4
color = "blue"
l = ["red", 3, False]
r.add_special("markdown",
f"""
We can add markdown and use the power of Python to mix:

- Variables, like a={a}
- Conditional formatting, like adding the <span style="color:{color}">color {color}</span>
- And even directly transform Python objects beyond things like the list: {l}
""", new_row=True
)

r.add(<h2> See some examples below! </h2>)

r.add(
"""
For example, Pandas Dataframes and Matplotlib Figures
""", new_col = False)

#Adding a DataFrame in a new line.

data = {
  "cost": [420, 380, 390],
  "speed": [50, 40, 45]
}
df = pd.DataFrame(data)

r.add(df, caption = "This is a table", new_row = True)

#Adding a plot.

r.add(df.plot(x="cost", y="speed").figure, caption = "This is a figure", new_row = True)

r.set_col_cls("d-flex justify-content-center")

#Saving the report

r.save_html("example_report.html")
```

## Simple to use, easy to hack

BakePy is designed to automatically transform Python objects such as Matplotlib Figures and Pandas DataFrames into HTML code. By using Bootstrap 5's grid you can easily arrange markup, mathematical formulas, plots and tables without needing boilerplate code.

If you need more customization, you can easily add CSS stylesheets in order to make the Report look exactly how you want it to.
