import React from 'react';
import styles from "../App.css";

// Header Bar Component
class HeaderBar extends React.Component { 
    render() {
        return (
            <div className="header-bar">
                <img className='header-bar__logo' src='static/logo.png' ></img>
            </div>
        );
    }
}

export default HeaderBar;