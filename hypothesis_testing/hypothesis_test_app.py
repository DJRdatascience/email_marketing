import streamlit as st
import numpy as np
from statsmodels.stats.gof import chisquare_effectsize
from statsmodels.stats.power import GofChisquarePower, TTestIndPower
import plotly.express as px

#####################################################################################
# FUNCTIONS
#####################################################################################

def calc_chipower( param_calc, *args ):

    # unpack arguments, last argument can be either lift (if param_calc=='Lift') or nobs (if param_calc=='Recipients')
    rate, alpha, power, last = args

    # set-up analysis
    analysis = GofChisquarePower()

    # calculate nobs (lift input)
    if param_calc == 'Lift':
        effect_size = chisquare_effectsize( np.ones(2)/2, [rate, rate+last/100] )
        return analysis.solve_power(effect_size=effect_size, power=power, nobs=None, alpha=alpha)
    
    # calculate lift (nobs input)
    else:
        # Newton's method - we use this because GofChisquarePower solves for effect size, and we want to know lift
        known = analysis.solve_power(effect_size=None, power=power, nobs=last, alpha=alpha)
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

def calc_effectsize( a, b ):
    return 2 * (np.arcsin(np.sqrt(a)) - np.arcsin(np.sqrt(b)))

def calc_tpower( param_calc, *args ):

    # unpack arguments, last argument can be either lift (if param_calc=='Lift') or nobs (if param_calc=='Recipients')
    rate, alpha, power, last = args

    # set-up analysis
    analysis = TTestIndPower()

    # calculate nobs (lift input)
    if param_calc == 'Lift':
        effect_size = calc_effectsize( rate+lift, rate )
        return analysis.solve_power(effect_size=effect_size, power=power, alpha=alpha, nobs1=None, ratio=1, alternative='two-sided' )
    
    # calculate lift (nobs input)
    else:
        # Newton's method - we use this because TTestIndPower solves for effect size, and we want to know lift
        known = analysis.solve_power(effect_size=None, power=power, alpha=alpha, nobs1=last, ratio=1, alternative='two-sided' )
        lift = 0 # initial guess
        calculated = calc_effectsize( rate+lift, rate ) # calculated effect size for the guessed value of lift
        inc = 0.1 # aribitrarily small value for initial step size between guesses
        last_sign = np.sign( known - calculated ) # used in Newton's method
        while abs( known - calculated ) > 0.001: # runs until calculated and known lift sizes are within 0.001
            sign = np.sign( known - calculated )
            if last_sign+sign == 0:
                inc /= 2
            last_sign = sign
            lift += sign*inc
            calculated = calc_effectsize( rate+lift, rate )
        return lift

def make_plot( param_calc, x, y, base_rate, param_input, t ):

    fig = px.line(
        x = x,
        y = y,
        orientation='h',
        title=f'<b>{t}</b>',
        template='simple_white'
    )

    if param_calc == 'Recipients':
        fig.add_vline( x=param_input, line_width=3, line_color='#D62728', annotation_text='Input',
                        annotation_position='top left', annotation_textangle=270,
                        annotation_font={'color':'#D62728'} )
    else:
        fig.add_hline( y=param_input, line_width=3, line_color='#D62728', annotation_text='Input',
                        annotation_position='top right', annotation_textangle=0,
                        annotation_font={'color':'#D62728'} )

    fig.update_traces(showlegend=False)

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis={'title_text': 'Number of Recipients'},
        yaxis={'title_text': f'Lift above {base_rate}% (%)'},
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

param_in = st.sidebar.selectbox(
    'Choose input parameter', [ 'Recipients', 'Lift' ]
)

if param_in == 'Recipients':
    obs_or_in = st.sidebar.number_input(
        'Recipients',value=300,min_value=20,max_value=800,step=1
    )
    obs_cr_in = obs_or_in # If we are using an input number of recipients, we do not select open-rate and click-rate numbers seperately
else: # If we are using an input lift, we calculate open-rate and click-rate numbers seperately
    obs_or_in = st.sidebar.number_input(
        'Lift (open rate)', value=8.0, min_value=0.5, max_value=50.0, step=0.1
    )
    obs_cr_in = st.sidebar.number_input(
        'Lift (click rate)', value=0.5, min_value=0.1, max_value=3.5, step=0.1
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
    '<font color="#1f77b4">Power tells us about our chance of avoiding Type II (false negative) error. We want to maximize this.</font>',
    unsafe_allow_html=True
)

#####################################################################################
# MAIN PAGE
#####################################################################################

param_dict = { 'Recipients':['lift','% lift'], 'Lift':['recipients',' recipients'] }

# Calculate the minimum lift or number of recipients to meet input criteria
required_or = calc_tpower( param_in, or_in/100, alpha_in/100, power_in/100, obs_or_in )
required_cr = calc_tpower( param_in, cr_in/100, alpha_in/100, power_in/100, obs_cr_in )
if param_in == 'Recipients':
    required_or, required_cr = round( required_or*100, 1 ), round( required_cr*100, 2 )
else:
    required_or, required_cr = round( required_or ), round( required_cr )

st.markdown( f'# Minimum { param_dict[param_in][0] }' )
st.markdown( 'To meet input power and significance, we would need to see the following.' )
st.markdown( f'## Open rate: <font color="#D62728">{ required_or }{ param_dict[param_in][1] }</font>', unsafe_allow_html=True )
st.markdown( f'## Click rate: <font color="#D62728">{ required_cr }{ param_dict[param_in][1] }</font>', unsafe_allow_html=True )
st.markdown('---')

#------------------------------------------------------------------------------------
# Plots
#------------------------------------------------------------------------------------

# Number of observations to iterate over
observations = range(20,820,20)

#~~~~~~~~~~
# Open rate
#~~~~~~~~~~
test_or = list( map( lambda obs: 100*calc_tpower( 'Recipients', or_in/100, alpha_in/100, power_in/100, obs ), observations ) )
fig1 = make_plot( param_in, observations, test_or, or_in, obs_or_in, 'Open Rate' )

#~~~~~~~~~~
# Click rate
#~~~~~~~~~~
test_cr = list( map( lambda obs: 100*calc_tpower( 'Recipients', cr_in/100, alpha_in/100, power_in/100, obs ), observations ) )
fig2 = make_plot( param_in, observations, test_cr, cr_in, obs_cr_in, 'Click Rate' )

#~~~~~~~~~~
# Plot figures
#~~~~~~~~~~
left_column, right_column = st.columns(2)
left_column.plotly_chart( fig1, use_container_width=True )
right_column.plotly_chart( fig2, use_container_width=True )