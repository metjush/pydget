function showItems() {
    categorySelect = document.getElementById('category');
    selectedCategory = categorySelect.value;
    itemId = 'item-' + selectedCategory;
    // itemSelect = document.getElementById(itemId);
    allItemSelects = document.getElementsByClassName('item');
    for (var i = 0; i < allItemSelects.length; i++) {
        if (allItemSelects[i].id == itemId) {
            // keep this open
            allItemSelects[i].disabled = false;
        } else {
            // hide it
            allItemSelects[i].disabled = true;
        }
    }
}

$(document).ready(function(){
    $(".button-collapse").sideNav();
});