// Change theme based on the switch
const toggleSwitch = document.getElementById("toggle-switch");
const statusText = document.getElementById("status");

toggleSwitch.addEventListener("change", () => {
  const mode = toggleSwitch.checked ? "Dark" : "Light";
  statusText.textContent = mode;

  // Change the theme
  if (mode === "Dark") {
    document.body.style.backgroundImage = "url('/static/background_night.jpg')";
    // document.body.style.color = "#fff";
    // powyżej zmiana tekstu na biały
  } else {
    document.body.style.backgroundImage = "url('/static/background.jpg')";
    document.body.style.color = "#000";
  }

  // Send the mode to the server
  fetch("/change-theme", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ mode: mode }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Theme changed:", data);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
});
