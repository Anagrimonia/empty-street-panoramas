import React from 'react';
import styles from "../App.css";

// Menu Panel Wrapper Component
class MenuWrapper extends React.Component {

    state = {
        checked: false
    };

    // Change mode of processing panoramas/images
    changeMode = () => {
        this.setState({checked: !this.state.checked});
    };

    // Call request function of processing
    handleClear = () => {
        if (!this.state.checked) {
            this.props.handleClearGooglePano();
        }
        else {
            const file = document.querySelector('input[type="file"]').files[0]
            this.props.handleClearUploaded(file);
        }
    };

    render() {
        return (
            <div className='content-wrapper__menu'>
                <p className='text1'>Enhance panoramic view in one click by removing pedestrians and vehicle.</p>
                <p className='text1'>Deep Learning algorithms will do all the work.</p>

                <iframe name="dummyframe" id="dummyframe" style={{display: 'none'}}></iframe>

                <form id='form' target="dummyframe" action="/clear-uploaded" method="post" encType="multipart/form-data">
                    <input id="uploadFile" className="f-input" />
                    <div className="fileUpload btn btn--browse">
                        <p>Browse</p>
                        <input id="uploadBtn" type="file" name="body" className="upload" />
                    </div>
                </form>


                <div className='switch-wrapper'>
                    <p style={{textAlign: 'end'}}>Google Panorama</p>
                    <label className="switch">
                        <input type="checkbox" 
                               checked={this.state.checked} 
                               onChange={this.changeMode} />
                        <span className="slider round"></span>
                    </label>
                    <p>Uploaded Image</p>
                </div>
                
                <button disabled={this.props.isLoading} id='clear-button' className='clear-button' onClick={this.handleClear}>
                    Clear Image
                </button>

                <a className='download' href={this.props.image} download='result.jpg'>
                    <p>[Download]</p>
                </a>

                <p className='message' style={{color: this.props.message.color}}>
                    {this.props.message.text}
                </p>
            </div>
        );
    }
}



export default MenuWrapper;