function gethistory(ip){
    fetch(`http://127.0.0.1:8000/exec_hist?ip=${ip}`)
    .then(response =>{
        return response.json();
    })
    .then(data => {
        obj = data;
        data = '<p>';

        for (const [key,value] of Object.entries(obj)) {
            data += `<strong>Timestamp:</strong>${key}<br>`;
            data += `<strong>Command:</strong><br>${value.command}<br>`;
            data += `<strong>Response:</strong><br>${value.response}<br>`;
            data += '--------------------------------------------------------------------------------------<br>';
        }
        document.getElementById(`response-${ip}`).innerHTML = `${data}</p>`;
    })
}
function submitCommand(event, ip) {
    event.preventDefault();
    const form = event.target;
    const command = form.querySelector('input[name="command"]').value;

  if(command != "history-c2"){
    fetch(`http://127.0.0.1:8000/exec_conn/${ip}`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': form.querySelector('input[name="csrfmiddlewaretoken"]').value,
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams(new FormData(form))
    })
    .then(response => response.text())
    .then(data => {
      // Display the response in the designated div below the input field
      document.getElementById(`response-${ip}`).innerHTML = `<p>${data}</p>`;
    })
    .catch(error => console.error('Error:', error));
  }
  else{
    gethistory(ip);
  }
}

