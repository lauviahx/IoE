import React, { Component } from "react";
import Sketch from "react-p5";
import socketIOClient from "socket.io-client";
import { ChromePicker } from 'react-color';


export default class App extends Component {

  constructor() {
    super();
    this.state = {
      endpoint: "http://192.168.0.7:8081", // this is telling our socket.io client to connect to our bridge.js node local server on port 8081
      oscPortIn: 7500,
      oscPortOut: 3331, // this will configure our bridge.js node local server to receive OSC messages on port 7400
      draw: this.shape1, //set up state for p5 draw function, so shape1 will be showed on load until changed with buttons
      displayColorPicker: false, // set up state for colour pickers (hide)
      displayColorPicker2: false,
      color: '#EAFF00', // set up default colour for colour pickers
      color1: '#F77AED',
    };
    // this.oscRecieved = false;
    this.spectrum = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]; // array of number that MIDI cooperate with when connection made, only 16 items, hence the web visualisations are not really spectacular as with using p5.sound 

    this.spectrum = []; // if no connection made it will use the random array data, or until MIDI keys pressed
    for (let i = 0; i < 16; i++) {
      this.spectrum.push(Math.floor((Math.random() * 150) + 1));
    }

  }

  componentDidMount() {
    const { endpoint } = this.state; // using our endpoint from state object - this is a modern ES6 way of accessing elements from an object called destructuring assignment
    const { oscPortIn } = this.state; // using our in port for OSC from state object
    const { oscPortOut } = this.state; //
    const socket = socketIOClient(endpoint); // create an instance of our socket.io client
    socket.on('connect', function () { // connect and configure local server with settings from the state object
      socket.emit('config', {
        server: { port: oscPortIn, host: '192.168.0.7' },
        client: { port: oscPortOut, host: '192.168.0.7' },
      });
    });
    socket.on('message', (function (msg) { // once we receive a message, process it a bit then call this.receiveOSC()
      console.log("Something");
      if (msg[0] === '#bundle') { // treat it slightly differently if it's a bundle or not
        for (var i = 2; i < msg.length; i++) {
          this.receiveOsc(msg[i][0], msg[i].splice(1));
        }
      } else {
        this.receiveOsc(msg[0], msg.splice(1));
      }
    }).bind(this)); // we have to explicitly bind this to the upper execution context so that we can call this.receiveOSC()
  }

  receiveOsc(address, value) {
    console.log('connected');
    this.spectrum = value.map(function (x) { return x * 5; }); // map values to array
    console.log(this.spectrum);
    if (address === '/analogue') {
    }
  }


  s = 16;
  c = 255;

  //p5 code, three different shapes to show visualisation 
  setup = (p5, canvasParentRef) => {
    p5.createCanvas(800, 600).parent(canvasParentRef);
    p5.colorMode(p5.HSB); // color mode set to HSB to enable "rainbow" effect on first shape along with i value
    this.w = p5.width / this.s;
    p5.background(0);
  };

  shape1 = p5 => { // first shape with rectangles 
    p5.push();
    p5.beginShape();
    p5.background(0);
    p5.noStroke();
    for (this.i = 0; this.i < this.spectrum.length; this.i++) { // use the spectrum array
      this.amp = this.spectrum[this.i];
      this.y = p5.map(this.amp, 0, 140, p5.height, 0);
      p5.fill(this.i * 21, this.c, this.c);
      p5.rect(this.i * this.w, this.y, this.w - 5, p5.height - this.y); // create rectangles
    }
    p5.endShape();
    p5.pop();
  };

  shape2 = p5 => { // second shape with lines and dots, code based on last year work with p5.sound

    p5.background(0);
    p5.push();
    p5.beginShape();
    p5.translate(p5.width / 2, p5.height / 2); //translate to middle
    p5.rotate(p5.frameCount / (100 * p5.PI)); // rotate shape
    for (this.i = 0; this.i < this.spectrum.length; this.i++) {
      this.amp = this.spectrum[this.i];
      this.r = p5.map(this.amp, 0, 255, 400, 550);
      this.x = this.r * 0.5 * p5.cos(this.i);
      this.y = this.r * 0.5 * p5.sin(this.i);
      p5.strokeWeight(4);
      p5.stroke(255);
      p5.point(this.x, this.y); //create dots
    }
    p5.endShape();
    p5.pop();

    p5.push();
    p5.beginShape();
    p5.translate(p5.width / 2, p5.height / 2);
    p5.rotate(p5.frameCount / (100 * p5.PI));
    for (this.i = 0; this.i < this.spectrum.length; this.i++) {
      this.angle = p5.map(this.i, 0, this.spectrum.length, 0, 360);
      this.amp = this.spectrum[this.i];
      this.r = p5.map(this.amp, 0, 256, 20, 100);
      this.x = this.r * p5.cos(this.angle);
      this.y = this.r * p5.sin(this.angle);
      this.col = p5.color(this.state.color); // get state colour from colour picker
      p5.stroke(this.col); // use picker colour for fill
      p5.strokeWeight(3);
      p5.line(0, 0, this.x * 2.3, this.y * 2.3); //create lines
    }
    p5.endShape();
    p5.pop();
  }

  shape3 = p5 => { // third shape vertex https://p5js.org/examples/sound-frequency-spectrum.html

    p5.push();
    p5.beginShape();
    p5.background(0);
    this.col = p5.color(this.state.color1);
    p5.stroke(this.col);
    p5.strokeWeight(3);
    p5.noFill();
    for (this.i = 0; this.i < this.spectrum.length; this.i++) {
      this.amp = this.spectrum[this.i];
      p5.vertex(this.i * 60, p5.map(this.amp*1.3, 0, 255, p5.height, 0)); // create vertex i*60 to expand the visualisation due to original array being short
    }
    p5.endShape();
    p5.pop();
  };

  change = () => {
    this.setState({ draw: this.shape1 });
  } // change function to control button, set state draw function from p5 (different visualisation)

  changeTwo = () => {
    this.setState({ draw: this.shape2 });
  } // same as above but different shape to display

  changeThree = () => {
    this.setState({ draw: this.shape3 });
  }  // same as above but different shape to display


  // functions for colour picker from https://casesandberg.github.io/react-color/
  // including hiding/displaying on button clicked
  handleChangeComplete = (color) => {
    this.setState({ color: color.hex }); // using hex format
  };

  handleChangeComplete1 = (color1) => {
    this.setState({ color1: color1.hex });
  };
  handleClick = () => {
    this.setState({ displayColorPicker: !this.state.displayColorPicker })
  };

  handleClose = () => {
    this.setState({ displayColorPicker: false })
  };
  handleClick1 = () => {
    this.setState({ displayColorPicker2: !this.state.displayColorPicker2 })
  };

  handleClose1 = () => {
    this.setState({ displayColorPicker2: false })
  };

  randomData = () => { // function to create random array every time button pressed, so no need to refresh the page
    this.spectrum = [];
    for (let i = 0; i < 16; i++) {
      this.spectrum.push(Math.floor((Math.random() * 150) + 1));
    }
  }

  render() {
    const popover = { // set up for colour picker
      position: 'absolute',
      zIndex: '2',
    }
    const cover = {
      position: 'fixed',
      top: '0px',
      right: '0px',
      bottom: '0px',
      left: '0px',
    }
    return (
      <div>
        <button id="random" type="button" onClick={this.randomData}>Load random data</button> 
        {/* random data function button */}

        <div className="sketch"><Sketch setup={this.setup} draw={this.state.draw} />
          {/* display sketch depending on which one is set in set state by buttons, or default */}

          <div class="row">
            <div class="column">
              <button className="button" id="btn" type="button" onClick={this.change}>Visualisation 1</button>
              {/* create button and assign on click function */}
            </div>
            <div class="column">
              <button className="button" id="btn2" type="button" onClick={this.changeTwo}>Visualisation 2<br></br>
                {/* create button and assign on click function with colour picker inside*/}
                <button id="picker" onClick={this.handleClick}>Change Colour</button>
                {this.state.displayColorPicker ? <div style={popover}>
                  <div style={cover} onClick={this.handleClose} />
                  <ChromePicker color={this.state.color}
                    onChangeComplete={this.handleChangeComplete} />
                </div> : null}</button>
            </div>
            <div class="column">
              <button className="button" id="btn2" type="button" onClick={this.changeThree}>Visualisation 3<br></br>
                <button id="picker" onClick={this.handleClick1}>Change Colour</button>
                {this.state.displayColorPicker2 ? <div style={popover}>
                  <div style={cover} onClick={this.handleClose1} />
                  <ChromePicker color1={this.state.color1}
                    onChangeComplete={this.handleChangeComplete1} />
                </div> : null}</button>
            </div>
          </div>
        </div>

      </div>
    );
  }
}

