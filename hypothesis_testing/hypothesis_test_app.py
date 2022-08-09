import streamlit as st
import numpy as np
from statsmodels.stats.power import TTestIndPower
import statsmodels.stats.api as sms
import plotly.express as px

#####################################################################################
# FUNCTIONS
#####################################################################################
lifts = np.arange(0.01,0.26,0.01)
def calc_power(rate=rate,power=power,lifts=lifts,alpha=alpha):
    out = []
    analysis = TTestIndPower()
    for lift in lifts:
        effect = sms.proportion_effectsize(rate, rate+lift, method='normal')
        result = analysis.solve_power(effect, power=power, nobs1=None, ratio=1.0, alpha=alpha)
        out.append(result)
    return out

#####################################################################################
# SETUP PAGE
#####################################################################################

st.set_page_config( page_title='Hypothesis_Testing',
                    page_icon=':bar_chart',
                    layout='wide' )


#####################################################################################
# SIDEBAR
#####################################################################################

st.sidebar.header('Email parameters')

n = st.sidebar.number_input(
    'Recipients',value=200,min_value=25,max_value=800,step=1
)

rate = st.sidebar.slider(
    'Base open rate (%)', min_value=20, max_value=40, value=30, step=1
)

power = st.sidebar.slider(
    'Power level (%)', min_value=60, max_value=98, value=80, step=2
)

alpha = st.sidebar.slider(
    'Significance level (%)', min_value=2, max_value=40, value=20, step=2
)

#####################################################################################
# MAIN PAGE
#####################################################################################

result = 'insignificant'
st.markdown( '# Result is <font color="#D62728">'+result+'</font>', unsafe_allow_html=True )
st.markdown( '###' )

#------------------------------------------------------------------------------------
# Row of plots
#------------------------------------------------------------------------------------

#~~~~~~~~~~
# Statistical power
#~~~~~~~~~~

fig1 = px.line(
    x = calc_power(),
    y = lifts,
    orientation='h',
    title='<b>Open Rates (percent)</b>',
    template='simple_white'
)
fig1.add_vline(x=n,line_width=3)
fig1.update_traces(showlegend=False)

fig1.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis={'title_text': None},
    yaxis={'title_text': None},
)

#~~~~~~~~~~
# Statistical power
#~~~~~~~~~~

fig1 = px.line(
    x = calc_power(),
    y = lifts,
    orientation='h',
    title='<b>Open Rates (percent)</b>',
    template='simple_white'
)
fig1.add_vline(x=n,line_width=3)
fig1.update_traces(showlegend=False)

fig1.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis={'title_text': None},
    yaxis={'title_text': None},
)

#~~~~~~~~~~
# Statistical power
#~~~~~~~~~~

fig1 = px.line(
    x = calc_power(),
    y = lifts,
    orientation='h',
    title='<b>Open Rates (percent)</b>',
    template='simple_white'
)
fig1.add_vline(x=n,line_width=3)
fig1.update_traces(showlegend=False)

fig1.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis={'title_text': None},
    yaxis={'title_text': None},
)

#~~~~~~~~~~
# Plot figures
#~~~~~~~~~~

left_column, middle_column, right_column = st.columns(3)

left_column.plotly_chart( fig1, use_container_width=True )
middle_column.plotly_chart( fig1, use_container_width=True )
right_column.plotly_chart( fig1, use_container_width=True )