import React from 'react';
import styles from "../App.css";


// Result Window Component
class ResultWrapper extends React.Component { 
    render() {
        return (
            <div className='result-wrapper'>
                <img id='result' className='result' style={{backgroundImage: 'url(' + this.props.image + ')'}} ></img>
            </div>
        );
    }
}

export default ResultWrapper;