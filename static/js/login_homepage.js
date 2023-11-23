var buttonClicked = false;
let currentRowId;
let currentSelectedButtonName = 'A-Z';
let saveCheck = false;

// Function to show and hide or show buttons
function showButtons() {
    var slideOutButtons = document.getElementById("filter-slide-out-buttons");
    if (!buttonClicked) {
        slideOutButtons.style.display = "block";
        buttonClicked = true;
    } else {
        slideOutButtons.style.display = "none";
        buttonClicked = false;
    }
}

// Event listener to listen for a button to be clicked
document.addEventListener("DOMContentLoaded", function() {
    // Sets the initial color based on the selected button (assuming currentSelectedButtonName is already defined)
    var initialSelectedButton = document.querySelector('.filter-show-buttons[onclick="changeColor(\'' + currentSelectedButtonName + '\')"]');
    if (initialSelectedButton) {
        initialSelectedButton.classList.add('selected');
    }
});

// Function that changes the color of the filter buttons
function changeColor(buttonName) {
    clearSearch();
    currentSelectedButtonName = buttonName;

    // Remove the 'selected' class from all buttons
    var buttons = document.getElementsByClassName('filter-show-buttons');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].classList.remove('selected');
    }

    // Add the 'selected' class to the currently clicked button
    var selectedButton = document.querySelector('.filter-show-buttons[onclick="changeColor(\'' + buttonName + '\')"]');
    selectedButton.classList.add('selected');
    
    // Does a get depending on which button was clicked
    if (buttonName === 'A-Z') {
        fetch('/login_homepage?buttonName=A-Z', {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            updateTable(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
        console.log('A-Z button clicked');
    } else if (buttonName === 'Z-A') {
        fetch('/login_homepage?buttonName=Z-A', {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            updateTable(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
        console.log('Z-A button clicked');
    } else if (buttonName === 'Oldest') {
        fetch('/login_homepage?buttonName=Oldest', {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            updateTable(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
        console.log('Oldest button clicked');
    } else if (buttonName === 'Newest') {
        fetch('/login_homepage?buttonName=Newest', {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            updateTable(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
        console.log('Newest button clicked');
    } else if (buttonName === 'Popular') {
        fetch('/login_homepage?buttonName=Popular', {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            updateTable(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    } else if (buttonName === 'Weakest') {
        fetch('/login_homepage?buttonName=Weakest', {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            updateTable(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}

// Function that updates the table depending on the data from the GET in the changeColor function
function updateTable(data) {
    var table = document.querySelector('table');
    table.innerHTML = '<caption style="text-align:right; margin-right: 51px;">Password Strength</caption>';

    // Add new rows based on the updated data
    for (var i = 0; i < data.length; i++) {
        var row = table.insertRow(-1); // Insert at the end of the table
        row.setAttribute('onclick', 'fetchLoginInfo(' + data[i][0] + ')');

        createCell(row, 'left-column', 'https://logo.clearbit.com/' + data[i][1] + '.com?size=45', true, data[i][0]);
        createCell(row, 'right-column', data[i][1], false);
        createCell(row, 'strength-column', data[i][2], false);
    }
}

// Function that creates a cell (div for the html) for the updateTable function
function createCell(row, className, content, isImage, row_id) {
    var cell = row.insertCell(-1);
    cell.classList.add(className);

    if (isImage) {
        var img = new Image();
        img.src = content;

        img.onerror = function () {
            cell.innerHTML = '<img class="logo-img" src="https://placehold.co/45/EEE/31343C?font=raleway&text=No-Image-Found" alt="No Logo">';
        };

        img.onload = function () {
            cell.innerHTML = '<img class="logo-img" src="' + content + '" alt="No Logo">';
        };
    } else if (className === 'strength-column') {
        var statusTextCell = row.insertCell(-1);
        statusTextCell.innerHTML = '<p class="status-text">' + getRectangleName(content) + '</p>';

        var rectangleContainer = document.createElement('div');
        rectangleContainer.className = 'rectangle-container';

        for (var j = 0; j < 3; j++) {
            var rectangle = document.createElement('div');
            rectangle.className = 'rectangle ' + getRectangleClass(content, j);
            rectangleContainer.appendChild(rectangle);
        }

        var rectangleCell = row.insertCell(-1);
        rectangleCell.appendChild(rectangleContainer);
    } else {
        cell.innerHTML = content;
    }
}

// Functions to open modals
function openConfirmModal() {
    event.preventDefault();
    document.getElementById("modal-confirm").style.display = "block";
}
function openViewModal() {
    document.getElementById("myModal_view").style.display = "block";
}
function openModal() {
    document.getElementById("myModal").style.display = "block";
}

// Functions to close modals
function closeModalView() {
    var passwordField = document.getElementById('new-password-view');
    makeReadOnly();
    showCloneIcons();
    document.getElementById("myModal_view").style.display = "none";
    document.getElementById("new-website-view").value = "";
    document.getElementById("new-email-view").value = "";
    document.getElementById("new-username-view").value = "";
    document.getElementById("new-password-view").value = "";
    document.querySelector('.save-button').style.display = 'none';
    document.querySelector('.edit-button').style.display = 'inline-block';
    document.querySelector('.delete-button').style.display = 'none';
    if (passwordField.type === 'text') {
        passwordField.type = 'password';
        showImg.style.display = 'inline';
        hideImg.style.display = 'none';
    }
    if (saveCheck) {
        saveCheck = false;
        changeColor(currentSelectedButtonName);
    }
}
function closeModal() {
    var email_i = document.getElementById('invalid_email');
    var inputs_i = document.getElementById('invalid_inputs');
    inputs_i.style.display = 'none';
    email_i.style.display = 'none';
    document.getElementById("myModal").style.display = "none";
    document.getElementById("new-website").value = "";
    document.getElementById("new-email").value = "";
    document.getElementById("new-username").value = "";
    document.getElementById("new-password").value = "";
}
function closeModalConform() {
    event.preventDefault();
    document.getElementById("modal-confirm").style.display = "none";
}

// Function to validate if an input is a valid email
function ValidateEmail() {
    event.preventDefault();
    var validRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    if ((document.getElementById('new-email')).value.match(validRegex)) {
        showEmailMessage(true);
        return true;
    
    } else {
        showEmailMessage(false);
        return false;
    }
}

// Function to show and hide a message depending on the input from ValidateEmail
function showEmailMessage(input) {
    var email_i = document.getElementById('invalid_email');
    var inputs_i = document.getElementById('invalid_inputs');
    
    inputs_i.style.display = 'none';
    email_i.style.display = 'none';
    
    if (input === true) {
        checkInputs();
    }
    else {
        email_i.style.display = 'block';
    }
}

// Function that checks if all the inputs are filled in
function checkInputs() {
    var inputs_i = document.getElementById('invalid_inputs');
    var input1 = document.getElementById("new-website").value;
    var input2 = document.getElementById("new-email").value;
    var input3 = document.getElementById("new-username").value;
    var input4 = document.getElementById("new-password").value;
    
    if (input1 && input2 && input3 && input4) {
        document.getElementById("loginForm").submit();
    } else {
        inputs_i.style.display = 'block';
    }
}

// Function that fetches log in information from the Database
function fetchLoginInfo(row_id) {
    currentRowId = row_id;

    // Perform an update call to increment a column by one
    fetch(`/update_row/${row_id}`, {
        method: 'PUT'
    })
    .then(response => response.json())
    .then(data => {
        // Continue with fetching the login info if the update is successful
        fetch(`/get_login_info/${row_id}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    // Display the fetched data in the modal
                    document.getElementById("new-website-view").value = data.website;
                    document.getElementById("new-email-view").value = data.email;
                    document.getElementById("new-username-view").value = data.username;
                    document.getElementById("new-password-view").value = data.password;
                    openViewModal();
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Function that copies text from an input
function copyText(inputId, iconId) {
    event.preventDefault();
    var inputElement = document.getElementById(inputId);

    // Create a temporary input element
    var tempInput = document.createElement("input");
    tempInput.style.position = "absolute";
    tempInput.style.left = "-9999px";
    document.body.appendChild(tempInput);

    // Set the temporary input value to the password value
    tempInput.setAttribute("value", inputElement.value);
    tempInput.select();
    document.execCommand("copy");

    // Clean up: remove the temporary input
    document.body.removeChild(tempInput);

    var iconElement = document.getElementById(iconId);
    iconElement.className = "fas fa-clipboard-check"; // Change the icon to indicate successful copy

    setTimeout(function () {
        iconElement.className = "far fa-clone"; // Revert back to the original icon
    }, 1000); // Revert after 1 second(s)

    // Focus on the original input field after a short delay
    setTimeout(function () {
        inputElement.focus();
        inputElement.select(); // Select the input field content
    }, 50); // Set focus after 50 milliseconds
}

// Function that makes an input editable
function makeEditable() {
    event.preventDefault();

    var copyButtons = document.querySelectorAll('.copy-button');
    copyButtons.forEach(function(button) {
        button.style.display = 'none';
    });

    // Make all input fields editable
    var inputFields = document.querySelectorAll('.new-password-input');
    inputFields.forEach(function(input) {
        input.readOnly = false;
    });

    // Hide the edit button and display the save button
    document.querySelector('.edit-button').style.display = 'none';
    document.querySelector('.save-button').style.display = 'inline-block';
    // Display the delete button
    document.querySelector('.delete-button').style.display = 'inline-block';
}

// Function that saves changes to the Databse
function saveChanges() {
    event.preventDefault();
    saveCheck = true;

    let lid = currentRowId;
    var website = document.getElementById('new-website-view').value;
    var email = document.getElementById('new-email-view').value;
    var username = document.getElementById('new-username-view').value;
    var password = document.getElementById('new-password-view').value;

    // Prepare the data payload to be sent to the Flask backend
    var data = {
        lid: lid,
        website: website,
        email: email,
        username: username,
        password: password
    };

    // Send the data to the Flask backend
    fetch('/save_changes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Data saved:', data);
        showCloneIcons();
        makeReadOnly();
    })
    .catch((error) => {
        console.error('Error:', error);
    });

    document.querySelector('.save-button').style.display = 'none';
    document.querySelector('.edit-button').style.display = 'inline-block';

    document.querySelector('.delete-button').style.display = 'none';
}

// Function that shows the clone icon
function showCloneIcons() {
    var copyButtons = document.querySelectorAll('.copy-button');
    copyButtons.forEach(function(button) {
        button.style.display = 'inline-block';
    });
}

// Function that makes an input read only
function makeReadOnly() {
    var inputFields = document.querySelectorAll('.new-password-input');
    inputFields.forEach(function(input) {
        input.readOnly = true;
    });
}

// Function that deletes an entry from the databse
function deleteEntry() {
    event.preventDefault();
    closeModalConform();

    var data = {
        row_id: currentRowId
    };
    fetch('/delete_row', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        closeModalView();
        changeColor(currentSelectedButtonName);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

// Function that searches the Database accroding to what is put in the search input
function searchDatabase() {
    clearFilterColors();
    var inputText = document.getElementById('searchInput').value;

    if (inputText.trim() === '') {
        changeColor('A-Z');
        return;
    }

    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: inputText })
    })
    .then(response => response.json())
    .then(data => {
        updateTable(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Function that clears the filter colors
function clearFilterColors() {
    var buttons = document.getElementsByClassName('filter-show-buttons');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].style.color = 'white';
    }
}

// Function that clears the search input
function clearSearch() {
    document.getElementById('searchInput').value = '';
}

// Function to replace error images with a default image
function replaceWithErrorImage(image) {
    image.onerror = null;
    image.src = "https://placehold.co/45/EEE/31343C?font=raleway&text=No-Image-Found";
}

// Function that sets the classes of the html rectangles for the strength
function getRectangleClass(strength, target_rectangle) {
    if (strength === 0) {
        return 'weak';
    } else if (strength === 1) {
        if (target_rectangle === 0) {
            return 'filled_okay';
        } else {
            return 'empty_okay';
        }
    } else if (strength === 2) {
        if (target_rectangle === 2) {
            return 'empty_great';
        } else {
            return 'filled_great';
        }
    } else {
        return 'excellent';
    }
}

// Function that changes the text of the html rectangles for the strength
function getRectangleName(strength) {
    if (strength === 0) {
        return 'Weak';
    } else if (strength === 1) {
        return 'Okay';
    } else if (strength === 2) {
        return 'Great';
    } else {
        return 'Excellent';
    }
}

// Function that toggles the visibility of a password
function togglePasswordVisibility() {
    var passwordField = document.getElementById('new-password-view');
    var showImg = document.getElementById('showImg');
    var hideImg = document.getElementById('hideImg');

    if (passwordField.type === 'password') {
      passwordField.type = 'text';
      showImg.style.display = 'none';
      hideImg.style.display = 'inline';
    } else {
      passwordField.type = 'password';
      showImg.style.display = 'inline';
      hideImg.style.display = 'none';
    }
}