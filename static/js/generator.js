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
    let lowerArray = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"];
    let uppercaseArray = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"];
    let numberArray = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"];
    let symbolArray = ["!", "@", "#", "$", "%", "^", "&", "*", "-", "_", "=", "+", ".", "?", "/"];

    let upperStart = 0;
    let numberStart = 0;
    let symbolStart = 0;

    let upperCount = 0;
    let numberCount = 0;
    let symbolCount = 0;

    let includeUpper = document.getElementById("generator-uppercase").checked;
    let includeNumber = document.getElementById("generator-numbers").checked;
    let includeSymbol = document.getElementById("generator-symbols").checked;

    if (includeUpper) {
        upperStart = masterArray.length;
        masterArray.push(...uppercaseArray);
    }

    if (includeNumber) {
        numberStart = masterArray.length;
        masterArray.push(...numberArray);
    }

    if (includeSymbol) {
        symbolStart = masterArray.length;
        masterArray.push(...symbolArray);
    }

    let length = parseInt(document.getElementById("generator-length").value, 10);
    let pwd = [];
    for (let i = 0; i < length; i++) {
        r = Math.floor(Math.random() * masterArray.length);
        pwd.push(masterArray[r]);

        if (includeSymbol && r >= symbolStart)
            symbolCount++;

        else if (includeNumber && r >= numberStart)
            numberCount++;

        else if (includeUpper && r >= upperStart)
            upperCount++;
    }

    if ((includeUpper && upperCount < 2) || (includeNumber && numberCount < 2) || (includeSymbol && symbolCount < 2)) {

        for (let i = length - 1; i >= 0; i--) {

            if (includeUpper && upperCount < 2 && lowerArray.includes(pwd[i])) {
                r = Math.floor(Math.random() * uppercaseArray.length);
                pwd[i] = uppercaseArray[r];
                upperCount++;
            }

            else if (includeNumber && numberCount < 2 && lowerArray.includes(pwd[i])) {
                r = Math.floor(Math.random() * numberArray.length);
                pwd[i] = numberArray[r];
                numberCount++;
            }

            else if (includeSymbol && symbolCount < 2 && lowerArray.includes(pwd[i])) {
                r = Math.floor(Math.random() * symbolArray.length);
                pwd[i] = symbolArray[r];
                symbolCount++;
            }
        }
    }

    document.getElementById("generator-output").value = pwd.join("");
}