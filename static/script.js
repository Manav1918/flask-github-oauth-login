function toggleProfileMenu() {
    document.getElementById("profile-menu").classList.toggle("show");
}
function addToCart(item) {
    const alertBox = document.createElement("div");
    alertBox.textContent = item + " has been added to your cart!";
    alertBox.style.position = "fixed";
    alertBox.style.bottom = "20px";
    alertBox.style.right = "20px";
    alertBox.style.backgroundColor = "#4CAF50";
    alertBox.style.color = "white";
    alertBox.style.padding = "10px";
    alertBox.style.borderRadius = "5px";
    alertBox.style.opacity = "1";
    alertBox.style.transition = "opacity 0.5s ease-out";
    document.body.appendChild(alertBox);

    setTimeout(() => {
        alertBox.style.opacity = "0";
        setTimeout(() => {
            document.body.removeChild(alertBox);
        }, 500);
    }, 2000);
}
function removeFromCart(item) {
    alert(item + " has been removed from your cart!");
}
