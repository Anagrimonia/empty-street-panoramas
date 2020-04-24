import React from 'react';
import styles from "./App.css";

import HeaderBar from './HeaderBar'
import SearchBar from './SearchBar'
import MenuWrapper from './MenuWrapper'
import ResultWrapper from './ResultWrapper'

// Main Component
class App extends React.Component {

    state = {
        coords: { lat: 55.80659245645836, lng: 37.54190777403561 },
        isLoading: false,
        image: 'static/init.jpg',
        message: {text: '', color: ''}
    };

    // Life cycle function (is called after component mounting)
    componentDidMount() {

        // Create a map
        var map = new google.maps.Map(document.getElementById('map'), {
            center: this.state.coords,
            zoom: 14
        });

        // Create a search input
        var input = document.getElementById('pac-input');
        var searchBox = new google.maps.places.SearchBox(input);

        // Create a panorama viewer
        var panorama = new google.maps.StreetViewPanorama(document.getElementById('pano'), {
                position: this.state.coords,
                pov: {
                heading: 34,
                pitch: 10
            }
        });

        // Set panorama viewer to the map
        map.setStreetView(panorama);

        // Listen panorama position changing 
        panorama.addListener('position_changed', () => {
            var obj = panorama.getPosition();
            this.setState({ coords: { lat: obj.lat(), lng: obj.lng() }});
        });

        var markers = [];
        // Listen for the event fired when the user selects a prediction and retrieve
        // more details for that place
        searchBox.addListener('places_changed', function() {
            var places = searchBox.getPlaces();
            if (places.length == 0) return;

            // Clear out the old markers
            markers.forEach(function(marker) {
              marker.setMap(null);
            });

            markers = [];

            // For each place, get the icon, name and location.
            var bounds = new google.maps.LatLngBounds();

            places.forEach(function(place) {
                  if (!place.geometry) {
                    console.log("Returned place contains no geometry");
                    return;
                }
                var icon = {
                    url: place.icon,
                    size: new google.maps.Size(71, 71),
                    origin: new google.maps.Point(0, 0),
                    anchor: new google.maps.Point(17, 34),
                    scaledSize: new google.maps.Size(25, 25)
                };

                // Create a marker for each place.
                markers.push(new google.maps.Marker({
                    map: map,
                    icon: icon,
                    title: place.name,
                    position: place.geometry.location
                }));

                if (place.geometry.viewport)
                    bounds.union(place.geometry.viewport);
                else 
                    bounds.extend(place.geometry.location);
            });

            map.fitBounds(bounds);
        });      

        // ----===== Disable redirection while uploading an image =====-----

        document.getElementById("uploadBtn").onchange = function () {
            document.getElementById("uploadFile").value = this.value.replace("C:\\fakepath\\", "");
        };

    }

    // Function of Google Panorama processing request
    handleClearGooglePano = () => {

        // Set loading layout
        this.setState({ isLoading: true,
                        message: { text:'Getting Google Panorama...', color: 'white' } });

        // Request an image
        fetch('http://localhost:5000/getpano?x=' + this.state.coords.lat + '&y=' + this.state.coords.lng )
        .then(res => {
            // Unset loading layout
            this.setState({ isLoading: false });

            if (res.status == 200)
                return res.blob()

            if (res.status == 400)
                return res.text()

            if (res.status == 500) 
                return this.setState({ message: { text: 'Server error 500', color: 'red' } });

        })
        .then(blob => {

            if (typeof blob === 'string') 
                return this.setState({ message: { text: blob, color: 'red' } });

            var img = URL.createObjectURL(blob);
            this.setState({ image: img });
            this.setState({ image: img,
                            message: { text:'Done!', color: 'green' } });

            this.handleClearUploaded(blob)

        })
    };

    // Function of user image processing request
    handleClearUploaded = (file) => {

        //const file = document.querySelector('input[type="file"]').files[0]
        const formData = new FormData();
        formData.append('filedata', file);

        // Set loading layout
        this.setState({ isLoading: true,
                        message: { text:'Processing an image...', 
                                   color: 'white' } });

        // Request an image
        fetch('http://localhost:5000/remove', {method: 'POST', body: formData })
        .then(res => {
            // Unset loading layout
            this.setState({ isLoading: false });

            if (res.status == 200)
                return res.blob()

            if (res.status == 400)
                return res.text()

            if (res.status == 500) 
                return this.setState({ message: { text: 'Server error 500', 
                                                  color: 'red' } });

        })
        .then(blob => {

            if (typeof blob === 'string') 
                return this.setState({ message: { text: blob, 
                                                  color: 'red' } });

            var img = URL.createObjectURL(blob);
            this.setState({ image: img,
                            message: { text:'Done!', 
                                       color: 'green' } });
        })
    };

    render() {
        return (
            <div id='test' className='container' style={{backgroundImage: 'url(' + this.state.image + ')'}}>
                <HeaderBar />
                <div className='content-wrapper'>
                    <SearchBar />
                    <div id="map"></div>
                    <div id="pano"></div>
                    <MenuWrapper handleClearGooglePano={this.handleClearGooglePano}
                                 handleClearUploaded={this.handleClearUploaded}  
                                 image={this.state.image}
                                 message={this.state.message}
                                 isLoading={this.state.isLoading}/>
                    
                </div>
                <ResultWrapper  image={this.state.image} />
                <p className='footer'>Anastasiia Kolonskaia. HSE 2019-2020</p>
            </div>
        );
    }
}

export default App;