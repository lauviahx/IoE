import React from 'react';
import Sketch from './sketch';
import Logo from './logo.png';
import './App.css';


function App() {

  return (
    <div className="App">
      <div className="Header">
        <img src={Logo} className="Logo" alt="logo" />
      </div>
      <div className="Intro">
        <h2>Enjoy the sound visualisation outside the room!</h2>
        <p>The person inside the room creates their own music by pressing keys on the MIDI keyboard with assigned samples. You can hear the created sounds and are able to see the sound spectrum visualisation here, in front of you.</p>
        <p>You will experience the most immersion inside the room and it is better to be the one in the control of the system, so get yourself inside!</p>
      </div>
      <p>If no connection is made, use random data button</p>
      <Sketch />
      {/* show sketch.js */}
    </div>
  );
}


export default App;

