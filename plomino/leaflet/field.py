from zope.formlib import form
from zope.interface import implements
from zope import component
from zope.schema import getFields
from zope.schema import TextLine, Text, Choice
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
map.setView(new L.LatLng(37, 16), 5)
   .addLayer(tilesLayer)
   .addLayer(geojsonLayer);

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
var map = new L.Map('leafletmapdiv', {doubleClickZoom: false});

/* YOUR TITES URL HERE */
var tilesLayer = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
map.attributionControl.setPrefix("OpenStreetMap");
//var tilesLayer = new L.TileLayer('http://{s}.tiles.mapbox.com/v3/mapbox.natural-earth-hypso-bathy/{z}/{x}/{y}.png');
//map.attributionControl.setPrefix("MapBox");

var geojsonLayer = new L.GeoJSON();

/* YOUR ORIGINAL LOCATION AND ZOOM LEVEL HERE */
map.setView(new L.LatLng(37, 16), 5)
   .addLayer(tilesLayer)
   .addLayer(geojsonLayer);


geojsonLayer.on("featureparse", function(e) {
    if(e.layer.editing) {
        e.layer.editing.enable();
    }
    if(e.geometryType == "Point") {
        e.layer.options.draggable = true;
    }
});

jq.getJSON(json_source, '', function(data){
    geojsonLayer.addGeoJSON(data);
    map.fitBounds(geojsonLayer.getBounds());
});
""",
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
    var geometries = []
    geojsonLayer._iterateLayers(function(layer) {
        if(layer.getLatLng) {
            latlng = layer.getLatLng();
            geometries.push('{"type": "Feature", "geometry": {"type": "Point", "coordinates": [' + latlng.lng + ', '+latlng.lat+']}}');
        }
        if(layer.getLatLngs) {
            var latlngs = jq.map(layer.getLatLngs(), function (latlng) {
                return '[' + latlng.lng + ', '+latlng.lat+']';
            });
            geometries.push('{"type": "Feature", "geometry": {"type": "LineString", "coordinates": [' + latlngs.join(',') + ']}}');
        }
    }, geojsonLayer);
    geojson = '{"type": "FeatureCollection", "features": ['+geometries.join(',')+']}';
    jq("input[name='%s']").val(geojson);
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

