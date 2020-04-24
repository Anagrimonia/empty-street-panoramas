# empty-street-panoramas
Program for Detecting and Removing Unwanted Objects from Street View Panoramic Images Based on Deep Learning Algorithms.\
HSE Coursework 2019-2020

## Installation

- Go to [Google Cloud Platform](https://console.cloud.google.com/) and get an API Token for using Google Maps Street View.\
Add token to ./src/index.html and ./server/server.py.
- Download Pix2Pix weights from [Google Drive](https://drive.google.com/open?id=1hCMmaPRyl2nLeTOgP4wMuygEPsR3WyB3) and put them in ./server/models/weights.
- Download necessary node modules: `npm install`.
- Run hosting NodeJS server: `node server/app.js`.
- Run Python server: `python server/server.py`.
- Go to localhost:3000.
