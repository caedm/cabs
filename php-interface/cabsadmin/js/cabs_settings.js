let setting = document.getElementById('setting');

function showChosen() {
    let settingForms = document.getElementsByClassName('settingForms');
    for (i = 0; i < settingForms.length; i++) {
        settingForms[i].classList.add('hidden');
        if (setting.value === settingForms[i].children[0].children[0].textContent) {
            settingForms[i].classList.remove('hidden');
        }
    }
}

setting.addEventListener('change', function() {
    showChosen();
})

showChosen();
