from zope.formlib import form
from zope.interface import implements
from zope import component
from zope.schema import getFields
from zope.schema import TextLine, Text, Choice
from zope.schema.vocabulary import SimpleVocabulary
from zope.pagetemplate.pagetemplatefile import PageTemplateFile

try:
    import json
except:
    import simplejson as json

from Products.CMFPlomino.fields.dictionaryproperty import DictionaryProperty
from Products.CMFPlomino.interfaces import IPlominoField
from Products.CMFPlomino.fields.base import IBaseField, BaseField, BaseForm

class ILeafletField(IBaseField):
    """
    Leaflet field schema
    """
    read_map_js = Text(title=u'Read mode settings',
                      description=u'Leaflet javascript code for read mode',
                      default=u"""
var map = new L.Map('leafletmapdiv', {doubleClickZoom: false});

/* YOUR TITES URL HERE */
var tilesLayer = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
map.attributionControl.setPrefix("OpenStreetMap");
//var tilesLayer = new L.TileLayer('http://{s}.tiles.mapbox.com/v3/mapbox.natural-earth-hypso-bathy/{z}/{x}/{y}.png');
//map.attributionControl.setPrefix("MapBox");

var geojsonLayer = new L.GeoJSON();

/* YOUR ORIGINAL LOCATION AND ZOOM LEVEL HERE */
map.setView(new L.LatLng(37, 16), 5);
/* OR AUTO-LOCATE THE USER */
// map.locate({setView: true});
map.addLayer(tilesLayer);
map.addLayer(geojsonLayer);

/* CUSTOM RENDERING */
geojsonLayer.on("featureparse", function(e) {
    if (e.properties) {
        if (e.properties.popupContent) {
            e.layer.bindPopup(e.properties.popupContent);
        }
        if (e.properties.style && e.layer.setStyle) {
            e.layer.setStyle(e.properties.style);
        }
        if (e.properties.radius && e.layer.setRadius) {
            e.layer.setRadius(e.properties.radius);
        }
    }
});

jq.getJSON(json_source, '', function(data){
    geojsonLayer.addGeoJSON(data);
    map.fitBounds(geojsonLayer.getBounds());
});
""",
                      required=False)
    edit_map_js = Text(title=u'Edit mode settings',
                      description=u'Leaflet javascript code for edit mode',
                      default=u"""
var map = new PlominoEditableMap('leafletmapdiv', {doubleClickZoom: false});

/* YOUR TITES URL HERE */
var tilesLayer = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
map.attributionControl.setPrefix("OpenStreetMap");
//var tilesLayer = new L.TileLayer('http://{s}.tiles.mapbox.com/v3/mapbox.natural-earth-hypso-bathy/{z}/{x}/{y}.png');
//map.attributionControl.setPrefix("MapBox");

var geojsonLayer = new PlominoEditableGeoJSON();

/* YOUR INITIAL LOCATION AND ZOOM LEVEL HERE */
map.setView(new L.LatLng(37, 16), 5)
   .addLayer(tilesLayer)
   .addLayer(geojsonLayer);

jq.getJSON(json_source, '', function(data){
    geojsonLayer.addGeoJSON(data);
    map.fitBounds(geojsonLayer.getBounds());
});
""",
                      required=False)
    
    find_location = Choice(vocabulary=SimpleVocabulary.fromItems([("In both edit and read mode", "BOTH"),
                                                           ("In read mode only", "READ"),
                                                           ("In edit mode only", "EDIT"),
                                                           ("Never", "NONE"),
                                                           ]),
                    title=u'Location finder',
                    description=u'Allow to center to map to a given location using geonames.org',
                    default="BOTH",
                    required=True)
    
    geonames_parameters = TextLine(title=u'Geonames extra parameters',
                      description=u'Added to geonames web services request, example: featureCode=P&country=FR to restrict to French cities.',
                      default=u"featureCode=P",
                      required=False)


class LeafletField(BaseField):
    """
    """
    implements(ILeafletField)

    plomino_field_parameters = {'interface': ILeafletField,
                                'label': "Leaflet map",
                                'index_type': "ZCTextIndex"}

    read_template = PageTemplateFile('leaflet_read.pt')
    edit_template = PageTemplateFile('leaflet_edit.pt')
    
    def getParameters(self, edit_mode=False):
        """
        """
        if edit_mode:
            js = self.edit_map_js
            js += """
jq("#plomino_form").submit(function() {
    jq("input[name='%s']").val(geojsonLayer.getGeoJSON());
});
""" % self.context.id
            return js
        else:
            return self.read_map_js

    def validate(self, submittedValue):
        """
        """
        errors=[]
        try:
            json.loads(submittedValue)
        except:
            errors.append(self.context.id + " must be a valid JSON.")
        return errors

    def processInput(self, submittedValue):
        """
        """
        return json.loads(submittedValue)

component.provideUtility(LeafletField, IPlominoField, 'LEAFLET')

for f in getFields(ILeafletField).values():
    setattr(LeafletField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(BaseForm):
    """
    """
    form_fields = form.Fields(ILeafletField)

