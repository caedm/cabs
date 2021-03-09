function filter() {
    let trs = document.getElementsByClassName("filterable");
    filterString = document.getElementById("filter").value;
    for (let i = 0; i < trs.length; i++) {
        let matches = false;
        for (let j = 0; j < trs[i].children.length; j++) {
            if (trs[i].children[j].textContent.toLowerCase().includes(filterString.toLowerCase())) {
                matches = true;
            }
        }
        if (!matches) {
            trs[i].classList.add("hidden");
        } else {
            trs[i].classList.remove("hidden");
        }
    }
}

document.getElementById("filterbutton").onclick = filter;
