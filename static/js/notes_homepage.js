let currentRowId;

function fetchNoteInfo(row_id) {
    currentRowId = row_id;

    fetch(`/get_note_info/${row_id}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    // Display the fetched data in the modal
                    document.getElementById("note-name-view").value = data.note_name;
                    document.getElementById("note-view").value = data.note;
                    openViewModal();
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
}
function openViewModal() {
    document.getElementById("myModal_view").style.display = "block";
}
function closeModalView() {
    document.getElementById("myModal_view").style.display = "none";
    document.getElementById("note-name-view").value = "";
    document.getElementById("note-view").value = "";
    document.querySelector('.save-button').style.display = 'none';
    document.querySelector('.edit-button').style.display = 'inline-block';
    document.querySelector('.delete-button').style.display = 'none';
    var inputs_i = document.getElementById('invalid_inputs_view');
    inputs_i.style.display = 'none';
    textInput = document.querySelectorAll('.note-name-text');
    textInput.forEach(function(input) {
        input.style.display = 'none';
    });
    document.querySelector('.note-name-input').style.display = 'none';
    makeReadOnly();
    location.reload();
}
function searchDatabase() {
    var inputText = document.getElementById('searchInput').value;
    fetch('/search_notes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: inputText })
    })
    .then(response => response.json())
    .then(data => {
        updateNote(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
function makeEditable() {
    event.preventDefault();

    // Make all input fields editable
    var inputFields = document.querySelectorAll('.note-name-input');
    var inputFieldsLong = document.querySelectorAll('.note-name-input-long');
    inputFields.forEach(function(input) {
        input.readOnly = false;
    });
    inputFieldsLong.forEach(function(input) {
        input.readOnly = false;
    });

    textInput = document.querySelectorAll('.note-name-text');
    textInput.forEach(function(input) {
        input.style.display = 'inline-block';
    });
    document.querySelector('.note-name-input').style.display = 'inline-block';

    // Hide the edit button and display the save button
    document.querySelector('.edit-button').style.display = 'none';
    document.querySelector('.save-button').style.display = 'inline-block';
    // Display the delete button
    document.querySelector('.delete-button').style.display = 'inline-block';
}
function saveChanges() {
    event.preventDefault();

    let nid = currentRowId;
    var note_name = document.getElementById('note-name-view').value;
    var note = document.getElementById('note-view').value;

    // Prepare the data payload to be sent to the Flask backend
    var data = {
        nid: nid,
        note_name: note_name,
        note: note
    };

    // Send the data to the Flask backend
    fetch('/save_changes_notes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Data saved:', data);
        // showCloneIcons();
        makeReadOnly();
    })
    .catch((error) => {
        console.error('Error:', error);
    });

    textInput = document.querySelectorAll('.note-name-text');
    textInput.forEach(function(input) {
        input.style.display = 'none';
    });
    document.querySelector('.note-name-input').style.display = 'none';
    document.querySelector('.save-button').style.display = 'none';
    document.querySelector('.edit-button').style.display = 'inline-block';

    document.querySelector('.delete-button').style.display = 'none';
}
function makeReadOnly() {
    var inputFields = document.querySelectorAll('.note-name-input');
    var inputFieldsLong = document.querySelectorAll('.note-name-input-long');
    inputFields.forEach(function(input) {
        input.readOnly = true;
    });
    inputFieldsLong.forEach(function(input) {
        input.readOnly = true;
    });
}
function openConfirmModal() {
    event.preventDefault();
    document.getElementById("modal-confirm").style.display = "block";
}
function deleteEntry() {
    event.preventDefault();

    var data = {
        row_id: currentRowId
    };
    fetch('/delete_row_note', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        closeModalView();
        location.reload();
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
function closeModalConform() {
    event.preventDefault();
    document.getElementById("modal-confirm").style.display = "none";
}
function openModal() {
    document.getElementById("myModal").style.display = "block";
}
function closeModal() {
    var inputs_i = document.getElementById('invalid_inputs');
    inputs_i.style.display = 'none';
    document.getElementById("myModal").style.display = "none";
    document.getElementById("note-name-add").value = "";
    document.getElementById("note-add").value = "";
}
function checkInputs() {
    event.preventDefault();
    var inputs_i = document.getElementById('invalid_inputs');
    inputs_i.style.display = 'none';

    var input1 = document.getElementById("note-name-add").value;
    var input2 = document.getElementById("note-add").value;
    
    if (input1 && input2) {
        document.getElementById("noteForm").submit();
    } else {
        inputs_i.style.display = 'block';
    }
}
function checkInputsSave() {
    event.preventDefault();
    var inputs_i = document.getElementById('invalid_inputs_view');
    inputs_i.style.display = 'none';

    var input1 = document.getElementById("note-name-view").value;
    var input2 = document.getElementById("note-view").value;
    
    if (input1 && input2) {
        saveChanges();
    } else {
        inputs_i.style.display = 'block';
    }
}
function updateNote(data) {
    var noteContainer = document.querySelector('.notes-container');
    noteContainer.innerHTML = '';

    for (var i = 0; i < data.length; i++) {
        var noteId = data[i][0];
        var noteName = data[i][1];

        // Create the HTML elements for each note
        var noteBox = document.createElement('div');
        noteBox.className = 'note-box';
        noteBox.setAttribute('onclick', 'fetchNoteInfo(' + noteId + ')');

        var boxLeftRectangle = document.createElement('div');
        boxLeftRectangle.className = 'box-left-rectangle';

        var noteNameParagraph = document.createElement('p');
        noteNameParagraph.className = 'note-name note-name-' + noteId;
        noteNameParagraph.innerHTML = noteName;

        // Append the elements to the noteBox
        noteBox.appendChild(boxLeftRectangle);
        noteBox.appendChild(noteNameParagraph);

        // Append the noteBox to the notesContainer
        noteContainer.appendChild(noteBox);
    }
}
