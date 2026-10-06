from flask import Flask, redirect, request, g
from urllib.parse import urlparse, urlunparse, urlencode

app = Flask(__name__)


@app.before_request
def capture_referrer():
    # Capture Referer header to track origin referrers externally
    referrer = request.headers.get("Referer")
    if referrer:
        host = request.host.lower()
        parsed_ref = urlparse(referrer)
        ref_host = parsed_ref.netloc.lower()

        # Exclude self-referrals within our domain and subdomains
        if (
            ref_host
            and ref_host != host
            and not ref_host.endswith(".mett.top")
            and ref_host != "mett.top"
        ):
            g.new_referrer = referrer


@app.after_request
def set_referrer_cookie(response):
    if hasattr(g, "new_referrer"):
        # Keep the cookie active for 30 days
        response.set_cookie(
            "from_referer", g.new_referrer, max_age=86400 * 30, path="/"
        )
    return response


def redirect_with_tracking(target_url):
    query = request.args.to_dict(flat=False)

    if request.referrer and "ref" not in query:
        query["ref"] = [request.referrer]

    parsed = urlparse(target_url)

    if query:
        query_str = urlencode(query, doseq=True)
    else:
        query_str = parsed.query

    final_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        query_str,
        parsed.fragment,
    ))

    return redirect(final_url)


@app.errorhandler(404)
def page_not_found(e):
    return redirect_with_tracking("https://www.mett.top:444/")


@app.route("/")
def root():
    return redirect_with_tracking("https://www.mett.top:444/")
