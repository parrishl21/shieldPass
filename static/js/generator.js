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