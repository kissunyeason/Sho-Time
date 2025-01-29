import streamlit as st
import extra_streamlit_components as stx
import json


def get_manager():
    return stx.CookieManager(key='init-callback')


cookie_manager = get_manager()
cookies = cookie_manager.get_all(key='get_all-callback')

if cookies:
    if 'session_id' in cookies:
        st.session_state.session_id = cookies['session_id']
    if 'credential_data' in cookies:
        st.session_state.credential_data = cookies['credential_data']
    if 'authorising_Oauth' in cookies:
        st.session_state.authorising_Oauth = cookies['authorising_Oauth']

query_params = st.query_params
if query_params:
    # st.json(query_params.items())
    # st.json(st.session_state, expanded=False)  # check if state stays the same across pages and across tabs
    if 'code' in query_params and 'session_id' in st.session_state and 'authorising_Oauth' in st.session_state:
        st.write('writing flow code .txt')
        if st.session_state.authorising_Oauth:
            with open(f'dist/{st.session_state.session_id}-flow code.txt', 'w') as f:
                json.dump(query_params.to_dict(), f)


@st.dialog("✅Flow code retrieved from callback URL")
def instruction_modal():
    st.write(
        'Please return to the tab/window where you left off before being redirected to Google Cloud Console for app authorisation.')
    st.markdown('Navigating to :green[Home] page from within this tab would not work.')


if 'code' in query_params and 'authorising_Oauth' in st.session_state and 'session_id' in st.session_state:
    if st.session_state.authorising_Oauth:
        instruction_modal()
else:
    st.info(
        'Nothing in here. This page is meant to act as an outfielder to receive callback from google cloud console.')

st.image('image/ohtani.png')
