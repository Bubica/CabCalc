import matplotlib
from matplotlib import pyplot as pp
import struct
import numpy 

"""
DEBUGGING ONLY!

Handles KML representation of the traversed path (defined by the sequence of points).
Used for display purposes (debugging only).
"""
def _exportPath(latitude, longitude,  color="7f0000ff"):
    path = ""
    styId = "line"+color
    path = path + "<Style id=\""+styId+"\"><LineStyle><color>#ff"+color+"</color><width>4</width></LineStyle></Style>"
    path = path + "<Placemark><styleUrl>#"+styId+"</styleUrl><LineString>\n<extrude>1</extrude>\n<tessellate>1</tessellate>\n<altitudeMode>absolute</altitudeMode>\n"
    path = path + "<coordinates>" 

    for ilat, ilon in zip(latitude,longitude):
        path = path + str(ilat)+","+str(ilon)+",0\n"

    path = path +"</coordinates>\n</LineString>\n</Placemark>\n"
    return path

def _header():
    header = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    header = header+"<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n"
    header = header+"<Document>\n"
    return header

def _footer():   
    footer = "</Document>\n"
    footer = footer + "</kml>\n"
    return footer

"""
Returns the kml string that displays the route between given points.
"""
def route(latitude, longitude):
    #colors=['7f0000ff', '7f00ff00', '7fff0000','7f000000', '7fff00ff', '7f00ffff', '7fffff00']
    cmap = pp.get_cmap('spectral')

    doc = _header()
    if isinstance(latitude[0], list) and isinstance(longitude[0], list): # not a very pythonic way....
        l = len(latitude)
        for i in range(0, l):
            lng=longitude[i]
            lat=latitude[i]
            c= [int(i) for i in 255*numpy.array(cmap(i/(1.*l))[:-1])]; 
            color = struct.pack('BBB',*c).encode('hex')
            doc = doc + _exportPath(lng, lat, color=color)
    else:
        c= [int(i) for i in 255*numpy.array(cmap(0.5)[:-1])]
        print c
        color = struct.pack('BBB',*c).encode('hex')
        doc = doc + _exportPath(longitude, latitude, color=color)
    
    doc = doc+_footer()
    
    return doc
"""
Return the kml string that displays the collection of points.
"""
def points(dot_p=[], pin_p=[]):
    doc = _header()

    #Add the style
    doc = doc + """
    <open>1</open>
    <Style id="redDot">
      <IconStyle>
        <Icon>
          <href>https://storage.googleapis.com/support-kms-prod/SNP_2752125_en_v0</href>
        </Icon>
      </IconStyle>
      <LineStyle>
        <width>2</width>
      </LineStyle>
    </Style>
    <Style id="yellowPin">
      <IconStyle>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
        </Icon>
      </IconStyle>
      <LineStyle>
        <width>2</width>
      </LineStyle>
    </Style>
    """ 
    doc = doc + "<Folder>"
    
    for pi in dot_p:

        doc = doc + """
        <Placemark>
        <visibility>0</visibility>
        <styleUrl>#redDot</styleUrl>
        <Point>
          <altitudeMode>absolute</altitudeMode>
          <coordinates>"""
        doc = doc + str(pi[0]) +","+str(pi[1])
        doc = doc + """,0</coordinates>
        </Point>
        </Placemark>
        """

    for pi in pin_p:

        doc = doc + """
        <Placemark>
        <visibility>0</visibility>
        <styleUrl>#yellowPin</styleUrl>
        <Point>
          <altitudeMode>absolute</altitudeMode>
          <coordinates>"""
        doc = doc + str(pi[0]) +","+str(pi[1])
        doc = doc + """,0</coordinates>
        </Point>
        </Placemark>
        """


    doc = doc+"</Folder>"
    doc = doc+_footer()

    return doc


