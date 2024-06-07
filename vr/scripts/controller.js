j0Text = document.getElementById("text_j0");
j1Text = document.getElementById("text_j1");
j2Text = document.getElementById("text_j2");
j3Text = document.getElementById("text_j3");
j4Text = document.getElementById("text_j4");
j5Text = document.getElementById("text_j5");

stateText = document.getElementById("stateText")

j0Object = document.getElementById("#J0");
j1Object = document.getElementById("#J1");
j2Object = document.getElementById("#J2");
j3Object = document.getElementById("#J3");
j4Object = document.getElementById("#J4");
j5Object = document.getElementById("#J5");


jointsPosition = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
toolsValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

// Joint Control = 0
// Tool Control = 1
state = 0

const url = "mqtt://127.0.0.1:9001"

const client = mqtt.connect(url);

client.on('connect', function () { 
  console.log("Connected to MQTT broker")

  client.subscribe("denso01/joint_states", (err) => {
    if (!err) {
      console.log("Subscribed to denso01/joint_states")
    }
  });
  }
)

client.on('message', function (topic, message) {
  // console.log(topic, message)
  const stringMsg = message.toString();
  const arrayMsg = stringMsg.split(',').map(Number);

  const fomartedArrayMsg = arrayMsg.map(num => {
    // Limitar rotação no if
    if (!isNaN(num)) {
      return (parseFloat(num) * 180/Math.PI).toFixed(2);
    } else {
      return num;
    }
  });
  jointsPosition = fomartedArrayMsg
  updateJoints(fomartedArrayMsg)
  updateHUD(state)
})

function onTriggerDown(e){
  if (currentElement != undefined){
    switch (currentElement.id){
      case "jointModeButton":
        if(state != 0){ 
          state = 0
          changeText(stateText, `Current Mode[Joint Control]`);
          updateHUD(state)
        }
        break;

      case "toolModeButton":
        if(state != 1){
          state = 1
          changeText(stateText, `Current Mode[Tool Control]`);
          updateHUD(state)
        }
        break;

      case "increase_j0":
        if(state == 0){
          jointsPosition[0] += 10
          const new_positions = jointsPosition.map(function(element) {return element.toFixed(1);}).join(" ");
          client.publish('denso/target_positions', new_positions);
        }
        else if(state == 1){
          calculateNewPositions()
          client.publish('denso/target_positions', `${new_position}`);
        }
        break;

      case "decrease_j0":
        if(state == 0){
          jointsPosition[0] -= 10
          const new_positions = jointsPosition.map(function(element) {return element.toFixed(1);}).join(" ");
          client.publish('denso/target_positions', new_positions);
        }
        else if(state == 1){
          calculateNewPositions()
          client.publish('denso/target_positions', `${new_position}`);
        }
        break;

    }
  }
}

// Apply rotation into A-frame
function updateJoints(jointsPosition){
  // console.log(jointsPosition)
  changeRotation(j0Object, {x:0, y:jointsPosition[0], z:0})
  changeRotation(j1Object, {x:0, y:0, z:jointsPosition[1]})
  changeRotation(j2Object, {x:0, y:0, z:jointsPosition[2]})
  changeRotation(j3Object, {x:jointsPosition[3], y:0, z:0})
  changeRotation(j4Object, {x:0, y:0, z:jointsPosition[4]})
  changeRotation(j5Object, {x:jointsPosition[5], y:0, z:0})
}

// Changes HUD information according to mode
function updateHUD(state){
  switch(state){
    case 0:
      changeText(j0Text, `J0[${jointsPosition[0]}]`);
      changeText(j1Text, `J1[${jointsPosition[1]}]`);
      changeText(j2Text, `J2[${jointsPosition[2]}]`);
      changeText(j3Text, `J3[${jointsPosition[3]}]`);
      changeText(j4Text, `J4[${jointsPosition[4]}]`);
      changeText(j5Text, `J5[${jointsPosition[5]}]`);
      break;

    case 1:
      changeText(j0Text, `X[${toolsValues[0]}]`);
      changeText(j1Text, `Y[${toolsValues[1]}]`);
      changeText(j2Text, `Z[${toolsValues[2]}]`);
      changeText(j3Text, `Roll[${toolsValues[3]}]`);
      changeText(j4Text, `Pitch[${toolsValues[4]}]`);
      changeText(j5Text, `Yaw[${toolsValues[5]}]`);
      break;
  }
}

function calculateNewPositions(axis, step){
  
}