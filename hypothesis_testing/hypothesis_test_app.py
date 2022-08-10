import streamlit as st
import numpy as np
import pandas as pd
from statsmodels.stats.gof import chisquare_effectsize
from statsmodels.stats.power import GofChisquarePower
from statsmodels.stats.proportion import proportions_chisquare
import plotly.express as px

#####################################################################################
# FUNCTIONS
#####################################################################################
def calc_power(rate,power,alpha,lift):
    nobs = []
    analysis = GofChisquarePower()
    for i,label in enumerate(['ab','abc','abcd']):
        for l in lift:
            effect = chisquare_effectsize( np.ones(2+i)/(2+i), [rate+l]+[rate]*(1+i) )
            if effect:
                obs = analysis.solve_power(effect_size=effect, power=power, nobs=None, alpha=alpha)
                if obs > 800:
                    break
                nobs.append([obs,l*100,label])
    return nobs

def calc_sig(rate,alpha):
    nobs = [ [], [] ]
    for obs in range(10,810,10):
        
        lift = 1-rate
        stat, p, table = proportions_chisquare(count=[rate*obs,(rate+lift)*obs],nobs=[obs,obs])
        
        if p < alpha:
            lift_inc = 0.2
            last_sign = -1
            len = 0
            while abs(p - alpha) > 0.001:
                sign = np.sign(p-alpha)
                if last_sign+sign == 0:
                    lift_inc /= 2
                lift += sign*lift_inc
                if lift < 0:
                    lift = 0.0001
                last_sign = sign

                stat, p, table = proportions_chisquare(count=[rate*obs,(rate+lift)*obs],nobs=[obs,obs])
                len += 1
                if len == 20:
                    break
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

st.markdown('---')
#------------------------------------------------------------------------------------
# Open rate plots
#------------------------------------------------------------------------------------

LIFT = 1.5**(-np.logspace(0.1,1,100))
test_power = calc_power(OR/100,POWER/100,ALPHA/100,LIFT)
test_power = pd.DataFrame(test_power,columns=['Samples','Lift','Experiment'])
test_signif = calc_sig(OR/100,ALPHA/100)

#~~~~~~~~~~
# Statistical power
#~~~~~~~~~~

fig1 = px.line(
    test_power,
    x = 'Samples',
    y = 'Lift',
    line_group = 'Experiment',
    orientation='h',
    title='<b>Statistical Power</b>',
    template='simple_white'
)
fig1.add_vline( x=nobs,line_width=3,line_color='#D62728',annotation_text='Input',
                annotation_position='top left',annotation_textangle=270,
                annotation_font={'color':'#D62728'})

fig1.update_traces(showlegend=True)

fig1.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis={'title_text': 'Number of Recipients'},
    yaxis={'title_text': f'Lift above {OR}% (%)'},
)

#~~~~~~~~~~
# Significance
#~~~~~~~~~~

fig2 = px.line(
    x = test_signif[0],
    y = test_signif[1],
    orientation='h',
    title='<b>Significance</b>',
    template='simple_white'
)
fig2.add_vline( x=nobs,line_width=3,line_color='#D62728',annotation_text='Input',
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
test_power = pd.DataFrame(test_power,columns=['Samples','Lift','Experiment'])
test_signif = calc_sig(CR/100,ALPHA/100)

fig1 = px.line(
    test_power,
    x = 'Samples',
    y = 'Lift',
    line_group = 'Experiment',
    orientation='h',
    title='<b>Statistical Power</b>',
    template='simple_white'
)
fig1.add_vline( x=nobs,line_width=3,line_color='#D62728',annotation_text='Input',
                annotation_position='top left',annotation_textangle=270,
                annotation_font={'color':'#D62728'})

fig1.update_traces(showlegend=True)

fig1.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis={'title_text': 'Number of Recipients'},
    yaxis={'title_text': f'Lift above {CR}% (%)'},
)

#~~~~~~~~~~
# Significance
#~~~~~~~~~~

fig2 = px.line(
    x = test_signif[0],
    y = test_signif[1],
    orientation='h',
    title='<b>Significance</b>',
    template='simple_white'
)
fig2.add_vline( x=nobs,line_width=3,line_color='#D62728',annotation_text='Input',
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