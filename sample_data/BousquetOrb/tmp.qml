<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.6.1-Noosa" minScale="1e+08" maxScale="0" hasScaleBasedVisibilityFlag="0" styleCategories="AllStyleCategories">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <customproperties>
    <property value="false" key="WMSBackgroundLayer"/>
    <property value="false" key="WMSPublishDataSourceUrl"/>
    <property value="0" key="embeddedWidgets/count"/>
    <property value="Value" key="identify/format"/>
  </customproperties>
  <pipe>
    <rasterrenderer type="paletted" band="1" opacity="1" alphaBand="-1">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <colorPalette>
        <paletteEntry color="#d7191c" value="0" label="0" alpha="255"/>
        <paletteEntry color="#ea633e" value="5" label="5" alpha="255"/>
        <paletteEntry color="#fdae61" value="10" label="10" alpha="255"/>
        <paletteEntry color="#fed791" value="30" label="30" alpha="255"/>
        <paletteEntry color="#ffffc0" value="60" label="60" alpha="255"/>
        <paletteEntry color="#d3ec95" value="100" label="100" alpha="255"/>
        <paletteEntry color="#a6d96a" value="200" label="200" alpha="255"/>
        <paletteEntry color="#60b855" value="10000" label="10000" alpha="255"/>
        <paletteEntry color="#1a9641" value="20000" label="20000" alpha="255"/>
      </colorPalette>
      <colorramp name="[source]" type="gradient">
        <prop v="215,25,28,255" k="color1"/>
        <prop v="26,150,65,255" k="color2"/>
        <prop v="0" k="discrete"/>
        <prop v="gradient" k="rampType"/>
        <prop v="0.25;253,174,97,255:0.5;255,255,192,255:0.75;166,217,106,255" k="stops"/>
      </colorramp>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0"/>
    <huesaturation colorizeOn="0" saturation="0" grayscaleMode="0" colorizeStrength="100" colorizeRed="255" colorizeGreen="128" colorizeBlue="128"/>
    <rasterresampler maxOversampling="2"/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
