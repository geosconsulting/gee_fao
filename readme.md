
## Welcome to WaPOR’s documentation!

The FAO Water Productivity Open-acces portal uses Remote sensing technologies to monitor and report on agriculture water productivity over Africa and the Near East. WaPOR. For more information on how to use the library API Documentation
Program Parameters.


usage: wpMain.py [-h] **[-a Year | -d Start End Dates Start End Dates]** *[-c | -m]
    [-e {u,d,a,g,n}] [-i] [-r REPLACE] [-t {agbp,eta,aet,npp}] [-s AREALSTAT] [-v]*
    
- bold = mandatory

- italic = optional

Arguments:

    -h, --help 	show this help message and exit
    -a Year, --annual Year
     	Calculate Water Productivity Annually - Year must be provided

    -d Start End Dates Start End Dates, –dekadal Start End Dates Start End Dates
        Calculate Water Productivity for dekads - Starting and ending date must be provided with the following format YYYY-MM-DD

    -c, --chart 	Each calculated component (AGBP, AET, WPm) shown on a chart
    -m, --map 	Show the final output overlaid on Google Map

    -e {u,d,a,g,n}, –export {u,d,a,g,n}
        Choose export to url(-u), drive (-d), asset (-t) or geoserver (-g)

    -i, --map_id 	Generate map id for generating tiles
    -r REPLACE, --replace REPLACE
     	Replace the Above Ground Biomass Production with Net Primary Productivity multiplied by a constant value. Sending -s 1.25 will set agbp=npp * 1.25. If not provided default datasets will be used instead

    -t {agbp,eta,aet,npp}, –timeseries {agbp,eta,aet,npp}
        Time Series from data collections stored in GEE for the chosen country/dataset

    -s AREALSTAT, --arealstat AREALSTAT
     	Zonal statistics form a WaterProductivity layer generated on the fly in GEE for the chosen country
    -v, --verbose 	Increase output verbosity

### Simple Use

Calculate Water Productivity betweeen 1st of January 2015 and 30th of January 2015 outuput to a map viewer statistics calculated for Benin and generate map ID

    wpMain.py -d 2015-1-1 2015-1-30 -m -s “Benin” -i

Calculate Water Productivity for 2015 output to a chart

    wpMain.py -a 2015 -c

Calculate Water Productivity betweeen 1st of January 2015 and 30th of January 2015 replacing Above Ground Biomass Production with Net Primary Productivity multuplied by 1.25.

No output

    wpMain.py -d 2015-1-1 2015-1-30 -r 1.25

