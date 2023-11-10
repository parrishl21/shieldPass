function copyText(inputId) {
    event.preventDefault();
    var inputElement = document.getElementById(inputId);
    inputElement.select();
    inputElement.setSelectionRange(0, 99999); // For mobile devices 
    document.execCommand("copy");
    
    var originalHtml = document.getElementById(inputId).nextElementSibling.innerHTML;
    document.getElementById(inputId).nextElementSibling.innerHTML = '<i class="fas fa-clipboard-check" style="color: #4CAF50; font-size: 30px;"></i>'; // Change to clipboard with check

    setTimeout(function() {
        document.getElementById(inputId).nextElementSibling.innerHTML = originalHtml; // Revert back to clone
    }, 1000); // Revert after 1 second(s)
}

function updateLength() {
    let slider = document.getElementById("generator-length");
    let length = slider.value;
    var value = (slider.value - slider.min) / (slider.max - slider.min) * 100;
    slider.style.background = 'linear-gradient(to right, #0DBC62 0%, #0DBC62 ' + value + '%, white ' + value + '%, white 100%)';
    let str = 'Password Length: <b>' + length + '</b>';
    document.getElementById("generator-length-text").innerHTML = str;
    generatePassword();

}

function generatePassword() {
    event.preventDefault();
    let masterArray = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"];
    let uppercaseArray = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"];
    let numbersArray = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"];
    let symbolsArray = ["!", "@", "#", "$", "%", "^", "&", "*", "-", "_", "=", "+", ".", "?", "/"];

    if (document.getElementById("generator-uppercase").checked) {
        masterArray.push(...uppercaseArray);
    }

    if (document.getElementById("generator-numbers").checked) {
        masterArray.push(...numbersArray);
    }

    if (document.getElementById("generator-symbols").checked) {
        masterArray.push(...symbolsArray);
    }
    let length = parseInt(document.getElementById("generator-length").value, 10);
    let pwd = [];
    for (let i = 0; i < length; i++) {
        r = Math.floor(Math.random() * masterArray.length);
        pwd.push(masterArray[r]);
    }

    document.getElementById("generator-output").value = pwd.join("");
}