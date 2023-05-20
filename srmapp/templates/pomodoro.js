
var timer;
var defaultTime = 20 * 60;
var frameData;
var videoElement;

function startTimer(duration) {
  var timerDisplay = document.getElementById("timer");

  var timerMinutes, timerSeconds;
  timer = setInterval(function() {
    timerMinutes = parseInt(duration / 60, 10);
    timerSeconds = parseInt(duration % 60, 10);

    timerMinutes = timerMinutes < 10 ? "0" + timerMinutes : timerMinutes;
    timerSeconds = timerSeconds < 10 ? "0" + timerSeconds : timerSeconds;

    timerDisplay.textContent = timerMinutes + ":" + timerSeconds;

    if (--duration < 0) {
      clearInterval(timer);
      alert("Timer has ended!");
    }
  }, 1000);
}

function resetTimer() {
  clearInterval(timer);
  startTimer(defaultTime);
}

function pauseTimer() {
  clearInterval(timer);
  isTimerRunning = false;
}

function playTimer() {
  if (!isTimerRunning) {
    startTimer(currentTime);
    isTimerRunning = true;
  }
}

function changeDefaultTime() {
  var newDefaultTime = prompt("Enter the new default time in minutes:");

  // Validate the user input
  if (newDefaultTime !== null && !isNaN(newDefaultTime) && newDefaultTime !== "") {
    defaultTime = parseInt(newDefaultTime, 10) * 60;
    resetTimer();
  }
}

function showAlertPopup(alert) {
  var popup = document.createElement("div");
  popup.className = "popup";
  popup.textContent = alert;

  document.body.appendChild(popup);

  // Remove the popup after a certain time (e.g., 5 seconds)
  setTimeout(function() {
    document.body.removeChild(popup);
  }, 5000);
}

function checkDrowsinessAlerts() {
  fetch("http://localhost:8000/detect_drowsiness/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Requested-With": "XMLHttpRequest" // Add this header to allow cross-origin requests
    },
    body: JSON.stringify({
      frame_data: frameData, // Replace 'frameData' with your actual frame data
    }),
  })
    .then(function(response) {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error("Error: " + response.status);
      }
    })
    .then(function(data) {
      // Process the detection result received in 'data'
      var isDrowsy = true;
      //data.is_drowsy;
      if (isDrowsy) {
        // Show drowsiness alert
        showAlertPopup("Drowsiness Alert: It seems you are sleepy.. Wake up!");
      }
    })
    .catch(function(error) {
      // Handle any errors
      console.error("Error:", error);
    });
}

function captureAndSendFrame() {
  const canvas = document.createElement("canvas");
  canvas.width = videoElement.videoWidth;
  canvas.height = videoElement.videoHeight;
  canvas.getContext("2d").drawImage(videoElement, 0, 0, canvas.width, canvas.height);
  const frameDataUrl = canvas.toDataURL("image/jpeg");

  const frameData = {
    frame_data: frameDataUrl,
  };

  fetch("http://localhost:8000/detect_drowsiness/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(frameData),
  })
    .then(function(response) {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error("Error: " + response.status);
      }
    })
    .then(function(data) {
      console.log(data);
    })
    .catch(function(error) {
      console.error("Error sending frame to the server:", error);
    });
}

document.addEventListener("DOMContentLoaded", function() {
  // Access the video element
  videoElement = document.getElementById("videoElement");

  // Check if the browser supports accessing the camera
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    // Access the camera and stream video
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then(function(stream) {
        // Set the video source to the stream
        videoElement.srcObject = stream;
      })
      .catch(function(error) {
        console.error("Error accessing the camera:", error);
      });
  } else {
    console.error("getUserMedia is not supported in this browser");
  }

  // Add click event listener to the start button
  //const startButton = document.getElementById("startButton");
  //startButton.addEventListener("click", function() {
    // Capture video frame and send to the server
    //captureAndSendFrame();
  //});

  // Start capturing and sending frames
  setInterval(captureAndSendFrame, 10000); // Adjust the interval as needed (e.g., every 500 milliseconds)

  // Check drowsiness alerts
  setInterval(checkDrowsinessAlerts, 20000);

  // Start the timer
  startTimer(defaultTime);
});
