import argparse
import os
import urllib
import GeoIP

# This will contain main.py and templates
PROJECT_ROOT = os.path.dirname(__file__)

parser = argparse.ArgumentParser(description='Apache2 log parser.')
parser.add_argument('--output',
    help="This is where we place the output files such as report.html and map.svg",
    default='build')
parser.add_argument('--path',
    help="Path to Apache2 log files", default="/var/log/apache2")
parser.add_argument('--top-urls',
    help="Find top URL-s", action='store_true')
parser.add_argument('--geoip',
    help="Resolve IP-s to country codes", default="/usr/share/GeoIP/GeoIP.dat")
parser.add_argument('--verbose',
    help="Increase verbosity", action="store_true")
args = parser.parse_args()

try:
    gi = GeoIP.open(args.geoip, GeoIP.GEOIP_MEMORY_CACHE)
except:
    print "Failed to open up GeoIP database, are you sure %s exists?" % args.geoip
    exit(255)

keywords = "Windows", "Linux", "OS X", "Ubuntu", "Googlebot", "bingbot", "Android", "YandexBot", "facebookexternalhit"
d = {} # Curly braces define empty dictionary
urls = {}
user_bytes = {}
countries = {}
ip_addresses = {} # Here we are going to collect "hits per IP-address"

total = 0
import gzip
for filename in os.listdir(args.path):
    if not filename.startswith("access.log"):
        continue
    if filename.endswith(".gz"):
        fh = gzip.open(os.path.join(args.path, filename))
    else:
        fh = open(os.path.join(args.path, filename))
    if args.verbose:
        print "Parsing:", filename
    for line in fh:
        total = total + 1
        try:
            source_timestamp, request, response, referrer, _, agent, _ = line.split("\"")
            method, path, protocol = request.split(" ")
        except ValueError:
            continue # Skip garbage

        source_ip, _, _, timestamp = source_timestamp.split(" ", 3)

        if not ":" in source_ip: # Skip IPv6
            ip_addresses[source_ip] = ip_addresses.get(source_ip, 0) + 1
            cc = gi.country_code_by_addr(source_ip)
            countries[cc] = countries.get(cc, 0) + 1
        if path == "*": continue # Skip asterisk for path

        _, status_code, content_length, _ = response.split(" ")
        content_length = int(content_length)
        path = urllib.unquote(path)
        
        if path.startswith("/~"):
            username = path[2:].split("/")[0]
            try:
                user_bytes[username] = user_bytes[username] + content_length
            except:
                user_bytes[username] = content_length

        try:
            urls[path] = urls[path] + 1
        except:
            urls[path] = 1
        
        for keyword in keywords:
            if keyword in agent:
                try:
                    d[keyword] = d[keyword] + 1
                except KeyError:
                    d[keyword] = 1
                break

def humanize(bytes):
    if bytes < 1024:
        return "%d B" % bytes
    elif bytes < 1024 ** 2:
        return "%.1f kB" % (bytes / 1024.0)
    elif bytes < 1024 ** 3:
        return "%.1f MB" % (bytes / 1024.0 ** 2)
    else:
        return "%.1f GB" % (bytes / 1024.0 ** 3)


from lxml import etree
from lxml.cssselect import CSSSelector

document =  etree.parse(open(os.path.join(PROJECT_ROOT, 'templates', 'map.svg')))

max_hits = max(countries.values())

for country_code, hits in countries.items():
    if not country_code: continue # Skip localhost, sattelite phones etc
    print country_code, hex(hits * 255 / max_hits)[2:] # 2: skips 0x of hexadecimal number
    sel = CSSSelector("#" + country_code.lower())
    for j in sel(document):
        # Instead of RGB it makes sense to use hue-saturation-luma color coding
        # 120 degrees is green, 0 degrees is red
        # we want 0 to max hits to be correlated from green to red
        j.set("style", "fill:hsl(%d, 90%%, 70%%);" % (120 - hits * 120 / max_hits))

        # Remove styling from children
        for i in j.iterfind("{http://www.w3.org/2000/svg}path"):
            i.attrib.pop("class", "")

with open(os.path.join(args.output, "map.svg"), "w") as fh:
    fh.write(etree.tostring(document))

from jinja2 import Environment, FileSystemLoader # This it the templating engine we will use

env = Environment(
    loader=FileSystemLoader(os.path.join(PROJECT_ROOT, "templates")),
    trim_blocks=True)

import codecs

# This is the context variable for our template, these are the only
# variables that can be accessed inside template

context = {
    "humanize": humanize, # This is why we use locals() :D
    "url_hits": sorted(urls.items(), key=lambda i:i[1], reverse=True),
    "user_bytes": sorted(user_bytes.items(), key = lambda item:item[1], reverse=True),
}

with codecs.open(os.path.join(args.output, "report.html"), "w", encoding="utf-8") as fh:
    fh.write(env.get_template("report.html").render(context))

    # A more convenient way is to use env.get_template("...").render(locals())
    # locals() is a dict which contains all locally defined variables ;)

os.system("x-www-browser file://" + os.path.realpath("build/report.html") + " &")


print("Top IP-addresses:")
results = ip_addresses.items()
results.sort(key = lambda item:item[1], reverse=True)
for source_ip, hits in results[:5]:
    print source_ip, "==>", hits

print
print("Top 5 visited URL-s:")
results = urls.items()
results.sort(key = lambda item:item[1], reverse=True)
for path, hits in results[:5]:
    print "http://enos.itcollege.ee" + path, "==>", hits, "(", hits * 100 / total, "%)"



print "The value of __file__ is:", os.path.realpath(__file__)
print "The directory of __file__ is:", os.path.realpath(os.path.dirname(__file__))

