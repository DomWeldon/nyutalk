# Setup Process For London Pub Data

## Setting Up Neo4J and Required Plugins

1. Download [version 3.1 of Neo4J](https://neo4j.com/download/other-releases/) (not the latest version, due to a dependency on the spatial plugin) and install on your machine. On windows, the program runs as an executable, on Linux/Mac you should just be able to copy it to a folder on your machine (in my case) `~/Databases` and then decompress it, and you're good to go. On Windows, there is a GUI.[ A tutorial is available to help you install it](https://neo4j.com/docs/operations-manual/current/installation/).
2. Download the [Neo4J Spatial Plugin](https://github.com/neo4j-contrib/spatial/releases) for version 3.1 of Neo4J and copy the `.jar` file to your `$NEO4J_HOME/plugins` directory (`$NEO4J_HOME` is simply the root of the Neo4J directory you've set up on your computer).
3. Download [GraphAware Time Tree version 3.1.4](https://products.graphaware.com/?dir=timetree) and copy the `.jar` file to your `$NEO4J_HOME/plugins` directory.
4. Turn on Neo4J. On Linux/Mac, this can be done by navigating to `$NEO4J_HOME` to and typing `./bin/neo4j start`, on Windows, there is a GUI.

## Loading the Open Street Map

Now that Neo4J is running on our computer, we can put some basic spatial data (volunteered geographical information) into it from the [Open Street Map](https://www.openstreetmap.org/).

### Download the OSM

1. Download the [latest release of OSM data from Geofabrik as a shapefile (`.shp.zip`)](http://download.geofabrik.de/europe/great-britain.html). In this example, I do it for Greater London, but there's no reason you couldn't do it for another region.
2. Create a directory in the `$NEO4J_HOME/import` directory, and decompress the shapefile (which is composed of lots of individual files) into this directory.
3. You're now ready to import the spatial data into the database.

### Import it into the Graph

These operations take place int he Neo4J Browser. First, navigate to `http://localhost:7474/browser/` (you will need to login using the default credentials, and then set your own password).

#### Setup DB Layers

First for points of interest:

    CALL spatial.addPointLayer('pois')

Then for railways:

    CALL spatial.addPointLayer('railways')

And public transport:

    CALL spatial.addPointLayer('transport')

#### Now Add Points from the OSM

First, add all points of interest, in my download, this was as two files, and so required the two queries below (call one, then the other). For my download, it loaded around 48k and 30k points respectively.

    CALL spatial.importShapefileToLayer('pubs', 'neo4j-community-3.1.5/import/greater_london/gis.osm_pois_free_1.shp') YIELD count
    CALL spatial.importShapefileToLayer('pubs', 'neo4j-community-3.1.5/import/greater_london/gis.osm_pois_a_free_1.shp') YIELD count

(you may need to change the filename to suit your installation)

If you run a basic query now, you should see there are nodes in your database.

    MATCH (n) RETURN n LIMIT 25

You can also query to find useful data, for example, let's look at some possible queries for pubs:

    // how many pubs in our data set?
    MATCH (n) WHERE n.fclass = "pub" RETURN COUNT(n)
    // let's see some - click and play around with the bubbles to see what is nearby!
    MATCH (n) WHERE n.fclass = "pub" RETURN n LIMIT 25
    // find a pub near me:
    // KCL Drury Lane Campus: { lon: -0.12300605702061, lat: 51.5149124137111 }
    // find within 500m
    CALL spatial.withinDistance('pois', { lon: -0.12300605702061, lat: 51.5149124137111 }, 0.5) YIELD node
    WITH node AS n
    WHERE n.fclass = "pub"
    RETURN n
    // WOW! There are lots of pubs in Central London. Let's try 200m:
    CALL spatial.withinDistance('pois', { lon: -0.12300605702061, lat: 51.5149124137111 }, 0.2) YIELD node
    WITH node AS n
    WHERE n.fclass = "pub"
    RETURN n
    // recognise a few names? right, we're good to go!

#### Label Features We're Interested In

    // apply a label to all railway stations
    MATCH (n) WHERE n.fclass = "railway_station" SET n:RailwayStation RETURN n
    // likewise, pubs
    MATCH (n) WHERE n.fclass = "pub" SET n:Pub RETURN n

You can now set pubs and railway station labels to have specific colours and sizes in the browser, [like the results of the query below](images/pubs_and_stations_near_KCL.png).

    CALL spatial.withinDistance('transport', { lon: -0.12300605702061, lat: 51.5149124137111 }, 1) YIELD node
    WITH node as r WHERE r:RailwayStation
    CALL spatial.withinDistance('pois', { lon: -0.12300605702061, lat: 51.5149124137111 }, 1) YIELD node
    WITH r, node AS p WHERE p:Pub
    RETURN *

## Next Steps

[Download and Process Data](/docs/02_download_and_process.md)
