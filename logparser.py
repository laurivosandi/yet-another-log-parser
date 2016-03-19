

import urllib

class LogParser(object):
    def __init__(self, gi, keywords):
        """
        This function sets up an LogParser instance
        """
        self.gi = gi                # Reference to GeoIP database object
        self.keywords = keywords    # List/tuple of keywords
        self.reset()                # Define and reset counter attributes

    def reset(self):
        """
        This function resets the counters of an LogParser instance
        """
        self.total = 0           # Total number of log entries parsed
        self.d = {}              # Hits per keyword
        self.urls = {}           # Hits per URL
        self.user_bytes = {}     # Bytes served per user
        self.countries = {}      # Hits per country code
        self.ip_addresses = {}   # Hits per source IP address

    def parse_file(self, fh):
        for line in fh:
            self.total = self.total + 1
            try:
                source_timestamp, request, response, referrer, _, agent, _ = line.split("\"")
                method, path, protocol = request.split(" ")
            except ValueError:
                continue # Skip garbage

            source_ip, _, _, timestamp = source_timestamp.split(" ", 3)

            if not ":" in source_ip: # Skip IPv6
                self.ip_addresses[source_ip] = self.ip_addresses.get(source_ip, 0) + 1
                cc = self.gi.country_code_by_addr(source_ip)
                self.countries[cc] = self.countries.get(cc, 0) + 1
            if path == "*": continue # Skip asterisk for path

            _, status_code, content_length, _ = response.split(" ")
            content_length = int(content_length)
            path = urllib.unquote(path)

            if path.startswith("/~"):
                username = path[2:].split("/")[0]
                try:
                    self.user_bytes[username] = self.user_bytes[username] + content_length
                except:
                    self.user_bytes[username] = content_length

            try:
                self.urls[path] = self.urls[path] + 1
            except:
                self.urls[path] = 1

            for keyword in self.keywords:
                if keyword in agent:
                    try:
                        self.d[keyword] = self.d[keyword] + 1
                    except KeyError:
                        self.d[keyword] = 1
                    break

