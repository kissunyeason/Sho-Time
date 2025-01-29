![Dream](image/ohtani.png)
# Project Description
A simple self-hosted web app for authorising selected Google API Oauth2 scopes. Supports Google Drive and Google Photos.

# Features
- supports headless machine, no GUI environment is required for completing OAuth 2.0 flow
- self-hosted, full control over your own data
- privacy-oriented, manually clear session anytime you want to start over or exit
- open-source
- light-weight design
- convenient deployment via Streamlit
- cookie support, remembers last used state

# How to deploy?
Head over to [Google cloud console](https://console.cloud.google.com), create your project if you haven't already and download your client secret. Make sure to select 'Web application' from the 'Application type' dropdown-menu when you're creating OAuth client ID.

In the redirect URIs, fill in your redirect URIs. For example, in local streamlit environment, the app is usually hosted at http://localhost:8501. Do note that http://localhost as redirect URI would only work if your app configured for 'Testing' mode under Publishing status section in OAuth consent screen setting, it won't work otherwise. Do not forget also to ensure the redirect URI specified in Google Cloud Project Credentials OAuth client section has to match that of this app.

Now do the same for the app itself by creating a file named .env, and fill in the URL where your app is hosted. (refer to .env.sample file) 

In both places, make sure both values are the same and end with this exact trailing path, **/callback**. For example, `http://localhost/8501/callback`

