"""
Nomisweb census data interactive query builder
See README.md for details on how to use this package
"""

import sys
import ukcensusapi.Nomisweb as Api

class Query:
  """
  Census query functionality
  """

  def __init__(self, api):
    self.api = api

  def table(self):
    """
    Interactive census table query
    """

    print("Nomisweb census data interactive query builder")
    print("See README.md for details on how to use this package")

    table = input("Census table: ")

    query_params = {}
    query_params["date"] = "latest"
    query_params["select"] = "GEOGRAPHY_CODE,"

    # select fields/categories from table
    meta = self.api.get_metadata(table)
    print(meta["description"])
    for field in meta["fields"]:
      if field != "GEOGRAPHY" and field != "FREQ":
        print(field + ":")
        for category in meta["fields"][field]:
          print("  " + str(category) + " (" + meta["fields"][field][category] + ")")
        categories = input("Select categories (default 0): ")
        include = True
        if categories == "":
          include = input("include in output (y/n, default=n)? ") == "y"
          categories = "0"
        query_params[field] = categories
        if field != "MEASURES" and include:
          query_params["select"] += field + ","

    query_params["select"] += "OBS_VALUE"

    add_geog = input("Add geography? (y/N): ") == "y"
    if add_geog:
      query_params["geography"] = self.__add_geog()
      #print(query_params)

      get_data = input("Get data now? (y/N): ") == "y"
      if get_data:
        print("\n\nGetting data...")

        # Fetch (and cache) data
        self.api.get_data(table, meta["nomis_table"], query_params)

    # Remove API key in example code (lest it be accidentally committed)
    if "uid" in query_params:
      del query_params["uid"]

    self.api.write_metadata(table, meta)

    self.write_code_snippets(table, meta, query_params)

  # returns a geography string that can be inserted into an existing query
  def get_geog_from_names(self, coverage, resolution):
    """
    Return a set of nomisweb geography codes for areas within the specified coverage at the specified resolution
    """

    # Convert the coverage area into nomis codes
    coverage_codes = self.api.get_lad_codes(coverage)
    return self.api.get_geo_codes(coverage_codes, resolution)

  def __add_geog(self):

    coverage = input("\nGeographical coverage\nE/EW/GB/UK or LA name(s), comma separated: ")
    resolution = input("Resolution (LA/MSOA/LSOA/OA): ")

    if resolution == "LA":
      resolution = Api.Nomisweb.LAD
    elif resolution == "MSOA11":
      resolution = Api.Nomisweb.MSOA11
    elif resolution == "LSOA11":
      resolution = Api.Nomisweb.LSOA11
    elif resolution == "OA11":
      resolution = Api.Nomisweb.OA11
    elif resolution == "MSOA01":
      resolution = Api.Nomisweb.MSOA01
    elif resolution == "LSOA01":
      resolution = Api.Nomisweb.LSOA01
    # elif resolution == "OA01":
    #   resolution = Api.Nomisweb.OA01
    else:
      print("Invalid resolution")
      sys.exit()

    if coverage == "E":
      coverage_codes = [Api.Nomisweb.England]
    elif coverage == "EW":
      coverage_codes = [Api.Nomisweb.EnglandWales]
    elif coverage == "GB":
      coverage_codes = [Api.Nomisweb.GB]
    elif coverage == "UK":
      coverage_codes = [Api.Nomisweb.UK]
    else:
      coverage_codes = self.api.get_lad_codes(coverage.split(","))

    area_codes = self.api.get_geo_codes(coverage_codes, resolution)
    return area_codes

  def write_code_snippets(self, table, meta, query_params):
    """
    Write out python and R code snippets, based on the supplied query, for later use
    """
    print("\nWriting python code snippet to " + self.api.cache_dir + table + ".py")
    with open(self.api.cache_dir + table + ".py", "w") as py_file:
      py_file.write("\"\"\"\n" + meta["description"])
      py_file.write("\n\nCode autogenerated by UKCensusAPI\n")
      py_file.write("(https://github.com/virgesmith/UKCensusAPI)\n\"\"\"")
      py_file.write("\n\n# This code requires an API key, see the README.md for details")
      py_file.write("\n\n# Query url:\n# " + self.api.get_url(meta["nomis_table"], query_params))
      py_file.write("\n\nimport ukcensusapi.Nomisweb as CensusApi")
      py_file.write("\n\napi = CensusApi.Nomisweb(\"" + self.api.cache_dir + "\")")
      py_file.write("\ntable = \"" + table + "\"")
      py_file.write("\ntable_internal = \"" + meta["nomis_table"] + "\"")
      py_file.write("\nquery_params = {}")
      for key in query_params:
        py_file.write("\nquery_params[\""+key+"\"] = \""+query_params[key]+"\"")
      if not "geography" in query_params:
        py_file.write("\n# TODO query_params[\"geography\"] = ...")
      py_file.write("\n" + table + " = api.get_data(table, table_internal, query_params)\n")

    print("\nWriting R code snippet to " + self.api.cache_dir + table + ".R")
    with open(self.api.cache_dir + table + ".R", "w") as r_file:
      r_file.write("# " + meta["description"])
      r_file.write("\n\n# Code autogenerated by UKCensusAPI")
      r_file.write("\n#https://github.com/virgesmith/UKCensusAPI")
      r_file.write("\n\n# This code requires an API key, see the README.md for details")
      r_file.write("\n# Query url: " + self.api.get_url(meta["nomis_table"], query_params))
      r_file.write("\n\nlibrary(\"UKCensusAPI\")")
      r_file.write("\ncacheDir = \"" + self.api.cache_dir + "\"")
      r_file.write("\napi = UKCensusAPI::instance(cacheDir)")
      r_file.write("\ntable = \"" + table + "\"")
      r_file.write("\ntable_internal = \"" + meta["nomis_table"] + "\"")
      r_file.write("\nqueryParams = list(")
      first = True
      for key in query_params:
        if first:
          r_file.write("\n  "+key+" = \""+query_params[key] + "\"")
          first = False
        else:
          r_file.write(",\n  "+key+" = \""+query_params[key] + "\"")
      if not "geography" in query_params:
        r_file.write("\n  # TODO add geography parameter to this query...")
      r_file.write("\n)")
      r_file.write("\n" + table + " = UKCensusAPI::getData(api, table, table_internal, queryParams)\n")
