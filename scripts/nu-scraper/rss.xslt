<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/channel">
 <html>
  <head>
    <title><xsl:value-of select="description"/></title>
    <style>
      * { box-sizing: border-box; }
      table {
        border-spacing: 0px;
        border-collapse: collapse;
        width: 100%;
        max-width: 100%;
        margin-bottom: 15px;
        background-color: transparent; /* Change the background-color of table here */
        text-align: left; /* Change the text-alignment of table here */
      }
      th { font-weight: bold; padding: 8px; bgcolor="#9acd32"}
      tr:nth-child(2) { border: 1px solid Grey; }
      td { padding: 8px; }
    </style>
  </head>
  <body>
    <center><h2><xsl:value-of select="description"/> RSS Feed/h2></center>
    <table border="1">
      <tr>
        <th>Release</th>
        <th>Publish Date</th>
      </tr>
      <xsl:for-each select="item">
      <tr>
        <td>
          /*<a href="{link}" title="{description}"><xsl:value-of select="title"/></a>*/
          <xsl:element name="a">
            <xsl:attribute name="href">
              <xsl:value-of select="link"/>
            </xsl:attribute>
            <xsl:attribute name="title">
              <xsl:value-of select="description"/>
            </xsl:attribute>
            <xsl:value-of select="title"/>
          </xsl:element>
        </td>
        <td><xsl:value-of select="pubDate"/></td>
      </tr>
      </xsl:for-each>
    </table>
  </body>
</html>
</xsl:template>

</xsl:stylesheet>
