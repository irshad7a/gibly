

document.addEventListener('DOMContentLoaded', function() {

    function greet() {
        console.log('Hello! This is a basic JS utility.');
    }

    // Call greet function
    greet();

    // function to toggle visibility of an element by id
    function toggleVisibility(id) {
        var elem = document.getElementById(id);
        if (elem) {
            if (elem.style.display === 'none') {
                elem.style.display = 'block';
            } else {
                elem.style.display = 'none';
            }
        }
    }

    // Example usage: toggle visibility of element with id 'example' on button click
    var toggleBtn = document.getElementById('toggleExampleBtn');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            toggleVisibility('example');
        });
    }
});
