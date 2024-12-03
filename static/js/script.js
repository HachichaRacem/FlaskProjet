document
  .getElementById("appointment-form")
  .addEventListener("submit", function (event) {
    const name = document.getElementById("name").value;
    const time = document.getElementById("time").value;
    const date = document.getElementById("time").value;
    document.getElementById("date").value;
    if (!name || date || !time) {
      alert("Veuillez remplir tous les champs.");
      event.preventDefault();
    }
  });
