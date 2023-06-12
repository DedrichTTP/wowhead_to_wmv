// Require the necessary modules
const axios = require("axios");
const cheerio = require("cheerio");
const path = require("path");
const argv = process.argv.splice(2);

// Asynchronous function to fetch texture data from a given texture ID
async function fetchTextureData(textureID) {
  // Construct the URL for the API call
  const url = `https://wow.tools/files/scripts/filedata_api.php?filedataid=${textureID}`;

  try {
    // Make the API call
    const response = await axios.get(url);
    // Load the response data into Cheerio
    const $ = cheerio.load(response.data);
    // Find all .blp files in the response
    const blpFiles = $("body").text().match(/[\w-]+\.blp/gi);

    if (blpFiles && blpFiles.length > 0) {
      // Return the name of the first .blp file found
      return path.parse(blpFiles[0]).name;
    } else {
      console.log(`No .blp file found for textureID ${textureID}`);
      return null;
    }
  } catch (error) {
    console.error(`Failed to fetch data for textureID ${textureID}`);
    return null;
  }
}

// Get the texture ID from the command line arguments
const textureID = argv[0];

if (!textureID) {
  console.error("Please provide a texture ID");
} else {
  // Fetch the texture data and log it to the console
  fetchTextureData(textureID).then((data) => {
    if (data !== null) {
      console.log(data);
    }
  });
}