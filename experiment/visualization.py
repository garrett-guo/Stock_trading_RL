import altair as alt
import seaborn as sns
import pandas as pd
from datetime import datetime as dt


def visualize(df):
	line_df = df[['date', 'Net Worth', 'category']]

	nearest = alt.selection(type='single', nearest=True, on='mouseover',
							fields=['date'], empty='none')

	line = alt.Chart(line_df).mark_line(interpolate='basis').encode(x='date:T', y='Net Worth:Q', color='category:N')

	action_points = alt.Chart(df).transform_filter(alt.datum.action != 'HOLD').mark_point(filled=True).encode(
		x=alt.X('date:T', axis=alt.Axis(title='Date')),
		y=alt.Y('Net Worth', axis=alt.Axis(format='.4f', title='Net Worth')), color='action').interactive(bind_y=False)

	selectors = alt.Chart(line_df).mark_point().encode(x='date:T', opacity=alt.value(0), ).add_selection(nearest)

	points = line.mark_point().encode(opacity=alt.condition(nearest, alt.value(1), alt.value(0)))

	text = line.mark_text(align='left', dx=5, dy=-5).encode(text=alt.condition(nearest, 'Net Worth:Q', alt.value(' ')))

	rules = alt.Chart(line_df).mark_rule(color='gray').encode(x='date:T', ).transform_filter(nearest)

	chart = alt.layer(line, selectors, points, rules, text, action_points, title="Portfolio Actions").properties(
		height=300, width=800)

	return chart