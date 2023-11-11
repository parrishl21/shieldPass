var buttonClicked = false;
let currentRowId;
let currentSelectedButtonName = 'A-Z';

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
function changeColor(buttonName) {
    currentSelectedButtonName = buttonName;
    var buttons = document.getElementsByClassName('filter-show-buttons');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].style.color = 'white'; // Change all text colors to white
    }
    var selectedButton = document.querySelector('button[onclick="changeColor(\'' + buttonName + '\')"]');
    selectedButton.style.color = '#0DBC62'; // Change the text color of the clicked button to green
    
    // Implement specific actions for each button here
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
    }
}
function updateTable(data) {
    var table = document.querySelector('table');
    
    table.innerHTML = '';
    
    // Add new rows based on the updated data
    for (var i = 0; i < data.length; i++) {
        var row = table.insertRow(-1); // Insert at the end of the table
        var cell1 = row.insertCell(0);
        var cell2 = row.insertCell(1);
        cell1.innerHTML = '<img class="logo-img" src="https://logo.clearbit.com/' + data[i][1] + '.com?size=45" alt="No Logo">';
        cell1.classList.add('left-column');
        cell2.innerHTML = data[i][1];
        cell2.classList.add('right-column');
        row.setAttribute('onclick', 'fetchLoginInfo(' + data[i][0] + ')');
    }
}
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
function closeModalConform() {
    event.preventDefault();
    document.getElementById("modal-confirm").style.display = "none";
}
function closeModalView() {
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
function saveChanges() {
    event.preventDefault();

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
function showCloneIcons() {
    var copyButtons = document.querySelectorAll('.copy-button');
    copyButtons.forEach(function(button) {
        button.style.display = 'inline-block';
    });
}
function makeReadOnly() {
    var inputFields = document.querySelectorAll('.new-password-input');
    inputFields.forEach(function(input) {
        input.readOnly = true;
    });
}
function deleteEntry() {
    event.preventDefault();

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
function searchDatabase() {
    var inputText = document.getElementById('searchInput').value;
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
function replaceWithErrorImage(image) {
    image.onerror = null; // to avoid infinite loops in case the replacement image is also missing
    image.src = "https://placehold.co/45/EEE/31343C?font=raleway&text=No-Image-Found"; // Replace with the URL of your placeholder image
}