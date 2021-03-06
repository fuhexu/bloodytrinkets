# File for handling all Highcharts

import datetime
import json
# Library to look for files and create them if needed
import os
import settings


##
## @brief      Gets the dps ilevel borders which helds dps values of a trinket.
##
## @param      trinket  The trinket with all ilevel dps values
##
## @return     The lowest ilevel and highest dps ilevel as string in a list
##             [lowest, highest].
##
def __get_dps_ilevel_borders(trinket):
  # this value should be greater than any possible ilevel value
  lowest_ilevel = "1200"
  highest_ilevel = "0"

  for ilevel in trinket:
    if int(ilevel) < int(lowest_ilevel) and trinket[ilevel] != "0":
      lowest_ilevel = ilevel
    if int(ilevel) > int(highest_ilevel) and trinket[ilevel] != "0":
      highest_ilevel = ilevel

  return [lowest_ilevel, highest_ilevel]


##
## @brief      Generates js output for http://www.highcharts.com/ bars of
##             http://www.stormearthandlava.com/elemental-shaman-hub/elemental-trinket-sims/
##
## @param      trinket_list           The normalised trinkets dictionary
##                                    {trinket_name s:{ilevel s:{dps s}}}
## @param      ordered_trinket_names  The ordered trinket names
## @param      filename               The filename
## TODO        Rewrite                Rewrite this whole function to use actual data types and
##                                    and convert that into json itself.
##
## @return     True if writing to file was successfull
##  
def print_highchart(trinket_list, ordered_trinket_names, filename):
  # let's create a real structure...
  categories = []
  for name in ordered_trinket_names:
    categories.append(name)

  # data handle for all series
  series = []

  # create legendary data for series
  series_legendaries_data = []
  for trinket_name in ordered_trinket_names:
    series_legendaries_data.append(int(trinket_list[trinket_name][settings.legendary_ilevel]))

  series_legendaries = {
    "name": settings.legendary_ilevel,
    "color": settings.legendary_colour,
    "data": series_legendaries_data
  }
  series.append(series_legendaries)

  ## handle all normal itemlevels data for series
  for i in range(0, len(settings.ilevels)):
    ilevel = settings.ilevels[i]
    if i < len(settings.ilevels) - 1:
      next_ilevel = settings.ilevels[i + 1]
    else:
      next_ilevel = False

    series_ilevel_data = []

    for trinket_name in ordered_trinket_names:
      lowest_dps_ilevel, highest_dps_ilevel = __get_dps_ilevel_borders(trinket_list[trinket_name])
      # if it's the lowest itemlevel, just print the values
      if ilevel == settings.ilevels[-1]:
        series_ilevel_data.append(int(trinket_list[trinket_name][ilevel]))
      else:
        # if a trinket doesn't have the current ilevel, or for some unknown reason the dps value couldn't be generated
        if trinket_list[trinket_name][ilevel] == "0":
          # if the dps of trinket wasn't saved from the sim-run, print the average of the former and later
          if int(ilevel) > int(lowest_dps_ilevel) and int(ilevel) < int(highest_dps_ilevel):
            series_ilevel_data.append( 
              int( 
                ( 
                  int( trinket_list[trinket_name][settings.ilevels[i - 1]] ) - int( trinket_list[trinket_name][settings.ilevels[i + 1]] ) 
                ) / 2.0
              ) 
            )
          else:
            series_ilevel_data.append(0)
        else:
          if int(trinket_list[trinket_name][ilevel]) - int(trinket_list[trinket_name][next_ilevel]) < 0:
            series_ilevel_data.append(0)
          elif trinket_list[trinket_name][next_ilevel] == "0" and int(next_ilevel) > int(lowest_dps_ilevel):
            series_ilevel_data.append(
              int(
                (
                  int( trinket_list[trinket_name][ilevel] ) - int( trinket_list[trinket_name][settings.ilevels[i + 2]] )
                ) / 2.0
              )
            )
          else:
            series_ilevel_data.append(
                int( trinket_list[trinket_name][ilevel] ) - int( trinket_list[trinket_name][next_ilevel] )
            )

    # create series ilevel dictionars
    series_ilevel = {
      "name": ilevel,
      "color": settings.graph_colours[ilevel],
      "data": series_ilevel_data
    }

    # add dictionary to series
    series.append(series_ilevel)


  highcharts_data = {
    "chart": {
      "type": "bar"
    },
    "title": {
      "text": settings.graph_title
    },
    "subtitle": {
      "text": "Last generated: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    "xAxis": {
      "categories": categories
    },
    "yAxis": {
      "min": 0,
      "title": {
        "text": '\\u0394 Damage per second'
      },
      "labels": {
        "enabled": True
      },
      "stackLabels": {
        "enabled": False,
        "style": {
          "fontWeight": "bold",
          "color": "'''(Highcharts.theme && Highcharts.theme.textColor) || 'white''''" 
        }
      }
    },
    "legend": {
      "align": "right",
      "x": 0,
      "verticalAlign": "bottom",
      "y": 0,
      "floating": False,
      "backgroundColor": "'''(Highcharts.theme && Highcharts.theme.background2) || 'white''''",
      "borderColor": '#CCC',
      "borderWidth": 1,
      "shadow": False,
      "reversed": True
    },
    "tooltip": {
      "headerFormat": "<b>{point.x}</b>",
      "formatter": """'''function() {
        var s = '<b>'+ this.x +'</b>';
        var cumulative_amount = 0;
        for (var i = this.points.length - 1 ; i >= 0 ; i--) {
            cumulative_amount += this.points[i].y;
            if (this.points[i].y !== 0){
                s += '<br/><span style=\"color: ' + this.points[i].series.color + '; font-weight: bold;\">' + this.points[i].series.name +'</span>: ' + cumulative_amount;
            }
        }
        return s;
      }'''""",
      "shared": True,
      "backgroundColor": "#eee",
      "borderColor": "#bbb",
      "style": {
        "color": "black"
      }
    },
    "plotOptions": {
      "series": {
        "borderColor": "#151515",
        "events": {
          "legendItemClick": "'''function() { return false; }'''"
        }
      },
      "bar": {
        "stacking": "normal",
        "dataLabels": {
          "enabled": False,
          "color": "'''(Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white''''"
        }
      }
    },
    "series": series
  }

  # write raw file
  with open(filename + "_raw.js", "w") as ofile:
    ofile.write("Highcharts.chart('" + filename[10:] + "', \n")
    json.dump(highcharts_data, ofile, indent=4, sort_keys=True)
    ofile.write(");")
  
  # create result file without quotes in inappropriate places
  with open(filename + "_raw.js", "r") as old:
    with open(filename + ".js", "w") as new:
      for line in old:
        # get rid of quotes for key ("key": "value")
        if "\":" in line:
          newline = line.split("\":")[0].replace("\"", "")
          line = newline + ":" + line.split("\":")[1]
        # get rid of quotes around our functions
        if "\"'''" in line or "'''\"" in line:
          newline = line.replace("\"'''", "\\n").replace("'''\"", "\\n").replace("\\n", "")
          new.write(newline)
        elif "\\\\u" in line:
          newline = line.replace("\\\\u", "\\u")
          new.write(newline)
        else:
          new.write(line)
  # delete raw file
  os.remove(filename + "_raw.js")
  return True



#  with open(filename + ".js", "w") as ofile:
#    ofile.write("Highcharts.chart('" + settings.simc_settings["class"] + "_" + settings.simc_settings["spec"] + "', {\n")
#    ofile.write("    chart: {\n")
#    ofile.write("        type: 'bar'\n")
#    ofile.write("    },\n")
#    ofile.write("    title: {\n")
#    ofile.write("        text: '" + settings.graph_title + "'\n")
#    ofile.write("    },\n")
#    ofile.write("    subtitle: {\n")
#    ofile.write("        text: 'Last generated: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "'\n")
#    ofile.write("    },\n")
#    ofile.write("    xAxis: {\n")
#    ofile.write("        categories: [")
#    for name in ordered_trinket_names:
#      ofile.write('"' + name + '"')
#      if not name == ordered_trinket_names[-1]:
#        ofile.write(",")
#    ofile.write("]\n")
#    ofile.write("    },\n")
#    ofile.write("    yAxis: {\n")
#    ofile.write("        min: 0,\n")
#    ofile.write("        title: {\n")
#    #Δ -> u0394
#    ofile.write("            text: '\\u0394 Damage per second'\n")
#    ofile.write("        },\n")
#    ofile.write("        labels: {\n")
#    ofile.write("            enabled: true\n")
#    ofile.write("        },\n")
#    ofile.write("        stackLabels: {\n")
#    ofile.write("            enabled: false,\n")
#    ofile.write("            style: {\n")
#    ofile.write("                fontWeight: 'bold',\n")
#    ofile.write("                color: (Highcharts.theme && Highcharts.theme.textColor) || 'white'\n")
#    ofile.write("            }\n")
#    ofile.write("        }\n")
#    ofile.write("    },\n")
#    ofile.write("    legend: {\n")
#    ofile.write("        align: 'right',\n")
#    ofile.write("        x: 0,\n")
#    ofile.write("        verticalAlign: 'bottom',\n")
#    ofile.write("        y: 0,\n")
#    ofile.write("        floating: false,\n")
#    ofile.write("        backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || 'white',\n")
#    ofile.write("        borderColor: '#CCC',\n")
#    ofile.write("        borderWidth: 1,\n")
#    ofile.write("        shadow: false,\n")
#    ofile.write("        reversed: true\n")
#    ofile.write("    },\n")
#    ofile.write("    tooltip: {\n")
#    ofile.write("        headerFormat: '<b>{point.x}</b>',\n")
#    ofile.write("        formatter: function() {\n")
#    ofile.write("            var s = '<b>'+ this.x +'</b>',\n")
#    ofile.write("            cumulative_amount = 0;\n")
#    ofile.write("            for (var i = this.points.length - 1 ; i >= 0 ; i--) {\n")
#    ofile.write("                cumulative_amount += this.points[i].y;\n")
#    ofile.write("                if (this.points[i].y !== 0){\n")
#    ofile.write("                    s += '<br/><span style=\"color: ' + this.points[i].series.color + '; font-weight: bold;\">' + this.points[i].series.name +'</span>: ' + cumulative_amount; \n")
#    ofile.write("                }\n")
#    ofile.write("            }\n")
#    ofile.write("            return s;\n")
#    ofile.write("        },\n")
#    ofile.write("        shared: true,\n")
#    ofile.write("        backgroundColor: '#eee',\n")
#    ofile.write("        borderColor: '#bbb',\n")
#    ofile.write("        style: {\n")
#    ofile.write("            color: 'black'\n")
#    ofile.write("        }\n")
#    ofile.write("    },\n")
#    ofile.write("    plotOptions: {\n")
#    ofile.write("        series: {\n")
#    ofile.write("            borderColor: '#151515',\n")
#    ofile.write("            events: {\n")
#    ofile.write("                legendItemClick: function () {\n")
#    ofile.write("                    return false; \n")
#    ofile.write("                }\n")
#    ofile.write("            }\n")
#    ofile.write("        },\n")
#    ofile.write("        bar: {\n")
#    ofile.write("            stacking: 'normal',\n")
#    ofile.write("            dataLabels: {\n")
#    ofile.write("                enabled: false,\n")
#    ofile.write("                color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white'\n")
#    ofile.write("            }\n")
#    ofile.write("        },\n")
#    ofile.write("    },\n")
#    ofile.write("    series: [")
#
#    ## handle all legendaries
#    ofile.write("{\n")
#    ofile.write("        name: '" + settings.legendary_ilevel + "',\n")
#    ofile.write("        color: '" + settings.legendary_colour + "',\n")
#    ofile.write("        data : [")
#
#    for trinket_name in ordered_trinket_names:
#      ofile.write(trinket_list[trinket_name][settings.legendary_ilevel])
#      if trinket_name != ordered_trinket_names[-1]:
#        ofile.write(",")
#    ofile.write("]\n")
#    ofile.write("    }")
#
#
#    ## handle all normal itemlevels
#    for i in range(0, len(settings.ilevels)):
#      ilevel = settings.ilevels[i]
#      if i < len(settings.ilevels) - 1:
#        next_ilevel = settings.ilevels[i + 1]
#      else:
#        next_ilevel = False
#      ofile.write(", {\n")
#      ofile.write("        name: '" + ilevel + "',\n")
#      ofile.write("        color: '" + settings.graph_colours[ilevel] + "',\n")
#      ofile.write("        data: [")
#
#      for trinket_name in ordered_trinket_names:
#        lowest_dps_ilevel, highest_dps_ilevel = __get_dps_ilevel_borders(trinket_list[trinket_name])
#        # if it's the lowest itemlevel, just print the values
#        if ilevel == settings.ilevels[-1]:
#          ofile.write(trinket_list[trinket_name][ilevel])
#        else:
#          # if a trinket doesn't have the current ilevel, or for some unknown reason the dps value couldn't be generated
#          if trinket_list[trinket_name][ilevel] == "0":
#            # if the dps of trinket wasn't saved from the sim-run, print the average of the former and later
#            if int(ilevel) > int(lowest_dps_ilevel) and int(ilevel) < int(highest_dps_ilevel):
#              ofile.write( 
#                str( 
#                  int( 
#                    ( 
#                      int( trinket_list[trinket_name][settings.ilevels[i - 1]] ) - int( trinket_list[trinket_name][settings.ilevels[i + 1]] ) 
#                    ) / 2.0
#                  ) 
#                )
#              )
#            else:
#              ofile.write("0")
#          else:
#            if int(trinket_list[trinket_name][ilevel]) - int(trinket_list[trinket_name][next_ilevel]) < 0:
#              ofile.write("0")
#            elif trinket_list[trinket_name][next_ilevel] == "0" and int(next_ilevel) > int(lowest_dps_ilevel):
#              ofile.write(
#                str(
#                  int(
#                    int( trinket_list[trinket_name][ilevel] ) - int( trinket_list[trinket_name][settings.ilevels[i + 2]] )
#                  ) / 2.0
#                )
#              )
#            else:
#              ofile.write(
#                str(
#                  int( trinket_list[trinket_name][ilevel] ) - int( trinket_list[trinket_name][next_ilevel] )
#                )
#              )
#
#        # if it's not the last trinket in the trinket list, add a comma
#        if not trinket_name == ordered_trinket_names[-1]:
#          ofile.write(",")
#
#      ofile.write("]\n")
#      ofile.write("    }")
#
#    ofile.write("]\n")
#    ofile.write("});\n")
#    return True
#  return False
