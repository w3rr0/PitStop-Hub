function postToUrl(url, params) {
  var form = document.createElement("form");
  form.method = "POST";
  form.action = url;

  for (var key in params) {
    if (params.hasOwnProperty(key)) {
      var hiddenField = document.createElement("input");
      hiddenField.type = "hidden";
      hiddenField.name = key;
      hiddenField.value = params[key];

      form.appendChild(hiddenField);
    }
  }

  document.body.appendChild(form);
  form.submit();
}

// Change theme based on the switch
const toggleSwitch = document.getElementById("toggle-switch");
const statusText = document.getElementById("status");

toggleSwitch.addEventListener("change", () => {
  const mode = toggleSwitch.checked ? "Dark" : "Light";
  statusText.textContent = mode;

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
