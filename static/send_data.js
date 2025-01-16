// Send data to backedn using POST request
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
