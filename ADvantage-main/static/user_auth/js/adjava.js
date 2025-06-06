

function updateFileName() {
    var fileInput = document.getElementById("fileInput");
    var fileName = fileInput.files.length > 0 ? fileInput.files[0].name : 'No file chosen';
    document.getElementById("fileName").textContent = fileName;
}