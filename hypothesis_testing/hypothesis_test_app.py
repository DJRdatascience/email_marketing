import streamlit as st
import numpy as np
from statsmodels.stats.gof import chisquare_effectsize
from statsmodels.stats.power import GofChisquarePower
import plotly.express as px

#####################################################################################
# FUNCTIONS
#####################################################################################

def calc_lift( args, obs ):

    # unpack arguments
    rate, alpha, power = args

    # set-up analysis
    analysis = GofChisquarePower()

    # calculate effect size
    known = analysis.solve_power(effect_size=None, power=power, nobs=obs, alpha=alpha)

    # Newton's method - we use this because GofChisquarePower solves for effect size, and we want to know lift
    lift = 0 # initial guess
    calculated = chisquare_effectsize(np.ones(2)/2, [rate, rate+lift]) # calculated effect size for the guessed value of lift
    inc = 0.1 # aribitrarily small value for initial step size between guesses
    last_sign = np.sign( known - calculated ) # used in Newton's method
    while abs( known - calculated ) > 0.001: # runs until calculated and known lift sizes are within 0.001
        sign = np.sign( known - calculated )
        if last_sign+sign == 0:
            inc /= 2
        last_sign = sign
        lift += sign*inc
        calculated = chisquare_effectsize(np.ones(2)/2, [rate, rate+lift])

    return lift

def iter_nobs( *args, obs_it = range(20,820,20) ):
    return [ 100*calc_lift( args, obs ) for obs in obs_it ]

def make_plot( x, y, user_input, t ):

    fig = px.line(
        x = x,
        y = y,
        orientation='h',
        title=f'<b>{t}</b>',
        template='simple_white'
    )
    fig.add_vline( x=user_input, line_width=3, line_color='#D62728', annotation_text='Input',
                    annotation_position='top left', annotation_textangle=270,
                    annotation_font={'color':'#D62728'} )

    fig.update_traces(showlegend=False)

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis={'title_text': 'Number of Recipients'},
        yaxis={'title_text': f'Lift above {or_in}% (%)'},
    )

    return fig

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

param_in = st.selectbox(
    'Choose input parameter', [ 'Lift', 'Recipients' ]
)

obs_in = st.sidebar.number_input(
    'Recipients',value=300,min_value=20,max_value=800,step=1
)

or_in = st.sidebar.slider(
    'Base open rate (%)', min_value=20, max_value=40, value=30, step=1
)

cr_in = st.sidebar.slider(
    'Base click rate (%)', min_value=0.1, max_value=6.0, value=2.0, step=0.1
)

alpha_in = st.sidebar.slider(
    'Significance level (%)', min_value=2, max_value=40, value=20, step=2
)
st.sidebar.markdown(
    '<font color="#1f77b4">Significance tells us about our risk of Type I (false positive) error. We want to minimize this.</font>',
    unsafe_allow_html=True
)

power_in = st.sidebar.slider(
    'Statistical power (%)', min_value=60, max_value=98, value=80, step=2
)
st.sidebar.markdown(
    '<font color="#1f77b4">Power tells us about our risk of Type II (false negative) error. We want to maximize this.</font>',
    unsafe_allow_html=True
)

#####################################################################################
# MAIN PAGE
#####################################################################################

# Perform some calculations
or_lift = calc_lift( (or_in/100, alpha_in/100, power_in/100), obs_in )
cr_lift = calc_lift( (cr_in/100, alpha_in/100, power_in/100), obs_in )

st.markdown( '# Minimum lift' )
st.markdown( 'To meet input power and significance, we would need to see the following lifts.' )
st.markdown( f'## Open rate = <font color="#D62728">{ round(or_lift*100,1) }%</font>', unsafe_allow_html=True )
st.markdown( f'## Click rate = <font color="#D62728">{ round(cr_lift*100,1) }%</font>', unsafe_allow_html=True )
st.markdown('---')

#------------------------------------------------------------------------------------
# Plots
#------------------------------------------------------------------------------------

# Number of observations to iterate over
observations = range(20,820,20)

#~~~~~~~~~~
# Open rate
#~~~~~~~~~~

test_or = iter_nobs( or_in/100, alpha_in/100, power_in/100, obs_it=observations )
fig1 = make_plot( observations, test_or, obs_in, 'Open Rate' )

#~~~~~~~~~~
# Click rate
#~~~~~~~~~~

test_cr = iter_nobs( cr_in/100, alpha_in/100, power_in/100, obs_it=observations )
fig2 = make_plot( observations, test_cr, obs_in, 'Click Rate' )

#~~~~~~~~~~
# Plot figures
#~~~~~~~~~~
left_column, right_column = st.columns(2)

left_column.plotly_chart( fig1, use_container_width=True )
right_column.plotly_chart( fig2, use_container_width=True )