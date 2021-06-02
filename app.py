import streamlit as st
import random
import requests
from time import sleep
from streamlit import caching
from streamlit.report_thread import get_report_ctx
import os, json

Languages = ['C', 'C++', 'C#', 'Go', 'Java', 'Javascript', 'Shell', 'Ruby', 'Python', 'Perl', 'Html', 'CSS', 'null', None]

def get_random_gist_url():
    id = random.randint(5000, 10000)
    url = "https://api.github.com/gists/" + str(id)
    return url

def get_code_from_gist(url):
    res = requests.get(url)
    try:
        data = res.json()['files']
        language = data[list(data.keys())[0]]['language']
        content = data[list(data.keys())[0]]['content']
    except:
        return False
    else:
        return{
                'language':language,
                'content':content
        }

@st.cache(show_spinner=False)
def random_gist():
    url = get_random_gist_url()
    gist = get_code_from_gist(url)
    while not gist:
        url = get_random_gist_url()
        gist = get_code_from_gist(url)
    return gist

@st.cache
def get_options_list(correct):
    options = random.sample(Languages,4)
    options.append(correct)
    options = list(set(options))
    random.shuffle(options)
    return options

def about_dev():
    st.sidebar.title("About the developer")
    st.sidebar.markdown("""
    #### Hi there, I am Akshansh Kumar <img src="https://media.giphy.com/media/hvRJCLFzcasrR4ia7z/giphy.gif" width="25px">
    ###### Please visit my [github page](https://github.com/akshanshkmr) for more such utilities
    ###### If you liked my work and would like to support me, consider buying me a coffee 😄
    <br><a href="https://www.buymeacoffee.com/akshanshkmr" target="_blank">
    <img class="center" src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a> 
    """,unsafe_allow_html=True)

def get_score():
    scores_file = os.path.dirname(os.path.realpath(__file__)) + '/scores.json'
    ctx = get_report_ctx()
    session_id = ctx.session_id
    with open(scores_file) as f:
        data = json.load(f)
    if session_id in data.keys():
        score = str(data[session_id]['correct']) + "/" + str(data[session_id]['total'])
        return score
    else:
        return '0/0'

def update_score(score):
    scores_file = os.path.dirname(os.path.realpath(__file__)) + '/scores.json'
    ctx = get_report_ctx()
    session_id = ctx.session_id
    with open(scores_file) as f:
        data = json.load(f)
        if session_id in data.keys():
            total = data[session_id]['total']
            correct = data[session_id]['correct']
            total+=1
            correct +=score
        else:
            total=1
            correct=score
    with open(scores_file, 'w') as f:
        data.update({
            session_id:{
                'total':total,
                'correct':correct
            }
        })
        json.dump(data, f)


if __name__ == "__main__":
    st.set_page_config(page_title="CodeGame", layout='wide')
    about_dev()
    st.title('CodeGame')
    cols = st.beta_columns([.5,.5])
    cols[0].subheader('Identify the programming language')
    cols[1].subheader('Current score : ' + get_score())

    with st.spinner('Generating random code snippet ...'):
        gist = random_gist()
    correct = gist['language']
    options = get_options_list(correct)

    with st.form('quiz'):
        st.code(gist['content'])
        # st.caption(str(correct)) # to show correct answer
        chosen = st.radio('Choose the correct option',  options)
        if st.form_submit_button('Confirm'):
            if chosen == correct:
                st.success('That is Correct!')
                update_score(1)
            else:
                st.error("Sorry that is incorrect, correct answer is " + str(correct))
                update_score(0)
            # wait for .2 seconds before clearing cache and rerunning the app
            sleep(0.2)
            caching.clear_cache()
            st.experimental_rerun()
