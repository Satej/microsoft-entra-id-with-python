import requests
from flask import Flask, render_template, session, request, redirect, url_for
from flask_session import Session
import config
import msal

app = Flask(__name__)
app.config.from_object(config)
sess = Session(app)
app.secret_key = "randomSecret"
app.config['SESSION_TYPE'] = config.SESSIONTYPE
sess.init_app(app)

@app.route("/")
def index():
    if not session.get("user"):
        cca = _build_msal_app()
        session["flow"] = cca.initiate_auth_code_flow(
            config.SCOPES, url_for("redir", _external=True));
        return render_template('index.html', 
            auth_uri=session["flow"]["auth_uri"])
    else :
        return render_template('index.html', user=session["user"])

@app.route("/redir")
def redir():
    cca = _build_msal_app()
    result = cca.acquire_token_by_auth_code_flow(session.get("flow", {}), request.args)
    session["user"] = result.get("id_token_claims")
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))

def _build_msal_app():
    return msal.ConfidentialClientApplication(
            config.CLIENT_ID, authority=config.AUTHORITY,
            client_credential=config.CLIENT_SECRET)
