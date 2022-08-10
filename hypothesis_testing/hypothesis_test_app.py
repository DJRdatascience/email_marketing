import streamlit as st
import numpy as np
from statsmodels.stats.gof import chisquare_effectsize
from statsmodels.stats.power import GofChisquarePower
from statsmodels.stats.proportion import proportions_chisquare
import plotly.express as px

#####################################################################################
# FUNCTIONS
#####################################################################################
def calc_lift_power(rate,known_effect):
    lift = 0
    calc_effect = chisquare_effectsize(np.ones(2)/2, [rate, rate+lift])
    if calc_effect < known_effect:
        lift_inc = 0.2
        last_sign = 1
        while abs(known_effect-calc_effect) > 0.001:
            sign = np.sign(known_effect-calc_effect)
            if last_sign+sign == 0:
                lift_inc /= 2
            lift += sign*lift_inc
            last_sign = sign
            calc_effect = chisquare_effectsize(np.ones(2)/2, [rate, rate+lift])
    return lift

def calc_lift_sig(rate,obs,alpha):
    lift = 0
    stat, p, table = proportions_chisquare(count=[rate*obs,(rate+lift)*obs],nobs=[obs,obs])
    lift_inc = 0.2
    last_sign = 1
    while abs(p - alpha) > 0.001:
        sign = np.sign(p-alpha)
        if last_sign+sign == 0:
            lift_inc /= 2
        lift += sign*lift_inc
        last_sign = sign
        stat, p, table = proportions_chisquare(count=[rate*obs,(rate+lift)*obs],nobs=[obs,obs])
    return lift


def calc_power(rate,power,alpha,lift):
    nobs = [ [], [] ]
    analysis = GofChisquarePower()
    for l in lift:
        effect = chisquare_effectsize(np.ones(2)/2, [rate, rate+l])
        if effect:
            obs = analysis.solve_power(effect_size=effect, power=power, nobs=None, alpha=alpha)
            if obs > 800:
                break
            nobs[0].append(obs)
            nobs[1].append(l*100)
    return nobs

def calc_sig(rate,alpha):
    nobs = [ [], [] ]
    for obs in range(10,810,10):
        lift = calc_lift_sig(rate,obs,alpha)
        nobs[0].append(obs)
        nobs[1].append(lift*100)
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

OBS = st.sidebar.number_input(
    'Recipients',value=300,min_value=20,max_value=800,step=1
)

OR = st.sidebar.slider(
    'Base open rate (%)', min_value=20, max_value=40, value=30, step=1
)

CR = st.sidebar.slider(
    'Base click rate (%)', min_value=0.1, max_value=6.0, value=2.0, step=0.1
)

POWER = st.sidebar.slider(
    'Statistical power (%)', min_value=60, max_value=98, value=80, step=2
)
st.sidebar.markdown(
    '<font color="#1f77b4">Power tells us about our risk of Type II (false negative) error. We want to maximize this.</font>',
    unsafe_allow_html=True
) # For example, an experiment with a statistical power of 80\% has a 4 in 5 chance of correctly accepting the alternative hypothesis.

ALPHA = st.sidebar.slider(
    'Significance level (%)', min_value=2, max_value=40, value=20, step=2
)
st.sidebar.markdown(
    '<font color="#1f77b4">Significance tells us about our risk of Type I (false positive) error. We want to minimize this.</font>',
    unsafe_allow_html=True
)

# Perform some calculations
analysis = GofChisquarePower()
effect = analysis.solve_power(effect_size=None, power=POWER/100, nobs=OBS, alpha=ALPHA/100)
or_lift_power = calc_lift_power(OR/100,effect)
cr_lift_power = calc_lift_power(CR/100,effect)
or_lift_sig = calc_lift_sig(OR/100,OBS,ALPHA/100)
cr_lift_sig = calc_lift_sig(CR/100,OBS,ALPHA/100)

#####################################################################################
# MAIN PAGE
#####################################################################################

st.markdown( '# Minimum lift' )
st.markdown( 'To meet input power and significance, we would need to see the following lifts.' )
st.markdown( f'## Open rate = <font color="#D62728">{round(max([or_lift_power,or_lift_sig])*100,1)}%</font>', unsafe_allow_html=True )
st.markdown( f'## Click rate = <font color="#D62728">{round(max([cr_lift_power,cr_lift_sig])*100,1)}%</font>', unsafe_allow_html=True )
st.markdown('---')

#------------------------------------------------------------------------------------
# Open rate plots
#------------------------------------------------------------------------------------

LIFT = 1.5**(-np.logspace(0.1,1,100))
test_power = calc_power(OR/100,POWER/100,ALPHA/100,LIFT)
test_signif = calc_sig(OR/100,ALPHA/100)

#~~~~~~~~~~
# Statistical power
#~~~~~~~~~~

fig1 = px.line(
    x = test_power[0],
    y = test_power[1],
    orientation='h',
    title='<b>Statistical Power</b>',
    template='simple_white'
)
fig1.add_vline( x=OBS,line_width=3,line_color='#D62728',annotation_text='Input',
                annotation_position='top left',annotation_textangle=270,
                annotation_font={'color':'#D62728'})

fig1.update_traces(showlegend=False)

fig1.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis={'title_text': 'Number of Recipients'},
    yaxis={'title_text': f'Lift above {OR}% (%)'},
)

#~~~~~~~~~~
# Significance
#~~~~~~~~~~

fig2 = px.line(
    x = test_sig[0],
    y = test_sig[1],
    orientation='h',
    title='<b>Significance</b>',
    template='simple_white'
)
fig2.add_vline( x=OBS,line_width=3,line_color='#D62728',annotation_text='Input',
                annotation_position='top left',annotation_textangle=270,
                annotation_font={'color':'#D62728'})
fig2.update_traces(showlegend=False)

fig2.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis={'title_text': 'Number of Recipients'},
    yaxis={'title_text': f'Lift above {OR}% (%)'},
)

#~~~~~~~~~~
# Plot figures
#~~~~~~~~~~
st.markdown( '## Open Rate' )
left_column, right_column = st.columns(2)

left_column.plotly_chart( fig1, use_container_width=True )
right_column.plotly_chart( fig2, use_container_width=True )

st.markdown('---')

#------------------------------------------------------------------------------------
# Click rate plots
#------------------------------------------------------------------------------------

LIFT = 0.1/np.logspace(0,2,100)
test_power = calc_power(CR/100,POWER/100,ALPHA/100,LIFT)
test_signif = calc_sig(CR/100,ALPHA/100)

fig1 = px.line(
    x = test_power[0],
    y = test_power[1],
    orientation='h',
    title='<b>Statistical Power</b>',
    template='simple_white'
)
fig1.add_vline( x=OBS,line_width=3,line_color='#D62728',annotation_text='Input',
                annotation_position='top left',annotation_textangle=270,
                annotation_font={'color':'#D62728'})

fig1.update_traces(showlegend=False)

fig1.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis={'title_text': 'Number of Recipients'},
    yaxis={'title_text': f'Lift above {CR}% (%)'},
)

#~~~~~~~~~~
# Significance
#~~~~~~~~~~

fig2 = px.line(
    x = test_sig[0],
    y = test_sig[1],
    orientation='h',
    title='<b>Significance</b>',
    template='simple_white'
)
fig2.add_vline( x=OBS,line_width=3,line_color='#D62728',annotation_text='Input',
                annotation_position='top left',annotation_textangle=270,
                annotation_font={'color':'#D62728'})
fig2.update_traces(showlegend=False)

fig2.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis={'title_text': 'Number of Recipients'},
    yaxis={'title_text': f'Lift above {CR}% (%)'},
)

#~~~~~~~~~~
# Plot figures
#~~~~~~~~~~
st.markdown( '## Click Rate' )
left_column, right_column = st.columns(2)

left_column.plotly_chart( fig1, use_container_width=True )
right_column.plotly_chart( fig2, use_container_width=True )