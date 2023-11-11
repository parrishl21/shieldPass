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