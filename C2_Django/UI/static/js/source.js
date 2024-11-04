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
}3