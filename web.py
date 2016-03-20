
import GeoIP
import os
import gzip
import humanize
from flask import Flask, request
from logparser import LogParser
from maprender import render_map
from jinja2 import Environment, FileSystemLoader

gi = GeoIP.open("/usr/share/GeoIP/GeoIP.dat", GeoIP.GEOIP_MEMORY_CACHE)

KEYWORDS = "Windows", "Mac OS X", "Android", "Linux"
PROJECT_ROOT = os.path.dirname(__file__)

env = Environment(
    loader=FileSystemLoader(os.path.join(PROJECT_ROOT, "templates")),
    trim_blocks=True)

app = Flask(__name__)

def list_log_files():
    """
    This is simply used to filter the files in the logs directory
    """
    for filename in os.listdir("/var/log/apache2"):
        if filename.startswith("access"):
            yield filename


@app.route("/report/")
def report():
    # Create LogParser instance for this report
    logparser = LogParser(gi, KEYWORDS)

    filename = request.args.get("filename")
    if "/" in filename: # Prevent directory traversal attacks
        return "Go away!"

    path = os.path.join("/var/log/apache2", filename)
    logparser.parse_file(gzip.open(path) if path.endswith(".gz") else open(path))

    return env.get_template("report.html").render({
            "map_svg": render_map(open(os.path.join(PROJECT_ROOT, "templates", "map.svg")), logparser.countries),
            "humanize": humanize.naturalsize,
            "keyword_hits": sorted(logparser.d.items(), key=lambda i:i[1], reverse=True),
            "url_hits": sorted(logparser.urls.items(), key=lambda i:i[1], reverse=True),
            "user_bytes": sorted(logparser.user_bytes.items(), key = lambda item:item[1], reverse=True)
        })


@app.route("/")
def index():
    return env.get_template("index.html").render(
        log_files=list_log_files())


if __name__ == '__main__':
    app.run(debug=True)
