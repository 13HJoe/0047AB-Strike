function gethistory(){
    let ip = document.getElementById('ip').innerHTML
    fetch(`http://127.0.0.1:8000/exec_hist?ip=${ip}`)
    .then(response =>{
        return response.text();
    })
    .then(data => {
        for(i=0; i<data.length(); i++){
            
        }
        document.querySelector('.resp').innerHTML = data;
    })
}
function submitCommand(event, ip) {
    event.preventDefault();
    const form = event.target;
    const command = form.querySelector('input[name="command"]').value;

    fetch(form.action, {
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
