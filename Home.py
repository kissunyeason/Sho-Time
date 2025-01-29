import streamlit as st
import json
from io import StringIO
from module import google_api_authenticator
import os
import extra_streamlit_components as stx
import uuid
from time import sleep, time
import glob

st.set_page_config(page_title='Sho-Time', initial_sidebar_state='collapsed',
                   page_icon=':house:')


def set_cookie_js(cookie, val, days=1):
    js_code = f"""
    <script>
    function setCookie(cookie, val, days) {{
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        let expires = "expires=" + date.toUTCString();
        document.cookie = cookie + "=" + val + ";" + expires + ";path=/";
    }}
    setCookie('{cookie}', '{val}', {days});
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)


def delete_cookie_js(cookie):
    js_code = f"""
    <script>
    function deleteCookie(cookie) {{
        document.cookie = cookie + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    }}
    deleteCookie('{cookie}');
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)


def get_manager():
    return stx.CookieManager()


cookie_manager = get_manager()
cookies = cookie_manager.get_all()
# read off values from cookies if any, to load previous states from previous session
if cookies:
    if 'session_id' in cookies:
        st.session_state.session_id = cookies['session_id']
    else:
        st.session_state.session_id = str(uuid.uuid4())
        set_cookie_js(cookie='session_id', val=st.session_state.session_id)
    if 'credential_data' in cookies:
        st.session_state.credential_data = cookies['credential_data']
    if 'authorising_Oauth' in cookies:
        st.session_state.authorising_Oauth = cookies['authorising_Oauth']

# st.subheader('Initial cookie')
# st.json(cookies, expanded=False)
# st.divider()

RADIO_CHOICE_MAP = {
    'None': 0,
    ':orange-background[Readonly]': 1,
    ':orange-background[Full]': 2
}

if 'credential_data' not in st.session_state:
    st.session_state.credential_data = None
if 'authorising_OAuth' not in st.session_state:
    st.session_state.authorising_Oauth = False

st.title('A simple Google Drive and Photos Authenticator')
st.header('1) Pick your scope(s)')
row = st.columns(2)

gphoto = row[0].container()
gphoto.subheader(':rainbow[Google Photos]')
default_gphoto = RADIO_CHOICE_MAP[cookies['gphoto_radio_choice']] if 'gphoto_radio_choice' in cookies else 0
gphoto.radio(
    '***Pick either one(select None to skip)***',
    [
        'None',
        ':orange-background[Readonly]',
        ':orange-background[Full]'
    ],
    captions=[
        'Skip authorising Google Photos scope',
        'Grant read only access to Google Photos',
        'Grant full permission(read, add, edit and delete) access to Google Photos'
    ],
    index=default_gphoto,
    key='gphoto',
    help='select the scope you want authorised',
    horizontal=True
)

gdrive = row[1].container()
gdrive.subheader(':rainbow[Google Drive]')
default_gdrive = RADIO_CHOICE_MAP[cookies['gdrive_radio_choice']] if 'gdrive_radio_choice' in cookies else 0
gdrive.radio(
    '***Pick either one(select None to skip)***',
    [
        'None',
        ':orange-background[Readonly]',
        ':orange-background[Full]'
    ],
    captions=[
        'Skip authorising Google Drive scope',
        'Grant read only access to Google Drive',
        'Grant full permission(read, add, edit and delete) access to Google Drive'
    ],
    index=default_gdrive,
    key='gdrive',
    help='select the scope you want authorised',
    horizontal=True
)

st.header('2) Upload your Google OAuth client file')
credential_file = st.file_uploader('Upload your Google credentials file(.json) here')

if credential_file:
    st.session_state.credential_data = StringIO(credential_file.getvalue().decode('UTF-8')).read()

if (st.session_state.gphoto != 'None' or st.session_state['gdrive'] != 'None') and st.session_state.credential_data:
    st.session_state.invalid_selection = False
else:
    st.session_state.invalid_selection = True

scopes = []

if 'Readonly' in st.session_state.gphoto:
    scopes.append('https://www.googleapis.com/auth/photoslibrary.readonly')
elif 'Full' in st.session_state.gphoto:
    scopes.append('https://www.googleapis.com/auth/photoslibrary')

if 'Readonly' in st.session_state.gdrive:
    scopes.append('https://www.googleapis.com/auth/drive.readonly')
elif 'Full' in st.session_state.gdrive:
    scopes.append('https://www.googleapis.com/auth/drive')

# st.json(st.session_state, expanded=False)

cookies_to_set = dict(
    credential_data=st.session_state.credential_data,
    gphoto_radio_choice=st.session_state.gphoto,
    gdrive_radio_choice=st.session_state.gdrive
)


def save_to_cookies():
    set_cookie_js(cookie='credential_data', val=st.session_state.credential_data)
    set_cookie_js(cookie='gphoto_radio_choice', val=st.session_state.gphoto)
    set_cookie_js(cookie='gdrive_radio_choice', val=st.session_state.gdrive)
    print('Cookies successfully saved')


button_authorise = st.button('Authorise', type='primary', disabled=st.session_state.invalid_selection,
                             key='authorise',
                             help='click to authorise once you have selected at least one scope and uploaded a valid credential file',
                             icon='🌀'
                             )

if button_authorise:
    st.session_state.authorising_Oauth = True
    set_cookie_js(cookie='authorising_Oauth', val=st.session_state.authorising_Oauth)
    with st.spinner('Saving state to cookies...'):
        save_to_cookies()
        sleep(.5)
    with st.empty():
        st.success('Cookies successfully saved!')
        sleep(.5)
        st.empty()
    flow = google_api_authenticator.generate_token(client_secret_data=st.session_state.credential_data,
                                                   scopes=scopes,
                                                   session_id=st.session_state.session_id
                                                   )
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.markdown(f'Please [sign in]({auth_url}) to authorise selected scope(s)')
    st.warning('⚠️Please do not close or refresh this page')

    while not os.path.exists(f'dist/{st.session_state.session_id}-flow code.txt'):
        print('Awaiting outfielder(another tab) to pass the ball back to main process...')
        sleep(1)
        if os.path.exists(f'dist/{st.session_state.session_id}-flow code.txt'):
            with open(f'dist/{st.session_state.session_id}-flow code.txt') as f:
                callback_result = json.load(f)
            print('flowcode is', callback_result['code'])
            flow.fetch_token(code=callback_result['code'])
            cred = flow.credentials
            print(f'Cred successfully generated: {cred}')
            with open(f'dist/{st.session_state.session_id}_token.json', 'w') as f:
                f.write(cred.to_json())
            # st.session_state.token_ready = True

st.header('3) Download token here')
if 'session_id' in st.session_state:
    if os.path.exists(f'dist/{st.session_state.session_id}-flow code.txt'):
        with st.expander(label='Contains sensitive info, watch out for data leakage when you expand this container',
                         icon='⚠️'):
            with open(f'dist/{st.session_state.session_id}_token.json', 'rb') as file:
                btn = st.download_button(
                    label="Download token",
                    data=file,
                    file_name="token.json",
                    mime="text/json",
                )

            with open(f'dist/{st.session_state.session_id}_token.json') as f:
                result = json.load(f)
            st.write(f'Refresh token👇')
            st.code(result['refresh_token'], None)
            st.write(f'Authorised scopes for this token')
            st.json(scopes)
        st.audio('audio/Burning Heart.flac', format='audio/flac', autoplay=True)
        st.balloons()
        token_success_msg = st.empty()
        token_success_msg.success('Token created and ready for download')
        sleep(10)
        token_success_msg.empty()

if st.button('Reset', type='primary', help='reset session', icon='🔄'):
    with st.spinner("Clearing cookies..."):
        for cookie in cookies.copy():
            delete_cookie_js(cookie)
        for item in st.session_state.keys():
            del item
        for file in glob.glob(f'dist/{st.session_state.session_id}*'):
            os.remove(file)
        sleep(1.5)
    st.toast('All cookies have been successfully cleared!')
    cookie_success_msg = st.empty()
    cookie_success_msg.success('All cookies have been successfully cleared!')
    sleep(1.5)
    cookie_success_msg.empty()
    st.info('A manual refresh is recommended after a session reset')


def clear_old_files(directory, age_limit=86400):
    '''clear <dist> directory periodically to prevent clogging'''
    now = time()
    file_patterns = ["*.txt", "*.json"]  # Targeted file types

    for pattern in file_patterns:
        for file_path in glob.glob(os.path.join(directory, pattern)):
            if os.path.isfile(file_path) and (now - os.path.getmtime(file_path)) > age_limit:
                os.remove(file_path)
                print(f"Deleted: {file_path}")


def get_last_cleanup():
    if os.path.exists("last_cleanup.txt"):
        with open("last_cleanup.txt", "r") as f:
            return float(f.read().strip())
    return 0  # Default to 0 if the file doesn't exist yet


def set_last_cleanup(timestamp):
    with open("last_cleanup.txt", "w") as f:
        f.write(str(timestamp))


# Run cleanup only once every 12 hours
last_cleanup = get_last_cleanup()
if time() - last_cleanup > 43200:  # 12 hours
    clear_old_files("dist")
    set_last_cleanup(time())
