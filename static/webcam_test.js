"use strict";

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
var context = canvas.getContext("2d");

const constraints = {
  audio: false,
  video: {
    width: 320,
    height: 240,
  },
};

// Access webcam
async function start() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    window.stream = stream;
    video.srcObject = stream;
  } catch (e) {
    alert("Webcam error");
    console.log(e);
  }
}

// Stop webcam
async function stop() {
  try {
    window.stream.getTracks().forEach(function (track) {
      if (track.readyState == "live") {
        track.stop();
      }
    });
    context.clearRect(0, 0, canvas.width, canvas.height);
  } catch (e) {
    alert("Webcam error");
    console.log(e);
  }
}

// capture image
function capture() {
  context.drawImage(video, 0, 0, 320, 240);
}

function dataURLtoBlob(dataURL) {
  let array, binary, i, len;
  binary = atob(dataURL.split(",")[1]);
  array = [];
  i = 0;
  len = binary.length;
  while (i < len) {
    array.push(binary.charCodeAt(i));
    i++;
  }
  return new Blob([new Uint8Array(array)], {
    type: "image/png",
  });
}

// send image
function send() {
  var myFormData = new FormData();
  myFormData.append("img", dataURLtoBlob(canvas.toDataURL()));
  myFormData.append("uname", uname);

  $.ajax({
    url: "/api/webcam_test",
    type: "POST",
    processData: false, // important
    contentType: false, // important
    dataType: "json",
    data: myFormData,
  }) // The response is passed to the function
    .done(function (json) {
      console.log("ack");
      if (json.error) {
        alert(json.message);
        window.location = json.redirect;
      }
      if (json.warn) {
        alert(
          `You have ${json.warnings}/5 warnings. You will be logged out after 5 warnings`
        );
      }
      if (json.warnings >= 5) {
        alert("Warnings exceeded. We are logging you out");
        window.location = `/api/logout/${uname}`;
      }
    });
}

$(function () {
  start(); // start on page load
  setInterval(function () {
    capture();
    send();
  }, 5000);
});
