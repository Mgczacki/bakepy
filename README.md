# BakePy

**Create good-looking documents programatically and easily**

BakePy was conceived as an way to create good-looking documents in Python without messing with templates or difficult layout systems.

Creating a BakePy Report is simple:

``` python
import pandas as pd 
from datetime import datetime as dt
from bakepy import Report

r = Report()

r.recipe("title", "Example BakePy Report")

r.recipe("markdown",
f"""
### {dt.now().strftime("%Y-%m-%d")}
""")
#We want to center text in the current column.
r.set_col_cls("text-center")

#A separator
r.recipe("separator")

#Some variables
a = 4
color = "blue"
l = ["red", 3, False]
#Replacing variables in generated text.
r.recipe("markdown",
f"""
We can add markdown and use the power of Python to mix:

- Variables, like a={a}
- Conditional formatting, like adding the <span style="color:{color}">color {color}</span>
- And even directly transform Python objects beyond things like the list: {l}
"""
)
#Now we add some more text, this time in the same row we were at before.
r.add("<h2> See some examples below! </h2>", new_row = False)
#We can even add items to the same column!
r.recipe("spacer", level = 3, new_col = False)
r.add(
"""
For example, Pandas Dataframes and Matplotlib Figures
""", new_col = False)

#Adding a DataFrame in a new line.
data = {
  "cost": [10, 23, 40],
  "gain": [20, 40, 45]
}
df = pd.DataFrame(data)

r.add(df, caption = "This is a table")
#We set row items to be aligned at the center.
r.set_row_cls("align-items-center")

#Adding a plot on the same line.
r.add(df.plot(x="cost", y="gain"), size=6, caption = "This is a figure", new_row=False)
#Saving the report

#An image
r.recipe("img",
"https://upload.wikimedia.org/wikipedia/en/thumb/8/80/Wikipedia-logo-v2.svg/800px-Wikipedia-logo-v2.svg.png",
size = 2,
caption = "Adding an image from the Internet.")

r.save_html("example_report.html")
```

## Simple to use, easy to hack

BakePy is designed to automatically transform Python objects such as Matplotlib Figures and Pandas DataFrames into HTML code. By using Bootstrap 5's grid you can easily arrange markup, mathematical formulas, plots and tables without needing boilerplate code.

If you need more customization, you can easily add CSS stylesheets in order to make the Report look exactly how you want it to.
