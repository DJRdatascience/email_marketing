import streamlit as st
import numpy as np
from statsmodels.stats.power import TTestIndPower
from statsmodels.stats.proportion import proportion_effectsize
import plotly.express as px

#####################################################################################
# FUNCTIONS
#####################################################################################
LIFT = np.arange(0.6,0.01,-0.005)
def calc_power(rate,power,alpha,lift=LIFT):
    nobs = [ [], [] ]
    analysis = TTestIndPower()
    for l in lift:
        effect = proportion_effectsize(rate, rate+l, method='normal')
        obs = analysis.solve_power(effect_size=effect, power=power, nobs1=None, ratio=1.0, alpha=alpha)
        if obs > 800:
            break
        nobs[0].append(obs)
        nobs[1].append(l)
    return nobs

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

nobs = st.sidebar.number_input(
    'Recipients',value=200,min_value=25,max_value=800,step=1
)

OR = st.sidebar.slider(
    'Base open rate (%)', min_value=20, max_value=40, value=30, step=1
)

CR = st.sidebar.slider(
    'Base click rate (%)', min_value=0.1, max_value=6.0, value=2.0, step=0.1
)

POWER = st.sidebar.slider(
    'Power level (%)', min_value=60, max_value=98, value=80, step=2
)

ALPHA = st.sidebar.slider(
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

test = calc_power(OR/100,POWER/100,ALPHA/100)

#~~~~~~~~~~
# Statistical power
#~~~~~~~~~~

fig1 = px.line(
    x = test[0],
    y = test[1],
    orientation='h',
    title='<b>Open Rates (percent)</b>',
    template='simple_white'
)
fig1.add_vline(x=nobs,line_width=3)
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
    x = test[0],
    y = test[1],
    orientation='h',
    title='<b>Open Rates (percent)</b>',
    template='simple_white'
)
fig1.add_vline(x=nobs,line_width=3)
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
    x = test[0],
    y = test[1],
    orientation='h',
    title='<b>Open Rates (percent)</b>',
    template='simple_white'
)
fig1.add_vline(x=nobs,line_width=3)
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