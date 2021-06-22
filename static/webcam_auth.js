"use strict";

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
var context = canvas.getContext("2d");
var myFormData = new FormData();
var num = 0;

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

function capture_many() {
  let num = 0;
  setInterval(capture, 100);
}

// capture image
function capture() {
  if (num < 10) {
    console.log(num);
    context.drawImage(video, 0, 0, 320, 240);
    myFormData.append(`img-${num}`, dataURLtoBlob(canvas.toDataURL()));
    num = num + 1;
  }
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
  myFormData.append("uname", uname);

  $.ajax({
    url: "/api/webcam_auth",
    type: "POST",
    processData: false, // important
    contentType: false, // important
    dataType: "json",
    data: myFormData,
  }) // The response is passed to the function
    .done(function (json) {
      console.log(json);
      if (json.error) {
        alert(json.message);
      }
      window.location = json.redirect;
    })
    .fail(function (xhr, status, errorThrown) {
      alert("Sorry, there was a problem!");
    });
}

$(function () {
  start(); // start on page load
});
