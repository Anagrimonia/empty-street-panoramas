import React from 'react';
import styles from "../App.css";

// Search Bar Component
class SearchBar extends React.Component { 
    render() {
        return (
            <input id='pac-input' placeholder='Search for place...' type='search' className='search-bar'/>
        );
    }
}

export default SearchBar;