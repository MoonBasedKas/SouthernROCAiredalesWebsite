function setLoginForm(action) {
    let form = document.getElementById("windowControl")
    let slide = document.getElementById("window")

    if (action === 'inc') {
        slide.value = "inc"
    } else if (action === 'dec') {
        slide.value = "dec"
    } else {
        slide.value = "none"
    }

    form.submit()
}