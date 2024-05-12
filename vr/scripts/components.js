scene = document.getElementById("scene");
velText = document.getElementById("velocity_text");
stateText = document.getElementById("state_text");
oriText = document.getElementById("orientation_text");

let regex = /\[(.*?)\]/;

currentElement = undefined;

const url = "mqtt://127.0.0.1:9001"

const client = mqtt.connect(url);

client.on('connect', function () { console.log("Connected to MQTT broker")})


AFRAME.registerComponent("clicable", {
  init: function () {
    let el = this.el;

    this.onRaycastHit = (evt) => {
      currentElement = el;
    };

    this.onRaycastClear = (evt) => {
      currentElement = undefined;
    };

    this.el.addEventListener("raycaster-intersected", this.onRaycastHit);
    this.el.addEventListener(
      "raycaster-intersected-cleared",
      this.onRaycastClear
    );
  },

  remove: function () {
    this.el.removeEventListener("raycaster-intersected", this.onRaycastHit);
    this.el.removeEventListener(
      "raycaster-intersected-cleared",
      this.onRaycastClear
    );
  },
});

AFRAME.registerComponent('denso_controller',{
  init: function () {
    this.el.addEventListener("triggerdown", onTriggerDown);
  }
});


AFRAME.registerComponent('thumbstick-logging-right',{
  init: function () {
    this.el.addEventListener('thumbstickmoved', this.logThumbstick);
  },
  
  logThumbstick: function (evt) {
      let deltaTheta = evt.detail.x/20.0;
      player.rotation.y -= deltaTheta;
    }
  });