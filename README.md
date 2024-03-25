There are 2 files attached in this repository:
- AITools
- AIToolsHelperFunctions

AITools file is a base of the script intent of which is to pull functions from an auxilary file AIToolsHelperFunctions.</br></br>
Breakdown of the script:
1. Takes an array of links and begins iteration
2. a. Visits each link and scrapes the visible strings</br>
   b. Extracts all the links from the navigation bar</br>
   c. Scrapes the visible strings from the extracted navlinks
3. Creates a separate txt file for every link it visited with extracted visible strings and updates a logger of this action. If error is present for some reason, records the error and moves on

   
