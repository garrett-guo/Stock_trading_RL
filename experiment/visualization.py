import altair as alt
import seaborn as sns
import pandas as pd
from datetime import datetime as dt


def visualize(df):
	scale = alt.Scale(
		domain=(min(min(df['close']), min(df['wealth'])) - 0.2, max(max(df['close']), max(df['wealth'])) + 0.2),
		clamp=True)

	close = alt.Chart(df).mark_line(
		color='red',
		opacity=0.2
	).encode(
		x='date:T',
		y=alt.Y('close', axis=alt.Axis(format='.4f', title='Net Worth'), scale=scale)
	).interactive(bind_y=False)


	wealth= alt.Chart(df).mark_line(
		color='black',
		opacity=0.2
	).encode(
		x='date:T',
		y=alt.Y('wealth', axis=alt.Axis(format='.4f', title='Net Worth'), scale=scale)
	).interactive(bind_y=False)

	points = alt.Chart(df).transform_filter(
		alt.datum.action != 'HOLD'
	).mark_point(
		filled=True
	).encode(
		x=alt.X('date:T', axis=alt.Axis(title='Date')),
		y=alt.Y('close', axis=alt.Axis(format='.4f', title='Net Worth'), scale=scale),
		color='action'
	).interactive(bind_y=False)

	chart = alt.layer(wealth, close, points, title="Portfolio Actions").properties(height=300, width=800)

	return chart