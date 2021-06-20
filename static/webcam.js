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

function capture() {
  context.drawImage(video, 0, 0, 320, 240);
}
