
from lxml import etree
from lxml.cssselect import CSSSelector

def render_map(fh, countries):
    """
    This function is used to color the map
    """
    # Parse the blank map SVG
    document =  etree.parse(fh)

    # Determine maximum count of hits per country,
    # this corresponds to color red, green is 0 anyway
    max_hits = max(countries.values())

    # Iterate over countries
    for country_code, hits in countries.items():

        # Skip localhost, sattelite phones etc
        if not country_code:
            continue

        # Select group of polygons which belongs to a particular country
        sel = CSSSelector("#" + country_code.lower())

        # Iterate over the groups
        for j in sel(document):
            # Instead of RGB it makes sense to use hue-saturation-luma color coding
            # 120 degrees is green, 0 degrees is red
            # we want 0 to max hits to be correlated from green to red
            hue = 120 - hits * 120 / max_hits

            # Set fill of inlined CSS style attribute
            j.set("style", "fill:hsl(%d, 90%%, 70%%);" % hue)

            # Remove styling from children (islands etc)
            for i in j.iterfind("{http://www.w3.org/2000/svg}path"):
                i.attrib.pop("class", "")

    # Return XML corresponding to colored map as a string
    return etree.tostring(document)
