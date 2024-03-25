There are 2 files attached in this repository:
- AITools
- AIToolsHelperFunctions

AITools file is a frame of the script intent of which is to pull functions from an auxilary file AIToolsHelperFunctions.
Breakdown of the script:
1. Takes an array of links and begins iteration
2. a. Visits each link and scrapes the visible strings
   b. Extracts all the links from the navigation bar
   c. Scrapes the visible strings from the extracted navlinks
3. Creates a separate txt file for every link it visited and records extracted visible strings

   
